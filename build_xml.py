#!/usr/bin/env python3

"""
Builds the various different BEAST2 configurations.

Note that, by decision, this script is building the `beastling`
configuration files, if necessary, and invoking `beastling` as a
tool. While it can be used as a library, we decided to do this way
to raise the transparency for reviewers.
"""

# Import Python standard libraries
from pathlib import Path
from collections import defaultdict
import argparse
import csv
import logging
import re
import subprocess
import unidecode


def read_nexus(nexus_map, nexus_path):
    """
    Read a NEXUS file as exported from EDICTOR.

    We use our own parser here, so as not have more dependencies, to better handle
    EDICTOR output, and to organize the beastling data.
    """

    section = None

    re_concept = re.compile(r"([^=]+)=(\d+)-(\d+);(.+)")
    re_vector = re.compile(r"([^01?-]+)\s+([01?-]+)")

    data = []
    with open(nexus_path) as nexus:
        concepts = []
        for line in nexus:
            # normalize line
            line = re.sub(r"\s+", " ", line.strip())

            # Get the current position
            if line.startswith("BEGIN CHARACTERS"):
                section = "characters"
            elif line.startswith("BEGIN DATA"):
                section = "data"
            elif line.startswith("MATRIX"):
                section = "matrix"
            elif section == "characters":
                match = re.match(re_concept, line)
                if match:
                    concept_id, start, end, gloss = match.groups()
                    concepts.append(
                        {
                            "concept_id": concept_id,
                            "gloss": gloss.strip()[1:-1],
                            "start": int(start),
                            "end": int(end),
                        }
                    )
            elif section == "matrix":
                match = re.match(re_vector, line)
                if match:
                    taxon, vector = match.groups()

                    # Manual excludes, while data is cleaned
                    if taxon == "Apiaká":
                        continue

                    for concept in concepts:
                        # Get subset of data vector
                        subset = vector[concept["start"] - 1 : concept["end"]]

                        # If it is unknown, make sure they are all unknowns
                        if "?" in subset:
                            if len(set(subset)) != 1:
                                logging.warning(
                                    "Partial unknown in %s/%s, %s",
                                    taxon,
                                    concept["gloss"],
                                    [subset],
                                )
                            value = "?"
                        else:
                            # Grab the index of all number 1s; note that, due to
                            # the partial cognates in the NEXUS file, we need to
                            # collect them as strings
                            value = "_".join(
                                [
                                    str(idx)
                                    for idx, value in enumerate(subset)
                                    if value == "1"
                                ]
                            )

                        if not value:
                            logging.warning(
                                "Missing informaiton for %s/%s", taxon, concept["gloss"]
                            )
                        else:
                            data.append(
                                {
                                    "Language_ID": nexus_map[taxon],
                                    "Feature_ID": concept["gloss"],
                                    "Value": value,
                                }
                            )

    return data


def read_cldf(cldf_path):
    """
    Read CLDF data and return a trimmed down version with beastling requirements.

    While `beastling` can use CLDF data directly, this function allows to generate a
    custom CSV file that will fix issues with the released data being incompatible
    with what `beastling` expects, and also scaffold the project so later we can
    move away from `beastling` if necessary.

    Note that this function is reading the files directly, as CSVs, so that we can
    more easily deal with the incompatibilities between the current versions of
    `pycldf` and related libraries, and those expected by beastling.
    """

    logging.info("Loading CLDF data...")

    # Load languages
    languages_path = cldf_path / "languages.csv"
    with open(languages_path.as_posix()) as csvfile:
        languages = {lang["ID"]: lang for lang in csv.DictReader(csvfile)}

    # Load concepts
    parameters_path = cldf_path / "parameters.csv"
    with open(parameters_path.as_posix()) as csvfile:
        parameters = {param["ID"]: param for param in csv.DictReader(csvfile)}

    # Load forms
    forms_path = cldf_path / "forms.csv"
    with open(forms_path.as_posix()) as csvfile:
        forms = {form["ID"]: form for form in csv.DictReader(csvfile)}

    # Load cognates
    cognates_path = cldf_path / "cognates.csv"
    with open(cognates_path.as_posix()) as csvfile:
        cognates = {cog["ID"]: cog for cog in csv.DictReader(csvfile)}

    # Write data
    data = []
    for cogid, cognate in cognates.items():
        lang_id = forms[cognate["Form_ID"]]["Language_ID"]
        glottocode = languages[lang_id]["Glottocode"]
        feature_id = forms[cognate["Form_ID"]]["Parameter_ID"]
        value = cognate["Cognateset_ID"]

        data.append(
            {
                "Language_ID": lang_id,
                "Glottocode": glottocode,
                "Feature_ID": feature_id,
                "Value": value,
            }
        )

    return data


def filter_data(data, args):
    """
    Filters raw data (from CLDF or NEXUS) for beastling.

    Note that this filtering is performed *before* building the model. `beastling`
    itself allows to perform some filtering; this method is supposed to be used
    to remove data that would not be used in any analysis.
    """

    # We first collect all concepts, then the ratio of concepts with data (non-missing)
    # for each language, and then filter out languages with a ratio below a given
    # threshold (set from command-line). This removes languages with overall not much
    # data; as removing concept with low coverage happens later, this value should
    # not, beforehand, be too aggressive.
    concepts = {entry["Feature_ID"] for entry in data}

    lang_stat = defaultdict(set)
    for entry in data:
        if entry["Value"] != "?":
            lang_stat[entry["Language_ID"]].add(entry["Feature_ID"])

    lang_ratio = {
        lang_id: len(lang_concepts) / len(concepts)
        for lang_id, lang_concepts in lang_stat.items()
    }

    pre_filter_len = len(data)
    data = [
        entry
        for entry in data
        if lang_ratio[entry["Language_ID"]] > args.ratio_threshold
    ]
    logging.info(
        "Filtering according to `ratio_threshold` (from %i to %i items).",
        pre_filter_len,
        len(data),
    )

    # Collect information on mutual coverage, for the second filtering
    cov_stat = defaultdict(set)
    for entry in data:
        if entry["Value"] != "?":
            cov_stat[entry["Feature_ID"]].add(entry["Language_ID"])
    max_cov = max([len(par_taxa) for par_taxa in cov_stat.values()])

    cov_ratio = {
        par_id: len(par_taxa) / max_cov for par_id, par_taxa in cov_stat.items()
    }

    pre_filter_len = len(data)
    data = [
        entry
        for entry in data
        if cov_ratio[entry["Feature_ID"]] > args.coverage_threshold
    ]
    logging.info(
        "Filtering according to `coverage_threshold` (from %i to %i items).",
        pre_filter_len,
        len(data),
    )

    return data


def write_data(tuled_data, base_path, args):
    """
    Write the beastling csv data file.
    """

    # Organize and normalize data for the CSV file
    csv_data = []
    for entry in tuled_data:
        feature_id = unidecode.unidecode(entry["Feature_ID"])
        feature_id = feature_id.upper()
        feature_id = feature_id.split("/")[0].strip()
        feature_id = feature_id.replace("(", "")
        feature_id = feature_id.replace(")", "")
        feature_id = feature_id.replace(",", "")
        feature_id = feature_id.replace(" ", "_")

        if entry["Value"] != "?":
            value = "%s__%s" % (feature_id, entry["Value"])
        else:
            value = "?"

        csv_data.append(
            {
                "Language_ID": entry["Language_ID"],
                "Glottocode": entry.get("Glottocode", ""),
                "Feature_ID": feature_id,
                "Value": value,
            }
        )

    # Write data
    datafile_path = base_path / "beastling" / args.datafile
    with open(datafile_path.as_posix(), "w") as csvfile:
        fieldnames = ["Language_ID", "Glottocode", "Feature_ID", "Value"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)

    logging.info("Wrote %i entries.", len(csv_data))


def write_calibration(calibrations, languages_in_data, base_path, args):
    """
    Write beastling calibration data.

    Calibration data is used in this project also to set the monophyletic groups,
    without depending on Glottolog's tree.
    """

    # Build beastling with language configurations
    calibration_conffile = base_path / "beastling" / "calibration.conf"
    with open(calibration_conffile.as_posix(), "w") as handler:
        handler.write("[calibration]\n")

        for language, calibration in calibrations.items():
            # If the first character is not a digit or if there is an
            # hyphen anywhere, we assume it is a beastling calibration;
            # otherwise, it is a tip that should be detracted from the
            # current year. Note that `date` is originally set to None
            # and will not be written to the configuration if it is not set;
            # we can also decide whether to calibrate very recent
            # languages or not.
            date_calibr = None
            if calibration:
                if calibration[0] in "0123456789" and not "-" in calibration:
                    # Only set languages that are over 100 years old
                    diff = 2.020 - float(calibration)
                    if diff > 0.1:
                        date_calibr = "%.3f" % diff
                else:
                    date_calibr = calibration

            # replace the ROOT node with the list of languages; if we have a group,
            # make sure the labels are sorted. Note that we need to make sure to only
            # add a calibration for languages that passed the various filters.
            if language == "ROOT":
                if date_calibr:
                    handler.write("root = %s\n" % date_calibr)
            elif "," in language:
                # Select only languages that are in data
                clade = [lang.strip() for lang in language.split(",")]
                clade = [lang for lang in clade if lang in languages_in_data]
                if len(clade) > 1 and date_calibr:
                    clade_label = ", ".join(sorted(clade))
                    handler.write("%s = %s\n" % (clade_label, date_calibr))
            else:
                if language in languages_in_data:
                    if date_calibr:
                        handler.write("%s = %s\n" % (language, date_calibr))


def run_beastling(args):
    """
    Run the `beastling` command-line tool to generate the XML model.
    """

    # Generate XML with beastling
    # TODO: use base_path
    command = ["beastling", "--verbose", "-o", "phylo/tuled-tg.xml"]

    if args.overwrite:
        command.append("--overwrite")

    command += [
        "beastling/tuled-tg.admin.conf",
        "beastling/tuled-tg.common.conf",
        "beastling/calibration.conf",
    ]

    subprocess.run(command)


def parse_arguments():
    """
    Parses arguments and returns a namespace.
    """

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "source",
        type=str,
        help="Either the path to a NEXUS file or to a CLDF directory to be used as source",
    )
    parser.add_argument(
        "-d",
        "--datafile",
        type=str,
        default="tuled.csv",
        help="Filename of the CSV data (default: `tuled.csv`)",
    )
    parser.add_argument(
        "-r",
        "--ratio_threshold",
        type=float,
        default=0.5,
        help="Threshold for minimum number of concepts defined in each language",
    )
    parser.add_argument(
        "-c",
        "--coverage_threshold",
        type=float,
        default=0.7,
        help="Threshold for minimum concept coverage",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Whether to overwrite existing .xml files (default: False)",
    )

    args = parser.parse_args()
    return args


def main():
    """
    Script entry point.
    """

    logging.info("Initializing...")

    # Get base path
    base_path = Path(__file__).parent.absolute()

    # Parse command-line arguments
    args = parse_arguments()

    # Load language data
    language_datafile = base_path / "beastling" / "languages.csv"
    calibrations = {}
    nexus_map = {}
    with open(language_datafile.as_posix()) as csvfile:
        logging.info("Loading language data...")
        for row in csv.DictReader(csvfile):
            calibrations[row["Language"]] = row["Calibration"]
            nexus_map[row["Nexus_Name"]] = row["Language"]
        logging.info("Read language data for %i languages/groups.", len(calibrations))

    # Read the data and write it in beastling format; note that the decision on
    # whether to parse the data as a CLDF dataset or as a nexus file is based
    # only on the presence of the ".nex" extension, no more robust verification is
    # performed.
    if args.source.endswith(".nex"):
        tuled_data = read_nexus(nexus_map, args.source)
    else:
        # Read CLDF data and write it, if necessary/asked for
        # TODO: check if it is really a CLDF directory (perhaps point to metadata?)
        cldf_path = Path(args.source).absolute()
        tuled_data = read_cldf(cldf_path)

    # Filter data in terms of languages, parameters, etc. and write it
    data = filter_data(tuled_data, args)
    write_data(data, base_path, args)

    # Load configuration for calibration and write beastling calibration; we need
    # an auxiliary list with the name of all languages as well
    languages_in_data = sorted({entry["Language_ID"] for entry in data})
    write_calibration(calibrations, languages_in_data, base_path, args)

    run_beastling(args)


if __name__ == "__main__":
    # config logger
    logging.basicConfig(level=logging.INFO)

    # Call entry point
    main()

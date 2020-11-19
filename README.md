# tuled-phylo - tupi-guarani

Code and data for classification of Tupi-Guarani languages

## System requirements

The analysis pipeline has a number of software requirements, mainly a working
Python installation, for preparing the data, and a Java environment for
running `beast2`.

The minimum Python version is 3.7. You can verify if your version of Python is compatible by issuing
the following command:

```bash
$ python --version
```

Please note that in some systems the executable might be called
`python3`, `python3.7` or something
similar. If you don't have Python installed, you can follow
[these instructions](https://www.python.org/downloads/).

The system also requires the `pip` package manager, which should be already
installed in most systems. Once more, you can check with the `pip --version` command;
if you do not have `pip` installed, find the appropriate way to install it in your
system (which might be different from the
[official instructions](https://pip.pypa.io/en/stable/installing/)).

You also need to have `git` installed and working. If you don't, consult the
documentation for your system (Bitbucket provides a
[good tutorial](https://www.atlassian.com/git/tutorials/install-git)).

It is highly recommended that you use a virtual environment. Different Python
distributions, such as Anaconda, will offer different alternatives for virtual
environments, but here we will follow the most common one.

(instructions for Java)

### Set up the repository

Go to the directory where you want to store these data, clone this repository and
move into it:

```bash
$ git clone https://github.com/LanguageStructure/phyloTG
$ cd phyloTG
```

Create a virtual environment and activate it:

```bash
$ python -m venv env
$ source env/bin/activate
```

Remember that, once you are done, you can leave the virtual environment with the
`deactivate` command.

You should also make sure that `pip` and related libraries are up-to-date:

```bash
$ pip install --upgrade pip wheel
```

Install the necessary Python packages:

```bash
$ pip install -r requirements.txt
```

If you have never installed the CLDF catalogs before, issue the following command, which
will set up a system-wide copy of the GitHub repositories for
[Glottolog](https://glottolog.org/),
[Concepticon](https://concepticon.clld.org/),
and [CLTS](https://clts.clld.org/). Note that this can take some minutes depending on
your connection speed.

```bash
$ cldfbench catconfig -q
```

### Install BEAST

(...)

## Download released data

The following Python script will download the latest released data, storing it in
`raw/`, and uncompress its contents to `data/`.

```bash
$ python download_data.py
```

## Build the BEAST2 XML configuration

To build the BEAST2 XML configuration, using `beastling`, run:

```bash
$ python build_xml.py
```

## Run the analysis

To run the analysis with BEAST, which takes a long time, run:

```
$ beast phylotupi-expert.xml
```

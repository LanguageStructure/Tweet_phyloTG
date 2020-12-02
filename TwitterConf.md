# [Linguistweets](https://www.linguistweets.org) Conference ([ABRALIN](https://www.abralin.org))

This page contains the [Twitter presentation]() and additional comments to it with references. The content was presented (tweeted) by Fabrício Ferraz Gerardi, Tiago Tresoldi and Stanislav Reichert on the 05 of December 2020.

## 1 (Introduction)

<div align="justify">

Tupí-Guaraní (TG) is the largest linguistic family of South-America. Little is known about its spread (genes and languages). Historical linguistics has tools to investigate such issue. Even more aided by digital data, computers, and methods from evolutionary biology.

</div>


[Tupí-Guaraní Languages](https://glottolog.org/resource/languoid/id/tupi1276) |  [Phylogenetic Tree](https://www.pnas.org/content/116/45/22657)
:-------------------------:|:-------------------------:
<img src="TG_map.png" width="260" height="200"> | <img src="F1.large.jpg" width="260" height="200">

## 2 (Data)

Using phylogenetic tools (BEAST2, beastling), we build linguistic trees from open-access reusable data in CLDF, lifted with EDICTOR from TuLeD (285 concepts, 40 TG langs, 16211 words). We first detected 2832 cognate sets with LexStat, then reviewed 40% manually (ongoing work).

[TuLeD](https://tuled.org) |  [CLDF](https://cldf.clld.org) | [EDICTOR](https://digling.org/edictor/) | [Linguistic Tree](https://www.pnas.org/content/116/21/10317)      |
:-------------------------:|:-------------------------:|:-------------------------:|:--------------------------:
<img src="tuled.png" width="280" height="200"> | <img src="cldf.png" width="280" height="200"> | <img src="edictor.png" width="280" height="200"> | <img src="F2.large.jpg"  height="200">


## 3 (Goal)

Linguistic trees display classifications comparable with results from other fields (Archaeology, Ethnography, History). We first test a model on lexical data only, then we interpret results considering extra-linguistic data, evaluating hypotheses, and accordingly improve data and model.

[Archaeology](https://amazonexpand.wixsite.com/expand) | [Archaeology](https://raw.githubusercontent.com/jgregoriods/rxpand/master/img/tutish.png) | Ethnographic Information |Amount of cognates
:-------------------------:|:-------------------------:|:---------------------:|:---------------------:|
<img src="https://static.wixstatic.com/media/7bbfe9_af29f695208b4b56a8468c205806fd75~mv2.png/v1/fill/w_538,h_658,al_c,usm_0.66_1.00_0.01/EmbeddedImage%20(1).png" height="200"> | <img src="tutish.png" height="200"> | <img src="bookCover.png" height="200"> |<img src="HeatMap_Cogs.jpeg" height="200">


## 4 (Explaining a model)

Evolutionary methods: we experiment from simple (NJ) to highly complex ones for millions of trees (Bayesian MCMC, covarion model, relaxed clock). The challenge is to deliver the best single tree to summarize the results.

NJ | NeighbourNet | Density Tree | (Gerhard's method) |
:-------------------------:|:-------------------------:|:--------------------:|:-----------------|
(pic)  | (pic) | <img src="DensiTree_TG.png" width="260" height="200"> | (pic)


## 5 (Preliminary RESULTS)

Mawetí-Guaraní hypothesis recognized. Fast expansion of the Guaraní slows ca. year 1580. 4 major groups identified. Blue group supports ethnogr/hist/ling evidence: dialect continuum, common area of origin, close contact. 

[Mawetí-Guaraní Hypothesis](https://glottolog.org/resource/languoid/id/mawe1252) | Phylogenetic Tree | (label) |
:-------------------------:|:-------------------------:|:--------------------:
(pic)  | <img src="TG_Tree.png" width="260" height="200"> | (pic)


## 6 (To do and REFS)

Collect more hist. information, improve cognacy. Cogancy alone is not all, include other ling. data. Constrain and calibrate model(s) (dates, geography, ratios, monophyletic groups). More info., references, and comments: https://tular.org/tgtweet 

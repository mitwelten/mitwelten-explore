# Datasets

This page gives an overview of the datasets that are available in this tool.

## Meteodata

*Datasets can be selected in [Datasets > Meteodata](select/meteo)*


Meteodata are provided by [MeteoSchweiz](https://www.meteoschweiz.admin.ch/).
The parameters are available in raw form and as aggregated values, with the aggregation described in the respective parameter name.


## Bird Dataset

*The Bird Dataset is located in [Datasets > Detections by Taxonomy](select/taxon)*


The BirdNET results dataset was collected as part of the [Mitwelten](https://www.mitwelten.org/) project.
It represents bird calls on audio recordings that were analyzed with the BirdNET algorithm.
The audio recordings were collected with [AudioMoths](https://www.openacousticdevices.info/audiomoth), full spectrum microphones from Open Acoustic Devices, at different locations and times. 

**<img src="assets/icons/warning-filled.svg" style="height:20px;" /> Interpretation and Quality of the Data**

Entries in the dataset are detected bird calls, not individuals. The acoustic activity of birds can vary greatly by species and time, making direct comparisons meaningful only with appropriate background information. It is possible that calls were not recognized or were misrecognized. Species exist that mimic calls of other species. It is possible that imitated calls lead to wrong results.
Recording periods were not uniform across all microphones. A smaller recording period will potentially result in fewer calls being detected. The quality of the audio recordings may affect the results. Quality degradation is possible in locations with loud ambient noise.



## Pax Data

*PAX data can be selected in [Datasets > Mitwelten PAX](select/pax)*

A PAX Counter is a system that counts smartphones. As part of the Mitwelten project, PAX counters were developed that receive periodically transmitted signals from smartphones and transmit the number of unique smartphones within a radius of a few meters as a measured value. The sum of the detected devices per time interval is transmitted. If a device is in range over several measurement intervals, it is counted in each measurement. For PAX counters connected via WiFi, the measurement interval is much smaller than for LoRa devices, which makes a direct comparison impossible.


## Pollinators

*Pollinator data can be selected in [Datasets > Detections by Taxonomy](select/taxon) or in [Datasets > Mitwelten Pollinators](select/pollinator) (by deployment)*


As part of the Mitwelten project, a pollinator study was conducted. Flower pots were placed at various locations. Cameras were used to take pictures of the flowers at regular intervals.
On the captured images, flowers are cut out with an ML object recognition model, on which pollinators are recognized in a second step.

**Available pollinator categories**

|Fliege|Honigbiene|Hummel|Schwebfliege|Wildbiene|
|:-:|:-:|:-:|:-:|:-:|
|Family Muscidae|Genus Apis|Genus Bombus|Family Syrphidae|Family Apidae|
|<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/2/20/Fly_close.jpg/300px-Fly_close.jpg" style="height:150px; width:180px; object-fit:cover;" alt="fliege" /> | <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Apis_mellifera_Western_honey_bee.jpg/577px-Apis_mellifera_Western_honey_bee.jpg" style="height:150px; width:180px; object-fit:cover;" alt="honigbiene" />|<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/7/7f/Bombus_lapidarius1.jpg/640px-Bombus_lapidarius1.jpg" style="height:150px; width:180px; object-fit:cover;" alt="hummel" />|<img src="https://upload.wikimedia.org/wikipedia/commons/c/c9/Schwebfliege.jpg" style="height:150px; width:180px; object-fit:cover;" alt="schwebfliege" />|<img src="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/DasypodaHirtipesFemale1.jpg/640px-DasypodaHirtipesFemale1.jpg" style="height:150px; width:180px; object-fit:cover;" alt="wildbiene" />|
|*GBIF Reference*|*GBIF Reference*|*GBIF Reference*|*GBIF Reference*|*GBIF Reference*|
|[5564](https://www.gbif.org/species/5564)|[1334757](https://www.gbif.org/species/1334757)|[1340278](https://www.gbif.org/species/1340278)|[6920](https://www.gbif.org/species/6920)|[4334](https://www.gbif.org/species/4334)|


<div style="padding:30px">
</div>

**Taxonomy of the available pollinator categories**

<img src="assets/images/polli_taxonomy.png" style="maxWidth:100%;" />



## Env Sensor Data

*Datasets can be selected in [Datasets > Mitwelten Env](select/env)*

*<img src="assets/icons/warning-filled.svg" style="height:20px;" />  Only data of the year 2021 is available*

The environment dataset was collected as part of the [Mitwelten](https://www.mitwelten.org/) project.
Following parameters were measured by multiple low-power sensor nodes at different locations:
* Air temperature, 30cm above ground (&deg;C)
* Relative air humidity, 30cm above ground (%RH)
* Soil moisture, 5cm underneath the surface (Absolute value between 0 and 1024)

## Location Characteristics

*Work in progress*

## GBIF Records

*Datasets with 3rd party observations are available in [Datasets > Detections by Taxonomy](select/taxon)*

There are a variety of institutions and communities that record observations of species. GBIF (Global Biodiversity Information Facility) is a platform that collects datasets from different sources and provides the observations in a standardized format.

The observations obtained from external sources can be used to validate parts of the automated observations made in the Mitwelten project. For rare species, it is possible to check if and when the species has already been detected in the surrounding area.

The datasets in this tool only include observations of birds and insects made within a 20 km radius of the Merian Gardens.

**<img src="assets/icons/warning-filled.svg" style="height:20px;" /> Interpretation and Quality of the Data**
* For some observations, the detection timestamp does not contain the time. Those observations are excluded in the Time of Day visualizations.

## GBIF Backbone Taxonomy

The [GBIF Backbone Taxonomy](https://www.gbif.org/dataset/d7dddbf4-2cf0-4f39-9b2a-bb099caae36c) dataset is used to translate names of the species and to query their taxonomy tree. This information is used for the representation and filtering of birds and pollinator detections.


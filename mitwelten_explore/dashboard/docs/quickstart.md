# Quickstart

*Follow the steps to get to know this tool*


## 1. Find an interesting dataset

---

#### Detections by taxonomy (Birds & Pollinators, Mitwelten & GBIF)

Hover over the text **Datasets** in the header of this page and click on a dataset type.

* Click on [Detections by Taxonomy](/app/select/taxon)
* Select the taxonomy level you are looking for, the list will update on change.
* Click on the taxon of interest (you can use the search input to search the content of the list)
* A Popup which contains information about the taxon (see image below) will appear.




<img src="assets/images/taxon_modal.png" style="maxWidth:50%;" />




* The number of Mitwelten detections and the number of GBIF Observations for the selected taxon are indicated in the upper right area.
* A short description and an image, both from from Wikipedia are shown in the center.
* The parent taxonomy classes are indicated above the image and the description. **K** stands for Kingdom, **P** for Phylum etc.
* In the lower section, there are three buttons:
  * **Add Mitwelten Detections to Collection** to add Observations from the Mitwelten Project to your collection.
  * **Add GBIF Observations to Collection** to add Observations made by third party institutions to your collection.
  * **Go to Taxon Dashboard** to open the Taxon Dashboard of the selected taxon in a new tab.


The whole process of adding Mitwelten Detections and GBIF Observations of the hover fly to the collection is shown in the animated image below.

<img src="assets/images/taxon_select.gif" style="maxWidth:75%;" />


---

#### Meteodata

Hover over the text **Datasets** in the header of this page and click on a dataset type.

* Click on [Meteodata](/app/select/meteo).
* Filter the datasets:
  * Select a meteo station by using the field *Meteo Station* or by clicking on a marker on the map.
  * Select the unit by using the field *Unit*
  * The list of available datasets will update on change of the filters.
* To add a dataset to the collection, click on the Bookmark icon <img src="assets/icons/bookmark-outline-rounded.svg" style="height:24px;" /> to the right of the dataset.
* To go directely to the Time Series Dashboard, click on the button **Viz**.
  * If you want to compare the dataset with other datasets, you should add the dataset to the collection.


---

#### PAX Counter

Hover over the text **Datasets** in the header of this page and click on a dataset type.

* Click on [Mitwelten PAX](/app/select/pax).
* Filter the datasets:
  * Select a deployment by using the field *Deployment* or by clicking on a marker on the map.
* To add a dataset to the collection, click on the Bookmark icon <img src="assets/icons/bookmark-outline-rounded.svg" style="height:24px;" /> to the right of the dataset.
* To go directely to the Time Series Dashboard, click on the button **Viz**.
  * If you want to compare the dataset with other datasets, you should add the dataset to the collection.



## 2. Explore a single dataset in the Time Series Dashboard

The *[Time Series Dashboard](viz/timeseries)* is designed to visualize a dataset with the time as primary axis.
* There are multiple ways to get to the Dashboard:
  * If the dataset is in your collection, you can hover over the text **Visualize** in the page header and click on **Single Time Series**. A Popup with the datasets of your collection will appear. Click on a dataset to go to the dashboard.
  * If you want to open the Time Series Dashboard for a dataset that is not in the collection, click on the **Viz** button of any dataset in a dataset selection page.


The Dashboard contains following components:
* The title of the dataset and a location name
* Controls:
  * Time Range of the shown data
  * Time bucket width (Resolution of the data)
  * Confidence (For ML Results)
  * Aggregation Method (`sum()` for detections)
* The time series chart
* The time of day chart
* Statistical aggregates
* A map which shows where the datapoints were recorded

<img src="assets/images/aves_ts_dashboard.png" style="maxWidth:75%;" />



## 3. Compare two or more datasets

Hover over the text **Visualize** in the page header and click on **Compare Datasets**.

The datasets you want to compare have to be selected by clicking on the ckeckboxes. Up to 5 datasets can be compared in this Dashboard.
After the selection, click on **Compare** to go to the dashboard.

## 6. Create an Annotation

*TODO*


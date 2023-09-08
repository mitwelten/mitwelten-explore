# Quickstart

*Follow the steps to get to know this tool*


<img src="assets/images/quickstart.png" style="maxWidth:80%;" />

**You can use the navbar to navigate between the steps**


## Find an interesting dataset and collect it


#### Detections by taxonomy (Birds & Pollinators, Mitwelten & GBIF)

Hover over the text **Datasets** in the header of this page and click on a dataset type.

* Click on [Detections by Taxonomy](/app/select/taxon)
* Select the taxonomy level you are looking for, the list will update on change.
* Click on the taxon of interest (you can use the search input to search the content of the list)
* A Popup which contains information about the taxon (see image below) will appear.



<div style="padding:15px 30px 15px 15px">
<img src="assets/images/taxon_modal.png" style="maxWidth:80%;" />
</div>



* The number of Mitwelten detections and the number of GBIF Observations for the selected taxon are indicated in the upper right area.
* A short description and an image, both from from Wikipedia are shown in the center.
* The parent taxonomy classes are indicated above the image and the description. **K** stands for Kingdom, **P** for Phylum etc.
* In the lower section, there are three buttons:
  * **Add Mitwelten Detections to Collection** to add Observations from the Mitwelten Project to your collection.
  * **Add GBIF Observations to Collection** to add Observations made by third party institutions to your collection.
  * **Go to Taxon Dashboard** to open the Taxon Dashboard of the selected taxon in a new tab.


The whole process of adding Mitwelten Detections and GBIF Observations of the hover fly to the collection is shown in the animated image below.

<div style="padding:15px 30px 15px 15px">
<img src="assets/images/taxon_select.gif" style="maxWidth:100%;border:1px solid gray;" />
</div>


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



#### PAX Counter

Hover over the text **Datasets** in the header of this page and click on a dataset type.

* Click on [Mitwelten PAX](/app/select/pax).
* Filter the datasets:
  * Select a deployment by using the field *Deployment* or by clicking on a marker on the map.
* To add a dataset to the collection, click on the Bookmark icon <img src="assets/icons/bookmark-outline-rounded.svg" style="height:24px;" /> to the right of the dataset.
* To go directely to the Time Series Dashboard, click on the button **Viz**.
  * If you want to compare the dataset with other datasets, you should add the dataset to the collection.


##### The selection of [Bird diversity](/app/select/bird) and [Pollinator](/app/select/pollinator) follows the same principle.


---

## Visualize
### Explore a single dataset in the Time Series Dashboard

The *[Time Series Dashboard](viz/timeseries)* is designed to visualize a dataset with the time as primary axis.

There are multiple ways to get to the Dashboard:
  * If the dataset is in your collection, you can hover over the text **Visualize** in the page header and click on **Single Time Series**. A Popup with the datasets of your collection will appear. Click on a dataset to go to the dashboard.
  * If you want to open the Time Series Dashboard for a dataset that is not in the collection, click on the **Viz** button of any dataset in a dataset selection page.



<div style="padding:15px 30px 15px 15px; ">
<img src="assets/images/aves_ts_dashboard.png" style="maxWidth:100%;border:1px solid gray;" />
</div>


---

### Compare two or more datasets

**The datasets to compare have to be stores in the collection**

Hover over the text **Visualize** in the page header and click on **Compare Datasets**.
* A Popup with a list of all datasets in your collection will appear:

<div style="padding:15px 30px 15px 15px">
<img src="assets/images/compare_select.png" style="maxWidth:80%;" />
</div>

* Check the checkboxes to the left of the dataset title to add the dataset to the dashboard.
* If at least two datasets are selected, the **Compare** button will be enabled. Click on it to load the dashboard.


A Dashboard that compares Mitwelten detections of the class Insecta, Air temperature 5cm above the ground, Global radiation and Diffuse radiation is shown in the image below.


<div style="padding:15px 30px 15px 15px">
<img src="assets/images/comp_dashboard.png" style="maxWidth:100%;border:1px solid gray;" />
</div>

---


### Explore a Taxon in the Taxon Dashboard

the taxon dashboard was developed to analyze the temporal and spatial activity of species or higher taxonomic classes.
There are two ways to access the Taxon Dashboard:
* If a taxon dataset is in the collection, there will be a button **Taxon Dashboard** next to the dataset name in [your Collection](collection)
* There is a direct link to the Taxon Dashboard for every taxon in the [Detections by Taxonomy](/app/select/taxon) selection page, after clicking on an item in the list.


A Taxon Dashboard for the order Apodiformes is shown in the image below.

<div style="padding:15px 15px 15px 15px">
<img src="assets/images/taxon_dashboard.png" style="maxWidth:100%;border:1px solid gray;" />
</div>

### See all available dashboards in the [dashboard section](docs#dashboards)
---
## Create an Annotation
Share your insights with other users!


See [Annotations](docs#annotations)

---


## Share a dashboard

To share a dashboard view, click on the green button <img src="assets/icons/more-two.svg" style="height:24px;" /> in the lower right corner of a dashboard  to expand the actions menu, then click on the Share button <img src="assets/icons/share.svg" style="height:24px;" />. 

A popup which contains a button *Copy to Clipboard* will appear. Click on it to copy the dashboard url to the clipboard.






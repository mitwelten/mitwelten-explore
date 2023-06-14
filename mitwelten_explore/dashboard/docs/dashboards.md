# Dashboards


## Time Series Dashboard

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


<div style="padding:15px 30px 15px 15px; ">
<img src="assets/images/aves_ts_dashboard.png" style="maxWidth:75%;border:1px solid gray;" />
</div>



## Comparison Dashboard

**The datasets to compare have to be stores in the collection**

Hover over the text **Visualize** in the page header and click on **Compare Datasets**.
* A Popup with a list of all datasets in your collection will appear:

<div style="padding:15px 30px 15px 15px">
<img src="assets/images/compare_select.png" style="maxWidth:60%;" />
</div>

* Check the checkboxes to the left of the dataset title to add the dataset to the dashboard.
* If at least two datasets are selected, the **Compare** button will be enabled. Click on it to load the dashboard.

The Dashboard contains following components:
* Controls:
  * Time Range of the shown data
  * Time bucket width (Resolution of the data)
* Dataset Card For every selected dataset
  * Every card contains the dataset title and location information
  * The color of the card corresponds to the colors in the charts
  * To modify the confidence, the aggregation method or to normalize the time series data, click on the **Edit Symbol** on the card.
* The time series chart
* The time of day chart (can be hidden by clicking on the tab)
* Statistical aggregates (will expand by clicking on the tab)
* Correlation and FFT (will expand by clicking on the tab)
* A map which shows where the datapoints were recorded (will expand by clicking on the tab)

A Dashboard that compares Mitwelten detections of the class Insecta, Air temperature 5cm above the ground, Global radiation and Diffuse radiation is shown in the image below.


<div style="padding:15px 30px 15px 15px">
<img src="assets/images/comp_dashboard.png" style="maxWidth:75%;border:1px solid gray;" />
</div>

---


## Taxon Dashboard

the taxon dashboard was developed to analyze the temporal and spatial activity of species or higher taxonomic classes.
There are two ways to access the Taxon Dashboard:
* If a taxon dataset is in the collection, there will be a button **Taxon Dashboard** next to the dataset name in [your Collection](collection)
* There is a direct link to the Taxon Dashboard for every taxon in the [Detections by Taxonomy](/app/select/taxon) selection page, after clicking on an item in the list.


The Dashboard contains following components:
* The name and taxonomy level of the selected taxon
* Controls:
  * Time Range of the shown data.
  * Time bucket width (Resolution of the data).
  * Confidence (For ML Results).
  * Data source (Mitwelten Data and/or GBIF Observations).
* The time series chart.
* A map which shows the sum of detections per clusters. The cluster size will change on zoom.
* The time of day chart (total detections per `time_of_day bucket` over the selected time period).
* The number of total detections and the number of mitwelten deployments where the taxon was detected.
* Taxon Info Card which contains:
  * An image of the taxon (from Wikipedia, if available)
  * The taxonomy tree with links to the respective taxon dashboards
  * A textual description (from Wikipedia, if available)
* A list containing the most detected species of the selected parent taxon class (Mitwelten detections only)

A Taxon Dashboard for the order Apodiformes is shown in the image below.

<div style="padding:15px 15px 15px 15px">
<img src="assets/images/taxon_dashboard.png" style="maxWidth:75%;border:1px solid gray;" />
</div>



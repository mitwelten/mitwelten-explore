# Charts


The interactive charts in this tool are made with [Plotly](https://plotly.com/). 

## Zoom, Pan & Select

#### Drag to zoom

<img src="https://plotly.github.io/static/images/zoom-pan-hover/drag-to-zoom.gif" style="maxWidth:60%;" />



#### Zoom axis

<img src="https://plotly.github.io/static/images/zoom-pan-hover/zoom-axis.gif" style="maxWidth:60%;" />



#### Drag to pan

<img src="https://plotly.github.io/static/images/zoom-pan-hover/drag-to-pan.gif" style="maxWidth:60%;" />



#### Pan axis

<img src="https://plotly.github.io/static/images/zoom-pan-hover/pan-axis.gif" style="maxWidth:60%;" />

#### Reset zoom

Double-click on the chart to reset both axis or on an axis to reset the axis.



*Images by [plotly](https://plotly.com/chart-studio-help/zoom-pan-hover-controls/)*

### Reload time range on zoom <img src="assets/icons/reload_switch.svg" style="height:20px;" />

If *reload on zoom* is enabled, the time range of the dashboard will be updated to the zoomed x-axis range.
- If the time range should be preserved, turn it off by clicking on the switch before zooming.





## Chart configuration


Click on the Menu icon <img src="assets/icons/menu-fill.svg" style="height:21px;" /> in the upper right corner of the chart to change the chart properties:

<img src="assets/images/chart_menu_h.png" style="maxWidth:75%;" />




### Chart types



**Line Plot**|**Area Plot**
:-:|:-:
In the line plot, every datapoint is connected with a line|The area plot is a line plot but filled to the zero point in the y-axis
<img src="assets/images/line_chart.png" style="maxWidth:95%;" />|<img src="assets/images/area_chart.png" style="maxWidth:95%;" />



**Scatter Plot**|**Bar Plot**
:-:|:-:
The scatter plot shows every datapoint as a point.|The bar plot shows a bar from the zero point to the value for each datapoint.
<img src="assets/images/scatter_chart.png" style="maxWidth:95%;" />|<img src="assets/images/bar_chart.png" style="maxWidth:95%;" />



### Layout types



**Overlay**|**Subplots**
:-:|:-:
In the overlay layout, there exists one y axis. Normalization might be helpful to compare datasets.|In the subplots layout, every dataset has its subplot with its y axis.
<img src="assets/images/overlay_chart.png" style="maxWidth:100%;" />|<img src="assets/images/line_chart.png" style="maxWidth:100%;" />

* The chart type and layout type for will be stored persistently in your browser.







# API Usage

See [Mitwelten Data API](https://data.mitwelten.org/api/v3/docs)

## Jupyter Notebooks

* [Bird Detections](https://colab.research.google.com/drive/1dLs__SQc4Dhn1tyFSjp67KbX7a1HsZKG?usp=sharing)


## Examples

### Bird detection dates

Get detection dates by scientific name

1. Get the `species_id`

```py
import requests

SPECIES_NAME = "Apus apus"
url = f"https://data.mitwelten.org/api/v3/taxonomy/sci/{SPECIES_NAME}"
taxonomy_tree = requests.get(url).json()
species_id = taxonomy_tree[0].get("datum_id")
# 5228676
```

```py
from datetime import datetime
from urllib.parse import urlencode

CONFIDENCE = 0.8
BUCKET_WIDTH = "1d"
TIME_FROM = datetime(2021, 5, 1).isoformat()
TIME_TO = datetime(2021, 9, 1).isoformat()
params = {
    "conf": CONFIDENCE,
    "bucket_width": BUCKET_WIDTH,
    "from": TIME_FROM,
    "to": TIME_TO,
}
url = f"https://data.mitwelten.org/api/v3/birds/{species_id}/date?{urlencode(params)}"
response = requests.get(url).json()
```

`detections` is a dict in following structure:
```json
{
    "bucket": [
        "2021-05-10T00:00:00+00:00",
        "2021-05-11T00:00:00+00:00",
        ...
    ],
    "detections": [
        35,
        381,
        ...
    ]
}    
```

Plot the data using plotly
```py
import plotly.graph_objects as go
fig = go.Figure(go.Bar(x=detections.get("bucket"),y=detections.get("detections")))
fig.show()
```
<img src="assets/images/api_usage_bar_chart.png" style="width:100%;" />



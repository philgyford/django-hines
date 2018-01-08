# Mappiness chart

For charting data from the [Mappiness app](http://www.mappiness.org.uk/) (or
using semi-randomly-generated example data).

[I wrote more about the chart on my website](http://www.gyford.com/phil/writing/2014/07/24/mappiness-chart.php).

## Development

While developing, it's a pain to have to keep fetching your JSON data. So,
download your raw data as a JSON file using the data download link from the
app. 

Put your JSON file, named `mappiness.json`, in the same directory as this code
(at the same level as `index.html`).

Put the code on a webserver (it won't load the JSON file if run locally from a
`file://` URL).

Load `index.html`.

**NOTE:** You may want to ensure the JavaScript files aren't cached while
developing. In `js/mappiness.js`, uncomment the `urlArgs` line used by
require.js to do this.


/**
 * Bar charts.
 * Requires D3.js (v5).
 *
 * Example usage for simple bar chart:
 *
 *  <div class="js-chart"></div>
 *
 *  <script>
 *    var data = [
 *      {
 *        'label': '2012',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 32}
 *        }
 *      },
 *      {
 *        'label': '2013',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 46}
 *        }
 *      },
 *      {
 *        'label': '2014',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 25}
 *        }
 *      }
 *    ];
 *
 *    var chart = hines.chart();
 *
 *    d3.select('.js-chart').datum(data).call(chart);
 *
 *  </script>
 *
 * We can also generate stacked bar charts by providing extra data groups of data:
 *
 *    var data = [
 *      {
 *        'label': '2012',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 32},
 *          'dogs': {'label': 'Dogs', 'value': 23},
 *        }
 *      },
 *      {
 *        'label': '2013',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 46},
 *          'dogs': {'label': 'Dogs', 'value': 29},
 *        }
 *      },
 *      {
 *        'label': '2014',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 25},
 *          'dogs': {'label': 'Dogs', 'value': 32},
 *        }
 *      },
 *    ];
 *
 * Also, each element can have an optional "url" element that will make that bar
 * clickable:
 *
 *    var data = [
 *      {
 *        'label': '2012',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 32, 'url': '/cats/2012'}
 *        }
 *      },
 *      {
 *        'label': '2013',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 46, 'url': '/cats/2013'}
 *        }
 *      },
 *      {
 *        'label': '2014',
 *        'columns': {
 *          'cats': {'label': 'Cats', 'value': 25, 'url': '/cats/2014'}
 *        }
 *      }
 *    ];
 */
(function() {
  "use strict";

  window.hines = window.hines || {};

  window.hines.chart = function(selection) {

    /**
     * Can be changed using the chart.numberFormatPrefix() method.
     */
    var numberFormatPrefix = "";

    /**
     * Can be changed using the chart.numberFormatSuffix() method.
     */
    var numberFormatSuffix = "";

    /**
     * Can be changed using the chart.margin() method.
     */
    var margin = { top: 5, bottom: 20, left: 50, right: 5 };

    /**
     * Can be changed using the chart.tooltipFormat() method.
     * @param {object} The d3 element. Superficially an array containing two
     *  integers, for lower and upper y values. But also has a data element
     *  containing more...
     * @param {string} The key for which bar this is. This will correspond to
     *  a key in d.data, like "cats" in the examples.
     */
    var tooltipFormat = function(d, groupKey) {
      var text = "<strong>" + d.data.label + ":</strong> ";
      if (chartType == "bar-stacked") {
        // Only need to show the group label if there are stacked bars.
        text += d.data.columns[groupKey]["label"] + ": ";
      }
      text += numberFormat(d.data.columns[groupKey]["value"]);
      return text;
    };

    // Internal things that can't be overridden:

    var xScale = d3.scaleBand();
    var yScale = d3.scaleLinear();
    var xAxis = d3
      .axisBottom(xScale)
      .tickSize(0)
      .tickPadding(6);
    var yAxis = d3
      .axisLeft(yScale)
      .ticks(5)
      .tickSize(0)
      .tickPadding(6)
      .tickFormat(numberFormat);
    // The horizontal lines:
    var yAxisGrid = d3
      .axisLeft(yScale)
      .ticks(5)
      .tickFormat("");
    var barPadding = 0.1;

    // Might be changed to "bar-stacked" if we have multiple bars per label:
    var chartType = "bar";

    // The tooltip that appears when hovering over a bar or span.
    // Only need to create the element once, no matter how many charts are
    // on the page.
    var tooltip;
    if (document.getElementsByClassName("chart-tooltip").length == 0) {
      tooltip = d3
        .select("body")
        .append("div")
        .classed("chart-tooltip js-chart-tooltip", true);
    } else {
      tooltip = d3.select(".chart-tooltip");
    }

    /**
     * Utility function: Adds a comma to numbers of 5 or more digits.
     */
    function numberFormat(d) {
      var ret;
      if (("" + d3.format(".0f")(d)).length > 4) {
        ret = d3.format(",")(d);
      } else {
        ret = d3.format("d")(d);
      }
      return numberFormatPrefix + ret + numberFormatSuffix;
    };

    /**
     * When cursor goes over a bar.
     */
    function onMouseover(d) {
      // Get the name of the group this rect is in:
      var groupKey = d3.select(this.parentNode).datum().key;
      tooltip.html(tooltipFormat(d, groupKey));
      tooltip.style("visibility", "visible");
    };

    /**
     * When cursor moves while over a bar.
     * Bit hacky. Keep the tooltip onscreen when it's at the right-most edge.
     */
    function onMousemove(d) {
      // Default, slightly to right of cursor:
      var tooltipLeft = event.pageX + 15;

      if (window.innerWidth - event.pageX < 120) {
        // Close to edge; put it to left of cursor:
        tooltipLeft = event.pageX - 90;
      }

      tooltip
        .style("top", event.pageY - 10 + "px")
        .style("left", tooltipLeft + "px");
    }

    /**
     * When cursor leaves a bar.
     */
    function onMouseout() {
      tooltip.style("visibility", "hidden");
    }

    /**
     * When a bar is clicked/tapped.
     */
    function onClick(d) {
      // Get the name of the group this rect is in:
      var groupKey = d3.select(this.parentNode).datum().key;
      // The original data for a single bar:
      var groupData = d.data[groupKey];
      if ("url" in groupData && groupData["url"]) {
        window.location.href = groupData["url"];
      } else {
        return false;
      }
    }

    /**
     * @param {object} selection The HTML elements to draw charts in.
     */
    function chart(selection) {

      selection.each(function(data) {
        var container = d3.select(this);

        // Need to be in a scope available to all the render methods.
        var chartW;
        var chartH;

        // The keys that we identify each of the coloured bar groups:
        var barGroupKeys = Object.keys(data[0].columns);

        if (barGroupKeys.length > 1) {
          chartType = "bar-stacked";
        }

        // Transform the data into what we need for stacked bar chart:
        var stack = d3.stack().keys(barGroupKeys).value(function(d, key) {
          return d.columns[key]["value"];
        });
        var seriesData = stack(data);

        // Set the domains for the scales based on the data:
        xScale.domain(
          data.map(function(d) { return d.label; })
        );
        yScale.domain([
          0,
          d3.max(seriesData, function(d) { return d3.max(d, function(d) { return d[1]})})
        ]);

        // Create new elements:
        var svg = container.append("svg");
        var inner = svg.append("g")
          .classed("chart__inner chart__inner--" + chartType, true);

        createAxes();

        // Append after the y-axis grid so that the bars are in front of grid:
        var barGroupsContainer = inner.append("g");

        // Render the chart and do it again on resize.
        render();
        window.addEventListener("resize", render);

        /**
         * Calculates size of chart, renders axes and chart contents.
         * For the first time or on window resize.
         */
        function render() {
          setChartSize();
          renderAxes();
          renderBars();
        }

        /**
         * Create the axes' elements.
         * Only happens once at the start.
         */
        function createAxes() {
          var xAxisG = inner
            .append("g")
            .classed("chart__axis chart__axis--x", true);

          // Add extra classes depending on the number of ticks on x-axis:
          if (data.length > 30) {
            xAxisG.classed("chart__axis--x--30", true);
          } else if (data.length > 20) {
            xAxisG.classed("chart__axis--x--20", true);
          } else if (data.length > 15) {
            xAxisG.classed("chart__axis--x--15", true);
          } else if (data.length > 10) {
            xAxisG.classed("chart__axis--x--10", true);
          }

          // Separate elements for the y-axis and its grid over the chart:
          inner.append("g").classed("chart__axis chart__axis--y", true);
          inner.append("g").classed("chart__axis chart__axis--y--grid", true);
        }

        /**
         * Sets the size of the chart based on window width.
         */
        function setChartSize() {
          // Outer width, including space for axes etc:
          var width = parseInt(container.style("width"), 10);
          var height = parseInt(container.style("height"), 10);

          // Inner width, chart area only, minus margins for axes etc.
          chartW = width - margin.left - margin.right;
          chartH = height - margin.top - margin.bottom;

          // Set the scales for these dimensions.
          xScale.range([0, chartW]).padding(barPadding);

          yScale.rangeRound([chartH, 0]);

          // Update outer dimensions.
          svg
            .transition()
            .attr("width", width)
            .attr("height", height);

          inner.attr("transform", translation(margin.left, margin.top));
        }

        /**
         * Render all the axes based on the current width and height.
         */
        function renderAxes() {
          svg
            .select(".chart__axis--x")
            .attr("transform", translation(0, chartH))
            .call(xAxis);

          svg.select(".chart__axis--y").call(yAxis);

          svg.select(".chart__axis--y--grid").call(yAxisGrid.tickSize(-chartW));
        }

        /**
         * Render all of the barGroups and bars.
         */
        function renderBars() {
          // Calculating the x, y, width and height of a bar:
          var barX = function(d, i) { return xScale(d.data.label); };
          var barY = function(d) { return yScale(d[1]); };
          var barW = xScale.bandwidth();
          var barH = function(d) { return yScale(d[0]) - yScale(d[1]); };

          // bars are grouped into barGroups, one per kind/color.
          // All barGroups are within the barGroupsContainer.

          // ENTER
          var barGroups = barGroupsContainer
            .selectAll(".chart__bargroup")
            .data(seriesData);

          // ENTER + UPDATE
          barGroups = barGroups
            .enter().append("g")
              .merge(barGroups)
              .attr("class", function(d, i) {
                return "chart__bargroup chart__bargroup--" + i;
              })

          var bars = barGroups
            .selectAll("rect")
            .data(function(d) { return d; });

          // ENTER
          bars
            .enter().append("rect")
              .attr("x", barX)
              .attr("y", barY)
              .attr("width", barW)
              .attr("height", barH)
              .classed("chart__bar", true)
              .classed("chart__bar--clickable", function(d, i) {
                // Get the name of the group this rect is in:
                var groupKey = d3.select(this.parentNode).datum().key;
                if ("url" in d.data.columns[groupKey] && d.data.columns[groupKey]["url"]) {
                  return true;
                } else {
                  return false;
                }
              })
              .style("opacity", function(d, i) {
                // If the bar is for the current year, make its opacity
                // in proportion to how far through the year we are.
                var currentYear = new Date().getFullYear();
                if (parseInt(d.data.label) == currentYear) {
                  return dayOfYear() / 366;
                } else {
                  return 1;
                }
              })
              .on("mouseover", onMouseover)
              .on("mousemove", onMousemove)
              .on("mouseout", onMouseout)
              .on("click", onClick);

          // UPDATE
          bars
            .transition()
            .attr("x", barX)
            .attr("y", barY)
            .attr("width", barW)
            .attr("height", barH);

          // EXIT
          bars.exit().remove();
        }

        /**
         * Utility function to save manually writing translate().
         */
        function translation(x, y) {
          return "translate(" + x + "," + y + ")";
        }

        /**
         * Utility function to return the day of the year, as a number
         * from 1-366.
         * From https://stackoverflow.com/a/8619946/250962
         */
        function dayOfYear() {
          var now = new Date();
          var start = new Date(now.getFullYear(), 0, 0);
          var diff = now - start;
          var oneDay = 1000 * 60 * 60 * 24;
          var day = Math.floor(diff / oneDay);
          return day;
        }

      });
    }

    chart.margin = function(value) {
      if (!arguments.length) return margin;
      margin = value;
      return chart;
    };

    chart.numberFormatPrefix = function(value) {
      if (!arguments.length) return numberFormatPrefix;
      numberFormatPrefix = value;
      return chart;
    };

    chart.numberFormatSuffix = function(value) {
      if (!arguments.length) return numberFormatSuffix;
      numberFormatSuffix = value;
      return chart;
    };

    chart.tooltipFormat = function(value) {
      if (!arguments.length) return tooltipFormat;
      tooltipFormat = value;
      return chart;
    };

    return chart;
  };
})();

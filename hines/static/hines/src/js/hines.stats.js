;(function() {
  'use strict';

  window.hines = window.hines || {};

  window.hines.chart = function(selection) {

    /**
     * Can be changed using the chart.kind() method.
     */
    var kind = 'bar';

    /**
     * Can be changed using the chart.margin() method.
     */
    var margin = {top: 5, bottom: 30, left: 50, right: 10};

    /**
     * Can be changed using the chart.tooltipFormat() method.
     */
    var tooltipFormat = function(d) {
      return '<strong>' + d.label + ':</strong> ' + d.value;
    };

    // Internal things that can't be overridden:

    var yAxisTickFormat = function(d){
      // Adds a comma to numbers of 5 or more digits.
      if ((''+d3.format('.0f')(d)).length > 4) {
        return d3.format(',')(d);
      } else {
        return d3.format('d')(d);
      };
    };
    var xScale = d3.scaleBand();
    var yScale = d3.scaleLinear();
    var xAxis = d3.axisBottom(xScale)
                  .tickSize(0)
                  .tickPadding(6);
    var yAxis = d3.axisLeft(yScale)
                    .ticks(5)
                    .tickSize(0)
                    .tickPadding(6)
                    .tickFormat(yAxisTickFormat);
    // The horizontal lines:
    var yAxisGrid = d3.axisLeft(yScale)
                      .ticks(5)
                      .tickFormat('');
    var barPadding = 0.1;
    // The tooltip that appears when hovering over a bar or span.
    var tooltip = d3.select('body')
                    .append('div')
                    .classed('chart-tooltip', true);

    function chart(selection) {

      selection.each(function(data) {

        var container = d3.select(this);

        var svg = container.append('svg');

        var inner = svg.append('g').classed('chart__inner', true);

        // Set up axes.
        inner.append("g")
              .classed("chart__axis chart__axis--x", true);

        inner.append("g")
              .classed("chart__axis chart__axis--y", true);

        inner.append("g")
              .classed("chart__axis chart__axis--y--grid", true);

        // Need to be in a scope available to all the render methods.
        var chartW;
        var chartH;

        /**
         * Sets scales/domains, renders axes and chart contents.
         * For the first time or on window resize.
         */
        function render() {
          setDomains();
          renderScales();
          renderAxes();
          renderBars();
        };

        /**
         * Set the values for the domain based on the current data.
         */
        function setDomains() {
          xScale.domain(data.map(function(d) { return d.label; }));
          yScale.domain([0, d3.max(data, function(d) { return d.value; })]);
        };

        /**
         * Calculates the scales and sets the size of the chart.
         */
        function renderScales() {
          // Outer width, including space for axes etc:
          var width  = parseInt(container.style('width'), 10),
              height = parseInt(container.style('height'), 10);

          // Inner width, chart area only, minus margins for axes etc.
          chartW = width - margin.left - margin.right;
          chartH = height - margin.top - margin.bottom;

          // Set the scales for these dimensions.
          xScale.range([0, chartW]).padding(barPadding);

          yScale.rangeRound([chartH, 0]);

          // Update outer dimensions.
          svg.transition().attr('width', width)
                          .attr('height', height);

          inner.attr("transform", translation(margin.left, margin.top));
        };

        function renderAxes() {

          svg.select('.chart__axis--x')
              .attr('transform', translation(0, chartH))
              .call(xAxis);

          svg.select('.chart__axis--y')
              .call(yAxis);

          svg.select('.chart__axis--y--grid')
              .call(yAxisGrid.tickSize(-chartW));
        };

        function renderBars() {
          // Calculating the x, y, width and height of a bar:
          var barX = function(d) { return xScale(d.label); },
              barY = function(d) { return yScale(d.value); },
              barW = xScale.bandwidth(),
              barH = function(d) { return chartH - yScale(d.value); };

          var bars = inner.selectAll('.chart__bar').data(data);

          bars.enter()
              .append("rect")
              .classed('chart__bar', true)
              .classed('chart__bar--clickable', function(d, i) {
                if ('url' in d && d['url']) {
                  return true;
                } else {
                  return false;
                };
              })
              // Not sure why these 4 lines have to be here as well as below:
              .attr("x", barX)
              .attr("y", barY)
              .attr("width", barW)
              .attr("height", barH)
              .on('mouseover', function(d, i) {
                tooltip.html( tooltipFormat(d) );
                tooltip.style('visibility', 'visible');
              })
              .on('mousemove', function() {
                tooltip
                  .style('top', (event.pageY-10)+'px')
                  .style('left',(event.pageX+15)+'px');
              })
              .on('mouseout', function() {
                tooltip.style('visibility', 'hidden');
              })
              .on('click', function(d, i) {
                if ('url' in d && d['url']) {
                  window.location.href = d['url'];
                } else {
                  return false;
                };
              });

          // Remove un-wanted bars.
          bars.exit().remove();

          // Update bar position, width and height.
          bars.transition()
              .attr("x", barX)
              .attr("y", barY)
              .attr("width", barW)
              .attr("height", barH);
        };

        /**
         * Utility function to save manually writing translate().
         */
        function translation(x,y) {
          return 'translate(' + x + ',' + y + ')';
        };

        render();

        window.addEventListener('resize', render);
      });

    };

    chart.margin = function(value) {
      if (!arguments.length) return margin;
      margin = value;
      return chart;
    };

    /**
     * Could be 'bar'.
     */
    chart.kind = function(value) {
      if (!arguments.length) return kind;
      kind = value;
      // if (typeof render === 'function') render();
      return chart;
    };

    chart.tooltipFormat = function(value) {
      if (!arguments.length) return tooltipFormat;
      tooltipFormat = value;
      return chart;
    };

    return chart;
  };

}());

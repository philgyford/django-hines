;(function() {
  'use strict';
  window.pop = window.pop || {};

  pop.pyramidChart = function(selection) {

    // Can be changed using the chart.margin() method.
    // Note extra 'middle', which is space in the center for the y-axis labels.
    var margin = {top: 0, right: 10, bottom: 20, left: 10, middle: 28};

    // Can (and should) be changed using the chart.data() method.
    // This will be replaced by any data passed to the chart.data() method:
    var data = [];

    // This will be replaced by a method when a chart is created.
    var render;

    // How many ticks do we suggest to d3 for the x-axes for different chart widths?
    var xAxisTicksWide = 8;
    var xAxisTicksNarrow = 4;

    // Internal things that can't be overridden:
    var xScale = d3.scaleLinear(),
        xScaleL = d3.scaleLinear(),
        xScaleR = d3.scaleLinear(),
        yScale = d3.scaleBand(),
        xAxisL = d3.axisBottom(xScaleL)
                    .tickFormat(d3.format('.0%')),
        xAxisR = d3.axisBottom(xScaleR)
                    .tickFormat(d3.format('.0%')),
        yAxisL = d3.axisRight(yScale)
                    .tickSize(0)
                    .tickPadding(margin.middle),
        yAxisR = d3.axisLeft(yScale)
                    .tickSize(0)
                    .tickFormat('');

    var tooltipFormat = function(value, percent) {
      var numFormat = d3.format(',');
      var percentFormat = d3.format(".1f");
      return '<strong>' + percentFormat(percent) + '%</strong> (' + numFormat(value) + ')';
    };

    var tooltip = d3.select('.chart__tooltip')

    if (tooltip.empty()) {
        tooltip = d3.select('body')
                    .append('div')
                    .classed('chart__tooltip', true);
    };

    // Will be the total counts for each side.
    // Need to be in the same scope as percentageL/R.
    var totalL;
    var totalR;

    // Functions for getting a value as a percentage of the sides' total.
    var percentageL = function(d) { return d / totalL; };
    var percentageR = function(d) { return d / totalR; };

    var makeLeftGridlines = function() { return d3.axisBottom(xScaleL); }
    var makeRightGridlines = function() { return d3.axisBottom(xScaleR); }

    function chart(selection) {
      selection.each(function() {

        // Create the elements for the chart.

        var container = d3.select(this);

        var svg = container.append('svg');
        var inner = svg.append('g').classed('chart__inner', true);

        // Set up axes.
        inner.append("g")
              .classed("axis axis--x axis--left", true);

        inner.append("g")
              .classed("axis axis--x axis--right", true);

        inner.append("g")
              .classed("axis axis--y axis--left", true);

        inner.append("g")
              .classed("axis axis--y axis--right", true);

        inner.append('g')
              .classed('grid grid--left', true);

        inner.append('g')
              .classed('grid grid--right', true);

        // Groups that will contain the bars on each side.
        var leftGroup = inner.append('g');
        var rightGroup = inner.append('g');

        // Need to be in a scope available to all the render methods.
        var chartW,
            chartH,
            sideW,
            xLeft0,
            xRight0,
            // What happens when cursor moves into, over or out of a bar.
            mouseOver = function(side, d) {
              var value,
                  percent;
              if (side == 'left') {
                value = d.left;
                percent = percentageL(value) * 100;
              } else {
                value = d.right;
                percent = percentageR(value) * 100;
              };
              tooltip.html( tooltipFormat(value, percent) );
              tooltip.style('visibility', 'visible');
            },
            mouseMove = function(){
                tooltip
                    .style('top', (event.pageY+10)+'px')
                    .style('left',(event.pageX+10)+'px');
            },
            mouseOut = function(){
                tooltip.style('visibility', 'hidden');
            };

        /**
         * Sets scales/domains, renders axes and chart contents.
         * For the first time or on window resize.
         */
        render = function() {
          setDomains();
          renderScales();
          renderAxes();
          renderBars();
        };

        /**
         * Set the values for the domains based on the current data.
         */
        function setDomains() {
          // Total values of all data on each side.
          // Used to calculage the percentages.
          totalL = d3.sum(data, function(d) { return d.left; });
          totalR = d3.sum(data, function(d) { return d.right; });

          // The highest x value on either side:
          var maxXValue = Math.max(
            d3.max(data, function(d) { return percentageL(d.left); }),
            d3.max(data, function(d) { return percentageR(d.right); })
          );

          // Set up scale domains.
          xScale.domain([0, maxXValue]);
          xScaleL.domain([0, maxXValue]);
          xScaleR.domain([0, maxXValue]);
          yScale.domain(data.map(function(d) { return d.band; }));
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

          // The width of each side of the chart:
          sideW = (chartW / 2) - margin.middle;

          // Where the 0 is on each side's x-axis:
          xLeft0 = sideW;
          xRight0 = chartW - sideW;

          // Set the scales for these dimensions.
          xScale.rangeRound([0, sideW]);
          xScaleL.rangeRound([sideW, 0]);
          xScaleR.rangeRound([0, sideW]);
          yScale.rangeRound([chartH, 0]).padding(0.1);

          // Update outer dimensions.
          svg.transition().attr('width', width)
                          .attr('height', height);

          inner.attr("transform", translation(margin.left, margin.top));
        };

        function renderAxes() {

          // Reverse scale on the left-hand side:
          xAxisL.scale( xScale.copy().range([xLeft0, 0]) );

          xAxisR.scale(xScale);

          // Set the number of x-axis ticks depending on width available:
          if (chartW > 500) {
            xAxisL.ticks(xAxisTicksWide);
            xAxisR.ticks(xAxisTicksWide);
          } else {
            xAxisL.ticks(xAxisTicksNarrow);
            xAxisR.ticks(xAxisTicksNarrow);
          };

          svg.select('.axis--x.axis--left')
              .attr('transform', translation(0, chartH))
              .call(xAxisL);

          svg.select('.axis--x.axis--right')
              .attr('transform', translation(xRight0, chartH))
              .call(xAxisR);

          svg.select('.axis--y.axis--left')
              .attr('transform', translation(xLeft0, 0))
              .call(yAxisL)
              .selectAll('text')
              .style('text-anchor', 'middle');

          svg.select('.axis--y.axis--right')
              .attr('transform', translation(xRight0, 0))
              .call(yAxisR);

          svg.select('.grid--left')
                .attr('transform', translation(0, chartH))
                .call(makeLeftGridlines()
                      .tickSize(-chartH)
                      .tickFormat('')
                );

          svg.select('.grid--right')
                .attr('transform', translation(xRight0, chartH))
                .call(makeRightGridlines()
                      .tickSize(-chartH)
                      .tickFormat('')
                );

        };

        function renderBars() {

          // Set positions of the left and right groups, that contain the bars.
          // Left has its scale inverted so the bars go from the centre to left.
          leftGroup.attr('transform', translation(xLeft0, 0) + 'scale(-1,1)');
          rightGroup.attr('transform', translation(xRight0, 0));

          // x, y and height are the same for bars on both sides:
          var barX = 0;
          var barY = function(d) { return yScale(d.band); };
          var barH = yScale.bandwidth();

          // Calculating the width of each bar on left and right:
          var barLW = function(d) { return xScale(percentageL(d.left)); };
          var barRW = function(d) { return xScale(percentageR(d.right)); };

          // Select bars on the left:
          var barsL = leftGroup.selectAll('.chart__bar--left')
                               .data(data);

          barsL.enter()
            .append('rect')
              .attr('class', 'chart__bar chart__bar--left')
              .attr('x', barX)
              .attr('y', barY)
              .attr('width', barLW)
              .attr('height', barH)
              .on('mouseover', function(d) { return mouseOver('left', d); })
              .on('mousemove', mouseMove)
              .on('mouseout', mouseOut);

          barsL.exit().remove();

          barsL.transition()
              .attr('x', barX)
              .attr('y', barY)
              .attr('width', barLW)
              .attr('height', barH);

          // Now the same for the bars on the right.

          var barsR = rightGroup.selectAll('.chart__bar--right')
                                .data(data)

          barsR.enter()
            .append('rect')
              .attr('class', 'chart__bar chart__bar--right')
              .attr('x', barX)
              .attr('y', barY)
              .attr('width', barRW)
              .attr('height', barH)
              .on('mouseover', function(d) { return mouseOver('right', d); })
              .on('mousemove', mouseMove)
              .on('mouseout', mouseOut);

          barsR.exit().remove();

          barsR.transition()
              .attr('x', barX)
              .attr('y', barY)
              .attr('width', barRW)
              .attr('height', barH);

        };

        /**
         * Utility function to save manually writing translate().
         */
        function translation(x,y) {
          return 'translate(' + x + ',' + y + ')';
        }

        render();

        window.addEventListener('resize', render);
      });

    };

    /**
     * Each of the methods below can be used to set variables and data both
     * before the chart is rendered, and afterwards, in order to update it.
     * Initially the `render` variable is undefined, so it's not called.
     * After the chart object has been call()ed, then `render` is a method.
     * So subsequent calls to, say, chart.data() will call render() once
     * the update data value has been set, re-rendering the chart.
     */

    chart.margin = function(value) {
      if (!arguments.length) return margin;
      margin = value;
      if (typeof render === 'function') render();
      return chart;
    };

    chart.data = function(value) {
      if (!arguments.length) return data;
      data = value;
      if (typeof render === 'function') render();
      return chart;
    };

    return chart;
  };

}());

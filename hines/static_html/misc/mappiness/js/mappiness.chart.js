/**
 * The top, main chart is referred to by `focus`.
 * The bottom, brush chart is referred to by `context`.
 */
define(['d3', './mappiness.templates'],
function(d3,     mappiness_templates) {
  return function(){
    var dispatch = d3.dispatch('tooltipOn', 'tooltipOff'),
        templates = mappiness_templates().templates(),

        // Total width and height for both charts:
        width = 960,
        height = 350,
        margin = {top: 10, right: 10, bottom: 20, left: 30},

        focusMargin,
        focusWidth,
        focusHeight,
        contextMargin,
        contextWidth,
        contextHeight,

        // Elements that will be defined later:
        svg,
        focusG,
        focusAxesG,
        contextG,
        contextAxesG,
        brush,
        tooltip,

        xValue = function(d) { return d[0]; },
        yValue = function(d) { return d[1]; },

        focusXScale = d3.time.scale(),
        contextXScale = d3.time.scale(),
        focusYScale = d3.scale.linear(),
        contextYScale = d3.scale.linear(),

        dateFormat = d3.time.format('%-d %b %Y'),
        ratingFormat = function(d) { return d * 100; },
        focusXAxis = d3.svg.axis()
                          .scale(focusXScale)
                          .orient('bottom'),
                          //.tickFormat(dateFormat),
                          //.ticks(d3.time.years, 5),
        contextXAxis = d3.svg.axis()
                          .scale(contextXScale)
                          .orient('bottom'),
        focusYAxis = d3.svg.axis()
                            .scale(focusYScale)
                            .orient('left')
                            .tickFormat(ratingFormat),
        contextYAxis = d3.svg.axis()
                            .scale(contextYScale)
                            .orient('left'),
        
        contextLine = d3.svg.line().x(X).y(contextY),
        focusLine = d3.svg.line().x(X).y(focusY);

    function exports(_selection) {
      _selection.each(function(data) {

        // We might get lines that have no datapoints, due to the constraints
        // the user has applied. We remove them or else we'll get errors
        // when trying to plot them.
        data = data.filter(function(d){ return d.values.length > 0; });

        // Select svg element if it exists.
        svg = d3.select(this)
                  .selectAll('svg')
                    .data([data]);

        createMain();

        if (brush !== undefined) {
          // Original extent of brush, if any.
          var brushExtent = brush.extent();
        };

        updateScales(data);

        renderAxes();

        renderBrush();

        if (! brush.empty()) {
          // If the brush was in use, then set focus x domain and brush extent
          // back to what they were.
          focusXScale.domain(brushExtent);
          brush.extent(brushExtent);
        };
      
        setBrushAndLines();
      });
    };

    /**
     * We have to check the brush before we draw the focus chart's lines.
     * Purely because if we add or remove a line, it might change the x-domain,
     * and this could mean that if there's a brush, it might be partially or
     * entirely off either end of the context chart.
     */
    function setBrushAndLines() {
      if (! brush.empty()) {
        var brushExtent = brush.extent();
        var xDomain = contextXScale.domain();

        if (brushExtent[0] > xDomain[1]
            ||
            brushExtent[1] < xDomain[0]
            ) {
          // Things have changed so much the brush is now entirely off either
          // the left- or right-hand edge of the context chart.
          // So remove it.
          brush.clear();
        } else if (brushExtent[1] > xDomain[1]) {
          // Right-hand edge of brush is off right-hand edge of context chart.
          brush.extent([brushExtent[0], xDomain[1]]);
        } else if (brushExtent[0] < xDomain[0]) {
          // Left-hand edge of brush is off left-hand edge of context chart.
          brush.extent([xDomain[0], brushExtent[1]]);
        };
      };

      // Ensures brush remains spanning the same dates if the domain has
      // changed.
      contextG.select('.x.brush').call(brush);
      brushed();

      renderLines('focus');

      renderTooltips();
    };


    function createMain() {
      setDimensions();

      // Create skeletal chart, with no data applied.
      focusG = svg.enter()
                    .append('svg')
                      .append('g')
                        .attr('class', 'focus');

      focusAxesG = focusG.append('g')
                        .attr('class', 'axes');

      if ( ! contextG) {
        // In an ideal world I would understand why we have to make sure
        // contextG isn't already defined. But I've spent an hour or two on
        // this and I'm still no wiser.
        // Without that we get an extra g.context whenever we duplicate a line.
        contextG = svg.append('g')
                          .attr('class', 'context');
        contextAxesG = contextG.append('g')
                          .attr('class', 'axes');
      };

      // If g.focus already exists, we need to explicitly select it:
      focusG = svg.select('g.focus');
      contextG = svg.select('g.context');

      // Update outer and inner dimensions.
      svg.transition().attr({ width: width, height: height });

      // When we add `clip-path:url(#clip)` to the lines in the main chart,
      // this stops them extending beyond the chart area.
      var clip = focusG.select('#clip');
      // Stops us adding extra #clips when we update the chart:
      if (clip.empty()) {
        focusG.append('clipPath')
                .attr('id', 'clip')
                .append('rect')
                  .attr('width', focusWidth)
                  .attr('height', focusHeight);
      };

      focusG.attr('transform',
                  'translate(' + focusMargin.left +','+ focusMargin.top + ')');
      contextG.attr('transform',
                'translate(' + contextMargin.left +','+ contextMargin.top + ')');

      // Make the tooltip div, but hidden.
      if ( ! tooltip) {
        tooltip = d3.select('body').append('div')
                      .attr('class', 'tooltip')
                      .style('left', '-10000px');
      };
    };


    function updateScales(data) {

      //if (brush == undefined || brush.empty()) {
        // Get min and max of all the start times for all the lines.
        
        if (data.length == 0) {
          // If we have no data (probably because none of the lines have
          // constraints which generate any datapoints) we need to fake
          // a domain so we don't get errors.
          // So we go from 1 year ago to today.
          var to = new Date(),
              from = new Date();
          from.setFullYear(from.getFullYear() - 1);
          focusXScale.domain([from, to]);
          contextXScale.domain([from, to]);

        } else {
          // Standard: Use the min and max dates from all the lines.

          focusXScale.domain([
            d3.min(data, function(line) {
              return d3.min(line.values, function(response) {
                return response.start_time;
              })
            }),
            d3.max(data, function(line) {
              return d3.max(line.values, function(response) {
                return response.start_time;
              })
            })
          ]);

          contextXScale.domain(focusXScale.domain());
        };


        focusXScale.range([0, focusWidth]);
        contextXScale.range([0, contextWidth]);

        focusYScale.domain([0, 1]).range([focusHeight, 0]);

        contextYScale.domain(focusYScale.domain()).range([contextHeight, 0]);
      //};
    };


    function setDimensions() {
      focusMargin = {top: margin.top, right: margin.right,
                        bottom: 100, left: margin.left};

      // Width and height of main, focus chart area, not including axes.
      focusWidth = width - focusMargin.left - focusMargin.right;
      focusHeight = height - focusMargin.top - focusMargin.bottom;

      contextMargin = {top: focusHeight + 40, right: focusMargin.right,
                        bottom: margin.bottom, left: focusMargin.left};

      // Width and height of small, context chart area, not including axes.
      contextWidth = width - contextMargin.left - contextMargin.right;
      contextHeight = height - contextMargin.top - contextMargin.bottom;
    };


    function renderAxes() {
      renderFocusXAxis();
      renderFocusYAxis();
      renderContextXAxis();
      renderFocusGrid();
    };


    function renderFocusXAxis() {
      focusAxesG.append('g')
              .attr('class', 'x axis');

      focusG.select('.x.axis')
              .attr('transform', 'translate(0,' + focusYScale.range()[0] + ')')
              .call(focusXAxis);
    };


    function renderFocusYAxis() {
      focusAxesG.append('g')
              .attr('class', 'y axis');
      focusG.select('.y.axis')
              .call(focusYAxis);
    };


    function renderContextXAxis() {
      contextAxesG.append('g')
              .attr('class', 'x axis');

      contextG.select('.x.axis')
              .attr('transform', 'translate(0,' + contextYScale.range()[0] + ')')
              .call(contextXAxis);
    };

    /**
     * Adds horizontal lines half-way up chart and at top.
     */
    function renderFocusGrid() {
      focusAxesG.selectAll('path.line.grid')
                  .data([
                          [
                            [focusXScale.domain()[0], 0.5],
                            [focusXScale.domain()[1], 0.5]
                          ],
                          [
                            [focusXScale.domain()[0], 1.0],
                            [focusXScale.domain()[1], 1.0] 
                          ]
                        ])
                  .enter().append('path')
                    .attr('class', 'line grid')
                    .attr('d', d3.svg.line()
                                      .x(function(d){return focusXScale(d[0]); })
                                      .y(function(d){return focusYScale(d[1]); })
                                    );
    };

    /**
     * Draw each of the lines, on either of the charts.
     * `chart` is either 'focus' or 'context'.
     */
    function renderLines(chart) {

      // Each chart has its own element that we draw in, and its own line object.
      if (chart == 'context') {
        var chartEl = contextG;
        var chartLine = contextLine;
      } else {
        var chartEl = focusG;
        var chartLine = focusLine;
      };

      var line = chartEl.selectAll('path.line.feeling')
                        .data(function(d) { return d; },
                              function(d) { return d.id; });

      line.enter().append('path')
            .attr('class', 'line feeling')
            .attr('id', function(d) { return lineCSSID(d.id, chart); })
            .style('stroke', function(d) { return d.color; });

      line.data(function(d) { return d; })
          .transition()
          .attr('d', function(d) { return chartLine(d.values); });

      // Remove any currently-drawn lines that no longer exist in the data.
      line.exit().remove();
    };

    /**
     * Most of the stuff for drawing the context/brush chart.
     */
    function renderBrush() {
      // So that we don't draw another brush when updating an existing chart:
      if (d3.select('g.brush').empty()) {

        brush = d3.svg.brush().x(contextXScale)
                              .on('brush', brushed);
                            
        renderLines('context');

        contextG.append('g')
          .attr('class', 'x brush')
          .call(brush)
        .selectAll('rect')
          .attr('y', -6)
          .attr('height', contextHeight + 6);
      } else {
        renderLines('context');
      };
    };

    /**
     * What happens when the brush in the context area is moved / changed.
     */
    function brushed() {
      focusXScale.domain(brush.empty() ? contextXScale.domain() : brush.extent());

      // Redraw lines.
      focusG.selectAll('path.line.feeling')
                .attr('d', function(d) { return focusLine(d.values); });

      // Redraw x-axis.
      focusG.select(".x.axis").call(focusXAxis);

      // Move the dots on the points.
      focusG.selectAll('.dot')
              .attr('cx', function(d) { return X(d); })
              .attr('cy', function(d) { return focusY(d); });
    };


    /**
     * Draws the invisible circles on each point which, when hovered over,
     * show the tooltip with info about that point.
     */
    function renderTooltips() {
      // Add a container for each line to hold all of its dots.
      var dotsG = focusG.selectAll('g.dots')
                          .data(function(d) { return d; },
                                function(d) { return d.id; });

      dotsG.enter().append('g')
                          .attr('class', 'dots')
                          .attr('id', function(d) { return 'dots-'+d.id; });

      dotsG.exit().remove();

      // Within each container, add a dot for every point on the line.
      var dots = dotsG.selectAll('.dot')
                          .data(function(d) { return d.values; });

      dots.enter().append('circle')
                    .attr('class', 'dot');

      dots.data(function(d) { return d.values; },
                function(d) { return d.start_time; })
            .attr('r', 5)
            .on('mouseover', function(d) {
              // Sends an event the controller can here, if needed.
              dispatch.tooltipOn(d);
              tooltipOn(d);
            })
            .on('mouseout', function(d) {
              // Sends an event the controller can here, if needed.
              dispatch.tooltipOff(d);
              tooltipOff(d);
            })
            .transition()
            .attr('cx', function(d) { return X(d); })
            .attr('cy', function(d) { return focusY(d); });

      dots.exit().remove();
    };

    /**
     * Called when the user hovers over one of the invisible circles on
     * a point.
     */
    function tooltipOn(d) {
      tooltip.html(tooltipContent(d));

      var tooltipWidth = parseInt(tooltip.style('width'), 10);
      var tooltipHeight = parseInt(tooltip.style('height'), 10);
      var windowWidth = window.innerWidth;
      var windowHeight = window.innerHeight;

      // Default positions, a bit to the right of the cursor:
      var left = d3.event.pageX + 12;
      var top = d3.event.pageY - 4;

      // -30 so it's not right up against edge, and more to allow for scrollbar
      if ((d3.event.pageX + tooltipWidth) > (windowWidth - 30)) {
        // Tooltip would extend off the right edge of page, so put it on the
        // left of the cursor.
        left = d3.event.pageX - tooltipWidth - 12;
      };
      if ((d3.event.pageY + tooltipHeight) > windowHeight) {
        // Tooltip would extend off the bottom of page, so move it up so it
        // stays on.
        top = d3.event.pageY - (d3.event.pageY + (tooltipHeight - windowHeight)) - 4;
      };

      tooltip.style('left', left + 'px')     
              .style('top', top + 'px');    
    };

    /**
     * Called when the user hovers out of one of the circles.
     */
    function tooltipOff(d) {
      tooltip.style('left', '-10000px');
    };

    /**
     * Generates the content for an individual tooltip.
     * The HTML is in mappiness.templates.
     */
    function tooltipContent(d) {
      // https://github.com/mbostock/d3/wiki/Time-Formatting
      var formatTime = d3.time.format('%H:%M %a %e %b %Y');

      // Go from 0.082341 to 8.
      var formatFeeling = function(f) {
        return Math.round(f*100);
      };

      var tooltipData = {
        start_time: formatTime(d.start_time),
        happy:   formatFeeling(d.happy),
        relaxed: formatFeeling(d.relaxed),
        awake:   formatFeeling(d.awake),
        in_out:    MAPPINESS_DATA_DICTIONARY.in_out[d.in_out],
        home_work: MAPPINESS_DATA_DICTIONARY.home_work[d.home_work],
        people: [],
        activities: [],
        notes: ('notes' in d && d.notes != null) ? d.notes : ''
      };

      d3.keys(MAPPINESS_DATA_DICTIONARY.people).forEach(function(key) {
        if (d[key] == 1) {
          tooltipData.people.push(MAPPINESS_DATA_DICTIONARY.people[key]);
        };
      })
      if (tooltipData.people.length == 0) {
        tooltipData.people.push('Alone or with strangers only');
      };

      d3.keys(MAPPINESS_DATA_DICTIONARY.activities).forEach(function(key) {
        if (d[key] == 1) {
          tooltipData.activities.push(MAPPINESS_DATA_DICTIONARY.activities[key]);
        };
      });

      return templates.tooltip(tooltipData);
    };

    /**
     * Return the string used for a line's CSS ID.
     * id is the numeric ID of the line.
     * chart is 'context' or 'focus'.
     */
    function lineCSSID(id, chart) {
      return chart + '-' + id; 
    };

    function X(d) {
      return focusXScale(d.start_time);
    };

    function focusY(d) {
      return focusYScale(d.value);
    };
    function contextY(d) {
      return contextYScale(d.value);
    };

    /**
     * Make a line visible/invisible (in both context and focus charts).
     * line_id is the numeric ID of the line.
     */
    exports.toggleLine = function(line_id) {
      // Do it for each chart:
      ['context', 'focus'].forEach(function(chart) {
        var line_selector = 'path#' + lineCSSID(line_id, chart);

        if (d3.select(line_selector).style('opacity') == 0) {
          d3.select(line_selector).transition().style('opacity', 1);
        } else {
          d3.select(line_selector).transition().style('opacity', 0);
        };
      });
    };

    /**
     * Make a line visible (in both context and focus charts).
     * line_id is the numeric ID of the line.
     */
    exports.showLine = function(line_id) {
      ['context', 'focus'].forEach(function(chart) {
        var selector = 'path#' + lineCSSID(line_id, chart);
        d3.select(selector).transition().style('opacity', 1);
      });
    };

    exports.margin = function(_) {
      if (!arguments.length) return margin;
      margin = _;
      return this;
    };

    exports.width = function(_) {
      if (!arguments.length) return width;
      width = _;
      return this;
    };

    exports.height = function(_) {
      if (!arguments.length) return height;
      height = _;
      return this;
    };

    exports.x = function(_) {
      if (!arguments.length) return xValue;
      xValue = _;
      return chart;
    };

    exports.y = function(_) {
      if (!arguments.length) return yValue;
      yValue = _;
      return chart;
    };

    d3.rebind(exports, dispatch, "on");

    return exports;
  };
});


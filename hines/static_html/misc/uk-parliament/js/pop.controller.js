;(function() {
  'use strict';
  window.pop = window.pop || {};

  pop.controller = function() {

    var agesChartSelector = '.js-chart-ages';
    var gendersChartSelector = '.js-chart-genders';

    // Will be data about genders/ages for each kind of thing we're showing.
    var chartData = {};

    // Will be the chart functions.
    var agesChart;
    var gendersChart;

    // Initial chart display.
    var start = {
      'left': 'commons-all',
      'right': 'lords-all'
    };

    // Will look like start once we've rendered the chart:
    var current = {};

    // Load the data and render the initial chart.
    d3.json('data/chart.json').then(function(data) {
      createSelects(data);
      processChartData(data);
      updateCharts(start['left'], start['right']);
    });

    /**
     * Create the left and right select input fields.
     */
    function createSelects(data) {
      // Will be all the optgroups and their options:
      var optgroups = [
        {
          'name': 'United Kingdom',
          'options': [
            ['uk', 'Adult population']
          ]
        }
      ];

      // Optgroups with empty options:
      var commonsOptgroup = {
        'name': 'House of Commons',
        'options': []
      };
      var lordsOptgroup = {
        'name': 'House of Lords',
        'options': []
      };

      // Populate the optgroups' options:
      data['commons'].forEach(function(d, i) {
        commonsOptgroup['options'].push(
          [ 'commons-'+d['id'], d['name'] ]
        );
      });
      data['lords'].forEach(function(d, i) {
        lordsOptgroup['options'].push(
          [ 'lords-'+d['id'], d['name'] ]
        );
      });

      // Add the two optgroups into the full list:
      optgroups = optgroups.concat(commonsOptgroup);
      optgroups = optgroups.concat(lordsOptgroup);

      // Add options to the two select fields.
      ['left', 'right'].forEach(function(side, i) {
        d3.select('.choices-'+side)
            .on('change', onSelectChange)
          .selectAll('optgroup')
            .data(optgroups)
            .enter()
          .append('optgroup')
            .attr('label', function(d) { return d.name; })
          .selectAll('option')
            .data(function(d) { return d.options; })
            .enter()
          .append('option')
            .attr('value', function(d) { return d[0]; })
            .property('selected', function(d) { return d[0] === start[side]; })
            .text(function(d) { return d[1]; });
      });
    };

    /**
     * Put the data from chart.json into a format useful for the interface.
     * i.e. keyed by the values used in the select fields.
     * Populates chartData.
     */
    function processChartData(data) {

      for(var key in data) {
        if (key == 'uk') {
          chartData[key] = {
            'name': data[key]['name'],
            'genders': data[key]['genders'],
            'ages': data[key]['ages']
          };

        } else {
          data[key].forEach(function(d, i) {
            // So it'll be like 'commons-4':
            chartData[key + '-' + d['id']] = {
              'name': d['name'],
              'genders': d['genders'],
              'ages': d['ages']
            };
          });
        };
      };
    };

    /**
     * Looks at current values of the select fields and updates the chart.
     */
    function onSelectChange() {
      // Get which side and what chart to display:
      var select = d3.select(this);
      var clss = select.attr('class');
      var val = d3.select(this).property('value');

      if (clss == 'choices-left') {
        updateCharts(val, current['right']);
      } else {
        updateCharts(current['left'], val);
      };
    };

    /**
     * When the page is loaded, or when we choose something new for left/right,
     * do all the things that need to be done.
     */
    function updateCharts(left, right) {

      setLeftRightTitles(left, right);
      renderAgesChart(left, right);
      renderGendersChart(left, right);

      // So we know what's currently showing.
      current = {
        'left': left,
        'right': right
      };
    };

    function setLeftRightTitles(left, right) {
      var leftTitle = chartData[left]['name'];
      var rightTitle = chartData[right]['name'];

      if (left.indexOf('commons') === 0) {
        leftTitle = 'House of Commons: ' + leftTitle;
      } else if (left.indexOf('lords') === 0) {
        leftTitle = 'House of Lords: ' + leftTitle;
      };
      if (right.indexOf('commons') === 0) {
        rightTitle = 'House of Commons: ' + rightTitle;
      } else if (right.indexOf('lords') === 0) {
        rightTitle = 'House of Lords: ' + rightTitle;
      };

      d3.selectAll('.js-title-left').text(leftTitle);
      d3.selectAll('.js-title-right').text(rightTitle);
    };

    /**
     * Create or update the chart.
     * `left` and `right` are keys used in the object in chart.json.
     * e.g. 'commonsall' or 'uk'.
     * One will be displayed on each side of the chart.
     */
    function renderAgesChart(left, right) {
      var data = [];

      for (var band in chartData[left]['ages']) {
        // Assuming both left and right have the same age bands.
        // So each element will be like:
        // {'band': '18-19', 'left': 4, 'right': 12}

        data.push({
          'band': band,
          'left': chartData[left]['ages'][band],
          'right': chartData[right]['ages'][band],
        })
      };

      if (typeof agesChart === 'function') {
        // The chart already exists, so update with new data.
        agesChart.data(data);

      } else {
        // Chart doesn't exist yet, so create it.
        agesChart = pop.pyramidChart().data(data);
        d3.select(agesChartSelector).call(agesChart);
      };
    };

    function renderGendersChart(left, right) {
      var data = [
        {
          'band': 'Male',
          'left': chartData[left]['genders']['m'],
          'right': chartData[right]['genders']['m']
        },
        {
          'band': 'Female',
          'left': chartData[left]['genders']['f'],
          'right': chartData[right]['genders']['f']
        }
      ];

      if (typeof gendersChart === 'function') {
        // The chart already exists, so update with new data.
        gendersChart.data(data);

      } else {
        // Chart doesn't exist yet, so create it.
        gendersChart = pop.pyramidChart().data(data);
        d3.select(gendersChartSelector).call(gendersChart);
      };
    };

  };

}());

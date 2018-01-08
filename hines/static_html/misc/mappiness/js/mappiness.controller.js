/**
 */
define(['jquery', 'd3', './mappiness.chart', './mappiness.data_manager', './mappiness.ui'],
function($, d3, mappiness_chart, mappiness_dataManager, mappiness_ui) {
  return function(){
    var exports = {},
        container,
        data,
        // Each element will correspond to one line on the chart, containing
        // all its data.
        lines_data = [],
        chart       = mappiness_chart(),
        dataManager = mappiness_dataManager(),
        ui          = mappiness_ui();

    /**
     * Call this to kick things off.
     */
    exports.init = function(spec) {
      if (spec) {
        if ('lineColors' in spec) {
          dataManager.colorPool(spec.lineColors);
          ui.key.colorPool(spec.lineColors);
        };
        if ('dataDictionary' in spec) {
           dataManager.constraintsDescriptions(spec.dataDictionary);
           ui.editor.constraintsDescriptions(spec.dataDictionary);
        };
      };

      initListeners();

      getJSON();
    };


    /**
     * Gets the Mappiness JSON data and passes it to dataManager.
     * If there is a local `mappiness.json` file, we use that.
     * Otherwise, we fetch the remote one.
     */
    function getJSON() {
      $.ajax({
        url: 'mappiness.json',
        type: 'HEAD'
      })
      .fail(function() {
        ui.general.importFormShow();
      })
      .done(function() {
        dataManager.loadJSON('mappiness.json');
      });
    };


    /**
     * Does the initial generating of the chart, once we've loaded all the
     * data.
     */
    function drawChart() {
      ui.general.loaderHide();
      ui.general.importFormHide();
      $('#loaded').fadeIn(500);

      // Add one line to kick things off:
      lines_data.push(dataManager.getCleanedData({feeling: 'happy'}));

      // Could add other starter lines too, eg:
      // lines_data.push(dataManager.getCleanedData({feeling: 'awake',
      //                in_out: 'in', home_work: 'home', with_children: 1}));

      chart.width( $('#chart').width() );

      // We don't want to this change when the window's resized because it'll
      // mess up all the rows of keys.
      $('#key').width( $('#chart').width() );

      container = d3.select('#chart');

      updateChart();
    };
    
    /**
     * Updates the chart and key with whatever is now in lines_data.
     */
    function updateChart() {
      container.data([lines_data])
               .call(chart);

      ui.updateLines(lines_data);
    };

    /**
     * Makes a copy of the line's data and adds it to the end of line_data.
     * Doesn't automatically update the chart or key displays.
     */
    function duplicateLine(line_id) {
      for (var n = 0; n < lines_data.length; n++) {
        if (lines_data[n].id == line_id) {
          // Make a new set of data using the original constraints passed into
          // the line we want to duplicate:
          var new_line = dataManager.getCleanedData(
                                            lines_data[n].original_constraints);
          // Originally wanted to add it just after the line that's being
          // duplicated, but that's madness and gets complicated.
          lines_data.push(new_line);
          break;
        };
      };
    };


    /**
     * Remove's the line's data from line_data.
     * Doesn't automatically update the chart or key displays.
     */
    function deleteLine(line_id) {
      for (var n = 0; n < lines_data.length; n++) {
        if (lines_data[n].id == line_id) {
          dataManager.releaseColor(lines_data[n].color);
          lines_data.splice(n, 1);
          break;
        };
      };
    };


    /**
     * Will replace a line in lines_data with a new set of data.
     * Matched using the lines' IDs.
     */
    function replaceLine(newLineData) {
      for (var n in lines_data) {
        if (lines_data[n].id == newLineData.id) {
          lines_data[n] = newLineData;
          break;
        };
      };
    };


    /**
     * Various components send events when something happens that the
     * controller needs to act on. Start listening for them...
     */
    function initListeners() {

      dataManager.on('dataReady', function() {
        drawChart(); 
      });

      // We only expect this if fetching remote JSONP.
      dataManager.on('dataError', function(msgCode) {
        ui.general.importFormError(msgCode);
      });

      // Chart
      // We draw these tooltips in the chart object itself now,
      // but these hooks are here in case we want to do something in ui
      // instead.
      chart.on('tooltipOn', function(d) { });
      chart.on('tooltipOff', function(d) { });


      // Import form.

      ui.general.on('importSubmit', function(downloadCode) {
        if (downloadCode !== false) {
          dataManager.loadJSONP('https://mappiness.me/' + downloadCode + '/mappiness.json') 
        }; // Else the form will already be showing an error message.
      });

      // The user wants to try some random data.
      ui.general.on('importRandom', function() {
        dataManager.loadRandomJSON();
      });


      // The switches to turn each line on/off.
      ui.key.on('keyShowLine', function(line_id) {
        chart.toggleLine(line_id);
      });

      ui.key.on('keyDuplicateLine', function(line_id) {
        duplicateLine(line_id);
        updateChart();
      });

      ui.key.on('keyDeleteLine', function(line_id) {
        deleteLine(line_id);
        updateChart();
        // If there is now only one line left, ensure it's visible.
        if (lines_data.length == 1) {
          chart.showLine(lines_data[0].id);
        };
      });

      ui.key.on('keyEditLine', function(line_id) {
        ui.editor.open(line_id);
      });
      
      
      ui.editor.on('editorSubmit', function(formData) {
        var newLineData = dataManager.getCleanedData(
                                formData.constraints,
                                {id: formData.lineID, color: formData.color});
        ui.editor.close();

        replaceLine(newLineData);

        updateChart();
      });

    };

    return exports;
  };
});


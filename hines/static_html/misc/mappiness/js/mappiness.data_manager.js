/**
 * Fetches and cleans and filters the data from a Mappiness JSON file.
 *
 *
 * Usage:
 *
 * var dataManager = mappiness_dataManager();
 * dataManager.colorPool([ ...array of colors... ]);
 * dataManager.constraintsDescriptions( ...object of descriptios... );
 *
 * // Then EITHER:
 * dataManager.loadJSONP(' ...URL to .json file... ');
 * // OR:
 * dataManager.loadJSON(' ... path to local .json file... ');
 *
 * dataManager.on('dataReady', function() {
 *   // eg:
 *   var line_data = dataManager.getCleanedData({feeling: 'happy'});
 *   // Do something with the data.
 * });
 *
 * NOTE: jQuery is currently ONLY used in loadJSONP().
 */
define(['d3', './mappiness.data_generator', 'jquery'],
function(d3,     mappiness_dataGenerator,    $) {
  return function() {
    var exports = {},
        dispatch = d3.dispatch('dataReady', 'dataLoading', 'dataError'),
        dataGenerator = mappiness_dataGenerator(),
        data,
        // Should be set by constraintsDescriptions();
        constraintsDescriptions = {},
        colorPool = [ '#f00', '#0f0', '#00f' ],
        colorsInUse = [];


    /**
     * Loads data from a local JSON file.
     * Does the dataLoading event while data is loading.
     */
    exports.loadJSON = function(filepath) {

      var load = d3.json(filepath); 

      load.on('progress', function() { dispatch.dataLoading(d3.event.loaded); });

      load.get(function(error, response) {
        processJSON(response);
      });
    };


    /**
     * Loads data from a remote JSON file using JSONP.
     * We use jQuery for this because using the d3.jsonp plugin seemed to
     * require a callback in the global scope.
     *
     * Does NOT do the dataLoading event while data is loading.
     * (I can't figure out how to add a 'progress' event to $.ajax when loading
     * jsonp.)
     */
    exports.loadJSONP = function(url) {
      $.ajax({
        url: url,
        dataType: 'jsonp'
      })
      .fail(function(response){
        dispatch.dataError('ajax_error');
      })
      .done(function(json){
        if ('error' in json) {
          // json.error is probably 'bad_secret'.
          dispatch.dataError(json.error);
        } else {
          processJSON(json);
        };
      });
    };

    
    /**
     * Generates a randomised set of fake data, puts it in the `data` variable,
     * and signals that the data is ready.
     * Should be a drop-in random replacement for loadJSON() or loadJSONP().
     */
    exports.loadRandomJSON = function() {
      json = dataGenerator.getJSON();
    
      processJSON(json);
    };


    /**
     * `original_constraints` is undefined, or an object with one or more of these
     * keys:
     * 'feeling': One of 'happy', 'relaxed' or 'awake'.
     * [And/or any of the keys accepted by getFilteredData().]
     *
     * `existing_data` is undefined, or is an object like:
     *   {id: 1234567890, color: '#ff3300'}
     * These values will be used for the returned data.
     */
    exports.getCleanedData = function(original_constraints, existing_data) {
      var constraints = tidyConstraints(original_constraints);
      var values = getFilteredData(constraints);
      var color, id;

      if (typeof existing_data === 'undefined') {
        color = getNextColor();
        id = makeID();
      } else {
        color = existing_data.color;
        id = existing_data.id;
        values.forEach(function(d, i) {
          values[i].id = id;
        });
      };

      return {
        id: id,
        color: color,
        constraints: getInflatedConstraints(constraints),
        original_constraints: original_constraints,
        values: values
      };
    };


    /**
     * Call this to remove a color from the list of colors currently in use.
     * The color will then be available for newly-created lines.
     * color is one of the colors in colorPool and colorsInUse.
     * eg '#4D4D4D'.
     */
    exports.releaseColor = function(color) {
      if (colorsInUse.indexOf(color) >= 0) {
        colorsInUse.splice(colorsInUse.indexOf(color), 1);  
      }; 
    };

    /**
     * Returns the next available color (eg, '#4D4D4D') from colorPool.
     * Adds that color to colorsInUse so it is not available next time.
     * If all colors are already in use, returns '#000'.
     */
    var getNextColor = function() {
      for (n=0; n < colorPool.length; n++) {
        if (colorsInUse.indexOf(colorPool[n]) < 0) {
          var color = colorPool[n];
          colorsInUse.push(color);
          break;
        };
      };
      // All the colors in the pool have been used.
      if (color == undefined) {
        // Yes, it'd be nicer to do something better than this.
        color = '#000';
      };
      return color;
    };


    /**
     * Takes the Mappiness JSON file's contents (an array of objects) and
     * cleans it, puts it in the `data` variable, and sigals that the data is
     * ready.
     */
    var processJSON = function(json) {

      json.forEach(function(d) {
        cleanData(d);
      });

      data = json;

      dispatch.dataReady(json);
    };



    /**
     * Ensures the submitted constraints are the correct format and have any
     * required fields.
     */
    var tidyConstraints = function(constraints) {
      if (typeof constraints === 'undefined') {
        constraints = {};
      }
      // Set default.
      if ( ! 'feeling' in constraints) {
        constraints.feeling = 'happy';
      };

      return constraints;
    };


    /**
     * Returns an object containing the textual descriptions of all the
     * constraints supplied.
     *
     * If constraints is like:
     * {
     *  feeling: 'happy',
     *  in_out: 'in',
     *  home_work: 'work',
     *  do_work: 1,
     *  do_music: 0,
     *  with_peers: 1,
     *  notes: "Test"
     * }
     *
     * then the returned object will be like:
     * {
     *  feeling: {value: 'happy', description: 'Happy'},
     *  in_out: {value: 'in', description: 'Indoors'},
     *  home_work: {value: 'work', description: 'At work'},
     *  people: {
     *            with_peers: {value: 1, description: 'Colleagues, classmates'}
     *  },
     *  activities: {
     *                do_work: {value: 1, description: 'Working, studying'},
     *                do_music: {value: 0, description: 'Listening to music'}
     *              },
     *  notes: {value: 'Test', description: 'Test'}
     * }
     */
    var getInflatedConstraints = function(constraints) {
      // What we'll be returning.
      var new_constraints = {};

      if ('feeling' in constraints) {
        // Capitalize first letter. Thanks JavaScript.
        new_constraints.feeling = {
                        value: constraints.feeling,
                        description: constraints.feeling.charAt(0).toUpperCase()
                                        + constraints.feeling.slice(1)};
      };

      if ('in_out' in constraints) {
        new_constraints.in_out = {
              value: constraints.in_out,
              description: constraintsDescriptions.in_out[
                                                        constraints.in_out ]};
      };
      if ('home_work' in constraints) {
        new_constraints.home_work = {
              value: constraints.home_work,
              description: constraintsDescriptions.home_work[
                                                      constraints.home_work ]};
      };
      
      // Get the descriptions for any People constraints.
      var people = {};
      d3.keys(constraintsDescriptions.people).forEach(function(k) {
        if (k in constraints) {
          people[k] = {value: constraints[k],
                       description: constraintsDescriptions.people[k]};
        };
      });
      if (d3.keys(people).length > 0) {
        new_constraints.people = people; 
      };
    
      // Get the descriptions for any Activities constraints.
      var activities = {};
      d3.keys(constraintsDescriptions.activities).forEach(function(k) {
        if (k in constraints) {
          activities[k] = {value: constraints[k],
                           description: constraintsDescriptions.activities[k]};
        };
      });
      if (d3.keys(activities).length > 0) {
        new_constraints.activities = activities;
      };

      // Add notes.
      if ('notes' in constraints) {
        new_constraints.notes = {value: constraints.notes,
                                 description: constraints.notes};
      };

      return new_constraints;
    };


    /**
     * The same as getFeelingData() but omitting any data points that don't
     * match the supplied constraints.
     *
     * `constraints` should at least have a `feeling` attribute, being one of
     * 'happy', 'relaxed' or 'awake'.
     *
     * Additional, optional attributes:
     *
     * 'in_out': A string, one of 'in', 'out' or 'vehicle'.
     *
     * 'home_work': A string one of 'home', 'work' or 'other'.
     *
     * Any of the keys from constraintsDescriptions.people, set to either 1 or 0.
     *
     * Any of the keys from constraintsDescriptions.activities, set to 1 or 0.
     *
     * 'notes' can be a string which will be RegExp'd against the point's notes
     * field, ignoring case.
     */
    var getFilteredData = function(constraints) {

      var feeling_data = getFeelingData(constraints.feeling);

      if ('in_out' in constraints) {
        feeling_data = feeling_data.filter(function(d) {
          return constraints.in_out.indexOf(d.in_out) >= 0; 
        });
      };

      if ('home_work' in constraints) {
        feeling_data = feeling_data.filter(function(d) {
          return constraints.home_work.indexOf(d.home_work) >= 0; 
        });
      };

      d3.keys(constraintsDescriptions.people).forEach(function(people) {
         if (people in constraints) {
            feeling_data = feeling_data.filter(function(d) {
              return d[people] == constraints[people]; 
            });
         };
      });

      d3.keys(constraintsDescriptions.activities).forEach(function(activity) {
         if (activity in constraints) {
            feeling_data = feeling_data.filter(function(d) {
              if (activity == 'do_other') {
                // Special case: The data has do_other and do_other2 as possible
                // fields, but in our UI we conflate them into one 'do_other'
                // field.
                return d[activity] == constraints[activity] || d['do_other2'] == constraints[activity]; 
              } else {
                return d[activity] == constraints[activity]; 
              };
            });
         };
      });

      if ('notes' in constraints) {
        feeling_data = feeling_data.filter(function(d) {
          if (d.notes == null) {
            return false;
          } else {
            return d.notes.match(new RegExp(constraints.notes, 'i')) !== null;
          };
        });
      };

      return feeling_data;
    };


    /**
     * Returns a copy of data but with each object having these additional
     * atributes:
     *  `feeling` - whatever is passed in to this function.
     *  `value` - the numeric value for that feeling.
     *
     * eg, if a data element is like:
     *  {accuracy_m: 200, awake: 0.417671, ...}
     * and we pass 'awake' into getFeelingData, each data element in the returned
     * array will be more like:
     *  {accuracy_m: 200, awake: 0.417671, feeling: 'awake', value: 0.417671, ...}
     *  
     *
     * `feeling` must be one of 'happy', 'relaxed' or 'awake'.
     */
    var getFeelingData = function(feeling) {
      var feeling_data = [];

      data.forEach(function(d, n) {
        // Don't like having to use jQuery here, but seems simplest/best way
        // to clone an object?
        feeling_data[n] = $.extend({}, d);
        feeling_data[n]['feeling'] = feeling;
        feeling_data[n]['value'] = d[feeling];
      });

      return feeling_data; 
    };


    /**
     * Make the ID we use for a particular line.
     * Unique enough.
     */
    var makeID = function() {
      return Math.floor(Math.random() * 100000000000);
    };

    /**
     * Do any tidying up of the data we need.
     */
    var cleanData = function(d) {
      // Change the string date/times into Date objects.
      // Those times will be like "2013/07/21 15:12:58 +0100".
      // We did just do `new Date(d.start_time)` but that generated 'Invalid
      // Date' in IE10.
      var timeFormat = d3.time.format('%Y/%m/%d %H:%M:%S %Z');
      if (d.beep_time) {
        d.beep_time = timeFormat.parse(d.beep_time);
      } else {
        d.beep_time = null;
      };
      d.start_time = timeFormat.parse(d.start_time);
      return d;
    };

    exports.constraintsDescriptions = function(_) {
      if (!arguments.length) return constraintsDescriptions;
      constraintsDescriptions = _;
      return this;
    };

    exports.colorPool = function(_) {
      if (!arguments.length) return colorPool;
      colorPool = _;
      return this;
    };

    d3.rebind(exports, dispatch, 'on');

    return exports;
  };
});


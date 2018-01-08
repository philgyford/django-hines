/**
 * For drawing the keys showing information about lines on the chart.
 * Includes the duplicate/edit/delete/show controls.
 */
define(['jquery', 'd3', './mappiness.templates'],
function($,        d3,     mappiness_templates) {
  return function() {
    var exports = {},
        dispatch = d3.dispatch('keyShowLine', 'keyDuplicateLine',
                                'keyDeleteLine', 'keyEditLine'),
        templates = mappiness_templates().templates(),
        // Can be set with exports.colorPool().
        colorPool = ['#f00', '#0f0', '#00f'],
        lines = [];

    /**
     * I know this is the wrong place for this, but I don't know what the right
     * place is.
     *
     * changeElementType jQuery plugin.
     * Changes the type of an element and retains all its attributes.
     * eg: $('b').changeElementType('i');
     *
     * But if changing from an 'a' to anything else, changes the 'href'
     * attribute to 'data-link'. And if changing *to* an 'a' and 'data-link' is
     * present, change that to an 'href'. So as not to add href attributes to
     * non-anchors.
     */
    $.fn.changeElementType = function(newType) {
      var attrs = {};

      $.each(this[0].attributes, function(idx, attr) {
          attrs[attr.nodeName] = attr.nodeValue;
      });

      if (newType == 'a' && 'data-link' in attrs) {
        attrs['href'] = attrs['data-link'];
        delete attrs['data-link'];
      } else if ('href' in attrs) {
        attrs['data-link'] = attrs['href'];
        delete attrs['href'];
      };

      this.replaceWith(function() {
          return $("<" + newType + "/>", attrs).append($(this).contents());
      });
    };

    initListeners();

    /**
     * Listens for jQuery events and turns them into events that the controller
     * listens for.
     */
    function initListeners() {
      $('#key').on('click', '.key-show-control', function(ev) {
        dispatch.keyShowLine($(this).data('line-id'));
      });

      $('#key').on('click', 'a.key-duplicate-control', function(ev) {
        ev.preventDefault();
        dispatch.keyDuplicateLine($(this).data('line-id'));
      });

      $('#key').on('click', 'a.key-delete-control', function(ev) {
        ev.preventDefault();
        dispatch.keyDeleteLine($(this).data('line-id'));
      });

      $('#key').on('click', 'a.key-edit-control', function(ev) {
        ev.preventDefault();
        dispatch.keyEditLine($(this).data('line-id'));
      });
    };


    /**
     * Displays the summaries/key for all the lines.
     */
    exports.update = function() {
      // Add keys.
      lines.forEach(function(line) {
        renderLineKey(line);
      });
      
      // Remove keys for any lines that no longer exist.
      var line_ids = lines.map(function(line) { return line.id; });
      $('.key-line').each(function(n, el) {
        var line_id = $(this).data('line-id');
        if (line_ids.indexOf(line_id) < 0) {
          removeLineKey(line_id);
        };
      });

      // If there's only one line left, remove the UI to delete it.
      // And make sure it's 'shown'.
      if (lines.length == 1) {
        hideControl('.key-delete', '#key');
        hideControl('.key-show', '#key');
        $('.key-show-control').prop('checked', true);
      } else {
        showControl('.key-delete', '#key');
        showControl('.key-show', '#key');
      };

      // If we've got the maximum lines we're allowed, hide the duplicate
      // option.
      if (lines.length == colorPool.length) {
        hideControl('.key-duplicate', '#key');
      } else {
        showControl('.key-duplicate', '#key');
      };

      makeThemLineUpNormallyInRowsWhyIsThisSoHard();
    };


    /**
     * Gives all the keys in a row the same height, so that the next row
     * will position themselves neatly in place underneath.
     * Can't think of another good way to do this without adding and removing
     * special 'clear' divs between keys depending on the width.
     * Or fixing the width of the page.
     */
    function makeThemLineUpNormallyInRowsWhyIsThisSoHard() {
      // The heights of each key in a single row.
      var heights = [],
          // The top position of keys in the current row.
          currentTop = false,
          // The 0-based index of the key at the start of the current row.
          startOfLineIdx = 0;

      $('.key-line').each(function(idx){
        var keyTop = $(this).position().top;

        if (currentTop !== false && currentTop !== keyTop) {
          // This key is at the start of a new row.
          // So give all keys in the previous row the height of the tallest
          // key in the row.
          $('.key-line').slice(startOfLineIdx,idx).height(d3.max(heights));          
          heights = [];
          startOfLineIdx = idx;
        } else if ((idx+1) == $('.key-line').length && heights.length > 0) {
          // The last element on the final row.
          // So give all keys in the final row the height of the tallest in it.
          $('.key-line').slice(startOfLineIdx,idx).height(d3.max(heights));          
        };
        
        heights.push($(this).height());
        currentTop = keyTop;
      });
    };


    /**
     * Remove the descriptive key for a line.
     */
    function removeLineKey(line_id) {
      $('#key-'+line_id).remove();
    };


    /**
     * Create the descriptive key for a line.
     * line is the data for that line.
     */
    function renderLineKey(line) {
      if ($('#key #key-'+line.id).length == 0) {
        // This line isn't listed, so make its empty HTML.
        $('#key').append(templates.line_key({
          line_id: line.id,
          line_color: line.color
        }));
      };

      // Needs to be in scope for AddToKey() and RemoveFromKey() to see it.
      // A bit nasty.
      var cssid = '#key-'+line.id;

      
      if (line.values.length > 0) {
        hideControl('.key-no-data', cssid);
        showControl('.key-show', cssid);
        if (d3.keys(line.constraints).length == 1) {
          showControl('.key-all-data', cssid);
        } else {
          hideControl('.key-all-data', cssid);
        };
      } else {
        showControl('.key-no-data', cssid);
        hideControl('.key-show', cssid);
        hideControl('.key-all-data', cssid);
      };

      /**
       * Add an element to the current key, or update its contents if it exists.
       * content is an object containing:
       * clss: The class of the element(s) that will be added.
       *       Should something like 'place-title', 'people-content'.
       * And one of:
       * title: Text to use for a title.
       * text: Text to use for this line.
       * rows: An array of objects with `description` and `value` elements.
       */
      var addToKey = function(content) {
        var containerClass = '.key-descriptions-' + content.clss.split('-')[0];

        // Which template do we need?
        var template = templates.line_key_text;

        if ('title' in content) {
          template = templates.line_key_title;
        } else if ('rows' in content) {
          template = templates.line_key_rows; 
        };

        if ($(containerClass+' .'+content.clss, cssid).length == 0) {
          // Element doesn't yet exist - create it.
          $(containerClass, cssid).append( template(content) );
        } else {
          // Element exists, so just update its html.
          $(containerClass+' .'+content.clss, cssid).replaceWith(
                                                          template(content) );
        };
      };

      /**
       * Remove an element from the current key.
       * clss is the class name of the element to remove.
       */
      var removeFromKey = function(clss) {
        $('.'+clss, cssid).remove();
      };

      var cons = line.constraints;

      $('h2', cssid).text(cons.feeling.description);

      if (('in_out' in cons && cons.in_out)
          || 
          ('home_work' in cons && cons.home_work)) {
          addToKey({clss: 'place-title', title: 'Place'});
      } else {
        removeFromKey('place-title')
      };
      if ('in_out' in cons && cons.in_out) {
        addToKey({clss: 'place-inout',
                  rows: [{description: cons.in_out.description,
                          value: 1}]});
      } else {
        removeFromKey('place-inout'); 
      };
      if ('home_work' in cons && cons.home_work) {
        addToKey({clss: 'place-homework',
                  rows: [{description: cons.home_work.description,
                          value: 1}]});
      } else {
        removeFromKey('place-homework');
      };

      if (d3.keys(cons.people).length > 0) {
        addToKey({clss: 'people-title', title: 'People'});

        // How many possible people constraints are there?
        var total_people_constraints = d3.keys(MAPPINESS_DATA_DICTIONARY.people).length;
        
        // How many of the constraints we have are 0?
        var num_zero_people_constraints = d3.values(cons.people).filter(
            function(v){ return v.value == 0; }
        ).length;

        if (num_zero_people_constraints == total_people_constraints) {
          // ALL of the people constraints are set and they're ALL 0.
          // That means we've chosen 'Alone'.
          addToKey({
                clss: 'people-content',
                rows: [
                  // Fake a constraint:
                  {description: 'Alone, or with strangers only', value: 1}
                ]
              });
        } else {
          // SOME people constraints are set.
          addToKey({clss: 'people-content', rows: cons.people});
        };
      } else {
        removeFromKey('people-title');
        removeFromKey('people-content');
      };
    
      if (d3.keys(cons.activities).length > 0) {
        addToKey({clss: 'activities-title', title: 'Activities'});
        addToKey({clss: 'activities-content', rows: cons.activities});
      } else {
        removeFromKey('activities-title');
        removeFromKey('activities-content');
      };

      if ('notes' in cons && cons.notes) {
        addToKey({clss: 'notes-title', title: 'Notes'});
        addToKey({clss: 'notes-content', text: 'Containing “'+cons.notes.description +'”'}); 
      } else {
        removeFromKey('notes-title');
        removeFromKey('notes-content');
      };
    };

    /**
     * Disable one of the control links/checkboxes at the top of a line's key.
     * Both `selector` and `container` are like '.classname' or '#id'.
     */
    function hideControl(selector, container) {
      if ($(selector+' a', container).length > 0) {
        // There's a link(s) in here; change to a span.disabled.
        $(selector+' a', container).each(function(){
          $(this).addClass('disabled').changeElementType('span');
        });

      } else if ($(selector+' span.disabled', container).length > 0) {
        // A link that's already disabled. Do nothing.

      } else if ($(selector+' input[type=checkbox]', container).length) {
        // There's a checkbox in here. Disable it and the surrounding span.
        $(selector+' input[type=checkbox]', container).each(function(){
          $(this).prop('disabled', true);
          $(this).parent().addClass('disabled');
        });

      } else {
        // Something else, like .key-no-data. Just hide it.
        $(selector, container).hide();
      };
    };

    /**
     * Enable one of the control links/checkboxes at the top of a line's key.
     * Both `selector` and `container` are like '.classname' or '#id'.
     */
    function showControl(selector, container) {
      if ($(selector+' span.disabled', container).length > 0) {
        // There's span.disabled(s) in here; change to links.
        $(selector+' span.disabled', container).each(function(){
          $(this).removeClass('disabled').changeElementType('a');
        });

      } else if ($(selector+' input[type=checkbox]', container).length > 0) {
        // There's a checkbox in here. Enable it and the surrounding span.
        $(selector+' input[type=checkbox]', container).each(function(){
          $(this).prop('disabled', false);
          $(this).parent().removeClass('disabled');
        });

      } else {
        // Something else, like .key-no-data. Just show it.
        $(selector, container).show();
      };
    };

    
    /* Getters/setters */

    exports.colorPool = function(val) {
      if (!arguments.length) return colorPool;
      colorPool = val;
      return this;
    };

    exports.lines = function(val) {
      if (!arguments.length) return lines;
      lines = val;
      return this;
    };

    d3.rebind(exports, dispatch, 'on');

    return exports;
  };
});

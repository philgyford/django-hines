/**
 * For drawing and handling everything related to the line-editing pop-up form.
 */
define(['jquery', 'jquery.modal', './mappiness.templates', 'd3'],
function($,        jquery_modal,     mappiness_templates,   d3) {
  return function() {
    var exports = {},
        dispatch = d3.dispatch('editorSubmit'),
        // Will be an object containing textual descriptions of constraints.
        // Should be set by constraintsDescriptions();
        constraintsDescriptions = {},
        lines = [],
        templates = mappiness_templates().templates();

    initListeners();

    /**
     * Listens for jQuery events and turns them into events that the controller
     * listens for.
     */
    function initListeners() {
      // OK, this one isn't listened for by the controller because we can do it
      // all within this object.
      $('#line-edit-buttons .button-cancel').on('click', function(ev) {
        ev.preventDefault();
        exports.close();
      });

      $('#line-edit').on('submit', function(ev) {
        ev.preventDefault();
        var formData = processForm();
        dispatch.editorSubmit( formData );
      });
    };


    /**
     * Open the editor for a particular line.
     */
    exports.open = function(line_id) {
      if (prepare(line_id)) {
        $('#line-edit').modal({
                            showClose: false,
                            clickClose: false
                        });
        
        // Occasionally it could re-open scrolled to the bottom, so:
        $('#line-edit-body').scrollTop(0);
      };
    };


    exports.close = function() {
      $.modal.close();
    };


    /**
     * When the form is submitted, go through the fields and create a new
     * set of constraints for this line and return them and the line id.
     */
    function processForm() {
      var constraints = {};

      constraints.feeling = $('input[name=le-feeling]:checked', '#line-edit').val();
      if ( ! constraints.feeling in ['happy', 'relaxed', 'awake']) {
        constraints.feeling = 'happy'; // Default.
      };

      // If the People radio button is 'Any', we do nothing here.
      var people_radio = $('input[name=le-people]:checked', '#line-edit').val();

      if (['alone', 'with'].indexOf(people_radio) >= 0) {
        // Go through all the possible responses...
        for (p in MAPPINESS_DATA_DICTIONARY.people) {
          if (people_radio == 'with') {
            // If the radio button is 'With...' then we record the constraint
            // for each option if it's 1 or 0.
            var value = parseInt($('#le-people-'+p).val());
            if ([1, 0].indexOf(value) >= 0) {
              constraints[p] = value; 
            };
          } else {
            // If the radio button is 'Alone, or with strangers only' then
            // we set ALL the people constraints to 0.
            constraints[p] = 0;
          };
        };
      };

      // Add in_out and home_work values if they're valid.
      
      var inout_value = $('#le-place-inout', '#line-edit').val(); 
      if (d3.keys(MAPPINESS_DATA_DICTIONARY.in_out).indexOf(inout_value) >= 0) {
        constraints.in_out = inout_value; 
      };

      var homework_value = $('#le-place-homework', '#line-edit').val(); 
      if (d3.keys(MAPPINESS_DATA_DICTIONARY.home_work).indexOf(homework_value) >= 0) {
        constraints.home_work = homework_value; 
      };

      // Add notes string if there is one.
      var notes_value = $('#le-notes', '#line-edit').val();
      if (notes_value !== '') {
        constraints.notes = notes_value; 
      };

      // Add any activities which aren't set to 'ignore'.
      for (a in MAPPINESS_DATA_DICTIONARY.activities) {
        var value = parseInt($('#le-activities-'+a).val());
        if ([1, 0].indexOf(value) >= 0) {
          constraints[a] = value; 
        };
      };

      return {
        constraints: constraints,
        lineID: parseInt($('#le-line-id', '#line-edit').val()),
        color: $('#le-color', '#line-edit').val()
      };
    };


    /**
     * Prepares the edit form for a particular line.
     */
    function prepare(line_id) {
      var line;
      lines.forEach(function(ln) {
        if (ln.id == line_id) {
          line = ln;
        };
      });

      if (line) {
        setupForLine(line);
        return true;
      } else {
        alert("Sorry, can't find the data for this line."); 
        return false;
      };
    };


    /**
     * Updates the contents of the edit form with all the correct inputs.
     * No form fields will be selected etc.
     */
    function initialize() {
      $('.line-edit-col').empty();

      $('#line-edit-col-1').append(templates.line_edit_hidden({ }));

      $('#line-edit-col-1').append(templates.line_edit_feelings({
        feelings: {happy: 'Happy', relaxed: 'Relaxed', awake: 'Awake'}
      }));
    
      $('#line-edit-col-1').append(templates.line_edit_people({
        people: constraintsDescriptions.people
      }));

      $('#line-edit-col-1').append(templates.line_edit_place({
        in_out: constraintsDescriptions.in_out,
        home_work: constraintsDescriptions.home_work
      }));
      
      $('#line-edit-col-1').append(templates.line_edit_notes());

      $('#line-edit-col-2').append(templates.line_edit_activities({
        activities: constraintsDescriptions.activities
      }));

      // Set up custom events when changing certain fields.

      // Show the With... constraints when selecting that People radio button.
      $('#le-people').on('change', 'input[type=radio]', function(ev) {
        if ($(this).attr('id') == 'le-people-with') {
          $('#le-people-with-list').slideDown(); 
        } else {
          $('#le-people-with-list').slideUp(); 
          $('#le-people-with-list select').val('ignore')
                                        .next('label').addClass('text-muted');
        };
      });

      // Default state.
      $('.muted-labels label').addClass('text-muted');

      // Make the label of checked radio buttons, or selected selects
      // change color.
      $('.muted-labels').on('change', 'select,input[type=radio]', function(ev) {
        if ($(this).attr('type') == 'radio') {
          $(this).siblings('input:radio').next('label').addClass('text-muted');
          $(this).next('label').removeClass('text-muted');
        
        } else {
          // select fields.
          if ($(this).val() == 'ignore') {
            $(this).closest('li').children('label').addClass('text-muted');
          } else {
            $(this).closest('li').children('label').removeClass('text-muted');
          };
        };
      });
      
      // Resizing...

      setModalBodyHeight();
      
      $(window).resize(function(){
        // Keep the edit window centered.
        $.modal.resize(); 
        setModalBodyHeight();
      });

    };


    function setModalBodyHeight() {
      var h = $('#line-edit').outerHeight()
              - $('#line-edit-buttons').outerHeight()
              - parseInt($('#line-edit-body').css('padding-top'))
              - parseInt($('#line-edit-body').css('padding-bottom'));
      $('#line-edit-body').height(h);
    };


    /**
     * Creates a new form for a particular line and its constraints.
     * line is a d3 line object.
     */
    function setupForLine(line) {
      // Clear any old settings.
      initialize();

      var c = line.constraints;

      $('#le-line-id').val(line.id);
      $('#le-color').val(line.color);

      if ('feeling' in c) {
        $('#le-feeling-'+c.feeling.value).prop('checked', true).change(); 
      };

      if ('people' in c) {
        // How many possible people constraints are there?
        var total_people_constraints = d3.keys(
                                      MAPPINESS_DATA_DICTIONARY.people).length;

        // How many of the constraints we have are 0?
        var num_zero_people_constraints = d3.values(c.people).filter(
            function(v){ return v.value == 0; }
        ).length;

        if (num_zero_people_constraints == total_people_constraints) {
          // ALL of the people constraints are set and they're ALL 0.
          // That means we've chosen 'Alone'.
          $('#le-people-alone').prop('checked', true).change();
        
        } else {
          // SOME people constraints are set.
          $('#le-people-with').prop('checked', true).change();

          for (p in c.people) {
            $('#le-people-'+p).val(c.people[p].value.toString()).change();
          
          };
        };
      
      } else {
        // No people constraints are set, either 1 or 0, at all.
        $('#le-people-ignore').prop('checked', true).change();
      };

      if ('in_out' in c) {
        $('#le-place-inout').val(c.in_out.value).change(); 
      };

      if ('home_work' in c) {
        $('#le-place-homework').val(c.home_work.value).change(); 
      };

      if ('notes' in c) {
        $('#le-notes').val(c.notes.value).change();
      };

      if ('activities' in c) {
        for (a in c.activities) {
          $('#le-activities-'+a).val(c.activities[a].value.toString()).change();
        };
      };

      $('#line-edit-buttons').css('borderTopColor', line.color);
    };


    /* Getters/setters */

    exports.constraintsDescriptions = function(val) {
      if (!arguments.length) return constraintsDescriptions;
      constraintsDescriptions = val;
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

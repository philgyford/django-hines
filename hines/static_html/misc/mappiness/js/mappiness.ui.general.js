/**
 * General UI stuff not related to the Key or Editor.
 * ie, stuff that appears on first load, or is always present.
 * eg, import form.
 * d3 is only used for its d3.dispatch events.
 */
define(['jquery', 'jquery.modal', 'd3'],
function($,        jquery_modal,   d3) {
  return function() {
    var exports = {},
        dispatch = d3.dispatch('importSubmit', 'aboutOpen', 'importRandom'),
        // Will be a JS timeout object:
        loaderTimeout,
        importFormErrors = {
          generic: 'Sorry, something went wrong',
          // These keys are defined in mappiness.dataManager:
          bad_secret: "Mappiness didn't recognise your data code. Please check it.",
          ajax_error: "There was a problem while fetching your data. Maybe try again?"
        };

    initListeners();

    /**
     * Listens for jQuery events and turns them into events that the controller
     * listens for.
     */
    function initListeners() {
      // The user is submitting their secret code.
      $('#importer').on('submit', function(ev) {
        ev.preventDefault();
        var downloadCode = importFormProcess();
        dispatch.importSubmit( downloadCode );
        setPageTitle('Mappiness chart using your data');
      });

      // The user wants to try some random data.
      $('#importer-random').on('click', function(ev) {
        ev.preventDefault();
        dispatch.importRandom();
        setPageTitle('Mappiness chart using random data');
      });

      // OK, these don't get sent to the controller.
      $('header .links-about').on('click', function(ev) {
        ev.preventDefault();
        exports.aboutOpen();
      });

      // Closing the 'About' modal.
      $('#about-buttons .button-submit').on('click', function(ev) {
        ev.preventDefault();
        exports.aboutClose();
      });

    };

    exports.aboutOpen = function() {
      $('#about').modal({
                      showClose: false,
                      clickClose: false
                  });

      $('#about-body').load('about.html');
      setModalBodyHeight();

      $(window).resize(function(){
        // Keep the edit window centered.
        $.modal.resize(); 
        setModalBodyHeight();
      });
    };

    exports.aboutClose = function() {
      $.modal.close(); 
    };

    exports.importFormShow = function() {
      exports.loaderHide(); 
      importFormErrorHide();
      $('#importer').fadeIn(500);
    };

    exports.importFormHide = function() { 
      $('#importer').hide();
    };

    exports.loaderShow = function() { 
      $('#loader').show();
      // If this starts taking a while, we show an extra message:
      loaderTimeout = setTimeout(function(){
        $('#loader-slow').fadeIn(1000); 
      }, 3000);
    };

    exports.loaderHide = function() { 
      clearTimeout(loaderTimeout);
      $('#loader-slow').hide();
      $('#loader').hide();
    };

    /**
     * There was an error related to the import form.
     * Show it and an error.
     */
    exports.importFormError = function(msgCode) {
      exports.importFormShow();
      importFormErrorShow(msgCode);
    };

    function setPageTitle(str) {
      $('#site-title').text(str); 
    };

    function setModalBodyHeight() {
      var h = $('#about').outerHeight()
              - $('#about-buttons').outerHeight()
              - parseInt($('#about-body').css('padding-top'))
              - parseInt($('#about-body').css('padding-bottom'));
      $('#about-body').height(h);
    };

    /**
     * The form should just have a secret code in it.
     * But we'll accept the whole URL and take the code from it too.
     * Returns the download code.
     * Or returns false if we couldn't extract one (and displays the error
     * message to the user).
     */
    function importFormProcess() {
      importFormErrorHide();
      // A url would be like 'https://mappiness.me/3kkq.pk7d.23wb'.
      var submitted_code = $('#importer-code').val();
      var code = submitted_code.match(/[a-z0-9]{4,4}\.[a-z0-9]{4,4}\.[a-z0-9]{4,4}/);
      if (code !== null) {
        $('#importer .text-error').hide();
        exports.importFormHide();
        exports.loaderShow();
        return code; 
      } else {
        $('#importer .text-error').show();
        return false;
      };
    };

    /**
     * The error at the top of the form.
     */
    function importFormErrorShow(msgCode) {
      exports.importFormShow();
      if ( ! msgCode in importFormErrors) {
        msgCode = 'generic';
      };
      $('#importer-error').html(importFormErrors[msgCode]).show();
    };

    /**
     * The error at the top of the form.
     */
    function importFormErrorHide() {
      $('#importer-error').hide();
    };

    d3.rebind(exports, dispatch, 'on');

    return exports;
  };
});

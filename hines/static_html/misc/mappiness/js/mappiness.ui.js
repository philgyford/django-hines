/**
 * For handling all the dynamic forms etc.
 */
define(['./mappiness.ui.general', './mappiness.ui.key', './mappiness.ui.editor'],
function(  mappiness_ui_general,     mappiness_ui_key,     mappiness_ui_editor) {
  return function() {
    var exports = {};

    exports.key = mappiness_ui_key();
    exports.editor = mappiness_ui_editor();
    exports.general = mappiness_ui_general();

    /**
     * When the lines on the chart change, we need to reflect that in the UI.
     * lines is an array of d3 line objects.
     */
    exports.updateLines = function(lines) {
      exports.key.lines(lines);
      exports.key.update();
      exports.editor.lines(lines);
    };

    return exports;
  };
});



/**
 * We use EasyMDE, which is a fork of SimpleMDE.
 */
(function($) {
  "use strict";

  $(document).ready(function() {
    // Enable the Markdown editor.
    // Requires the MDE JS and CSS to be loaded too.

    hines.admin.markdownEditor().init();
  });

  window.hines = window.hines || {};

  window.hines.admin = window.hines.admin || {};

  window.hines.admin.markdownEditor = function module() {
    var fields = [
      {
        selector: "body.app-weblogs.model-post.change-form #id_intro",
        elementId: "id_intro",
        autosaveId: "weblogs-post-intro",
        buttons: "minimal",
        minHeight: "100px"
      },
      {
        selector: "body.app-weblogs.model-post.change-form #id_body",
        elementId: "id_body",
        autosaveId: "weblogs-post-body",
        buttons: "full",
        minHeight: "300px"
      }
    ];

    // The value of the "HTML format" select field that indicates whether
    // this post is in Markdown format or not.
    var markdown_formats = [
      "2", // Markdown
      "3" // Hines Markdown
    ];

    var exports = {
      /**
       * Call this method to set everything up.
       */
      init: function() {
        // Only for Markdown posts.
        if (markdown_formats.indexOf($("#id_html_format").val()) >= 0) {
          $.each(fields, function(idx, field) {
            if ($(field["selector"]).length > 0) {
              initField(field);
            }
          });
        }
      }
    };

    function initField(field) {
      var config = {
        element: document.getElementById(field["elementId"]),
        autoDownloadFontAwesome: true,
        autosave: {
          enabled: true,
          uniqueId: getAutosaveId(field),
          delay: 120000 // milliseconds
        },
        indentWithTabs: false, // Use spaces
        promptURLs: true, // Show pop-up for URL when adding a link
        minHeight: field["minHeight"]
      };

      if (field["buttons"] == "minimal") {
        config["toolbar"] = [
          "bold",
          "italic",
          {
            name: "cite",
            action: makeCite,
            className: "fa fa-angle-double-left",
            title: "Cite"
          },
          "link",
          "|",
          "preview",
          "side-by-side",
          "fullscreen"
        ];
      } else if (field["buttons"] == "full") {
        config["toolbar"] = [
          "bold",
          "italic",
          {
            name: "cite",
            action: makeCite,
            className: "fa fa-angle-double-left",
            title: "Cite"
          },
          "link",
          "|",
          "heading",
          "code",
          {
            name: "quote-with-caption",
            action: makeQuoteWithCaption,
            className: "fa fa-quote-left",
            title: "Quote with caption"
          },
          //"unordered-list",
          //"ordered-list",
          //"horizontal-rule",
          "|",
          {
            name: "image-left",
            action: makeImageLeft,
            className: "fa fa-arrow-left",
            title: "Image, aligned left"
          },
          {
            name: "image-standard",
            action: makeImageStandard,
            className: "fa fa-picture-o",
            title: "Image, standard"
          },
          {
            name: "image-full",
            action: makeImageFull,
            className: "fa fa-arrows-h",
            title: "Image, full-width"
          },
          {
            name: "image-right",
            action: makeImageRight,
            className: "fa fa-arrow-right",
            title: "Image, aligned right"
          },
          "|",
          {
            name: "video-left",
            action: makeVideoLeft,
            className: "fa fa-backward",
            title: "Video, aligned left"
          },
          {
            name: "video-full",
            action: makeVideoFull,
            className: "fa fa-play",
            title: "Video, full-width"
          },
          {
            name: "video-right",
            action: makeVideoRight,
            className: "fa fa-forward",
            title: "Video, aligned right"
          },
          "|",
          "preview",
          "side-by-side",
          "fullscreen"
        ];
      }

      var editor = new EasyMDE(config);
    }

    /**
     * Makes a unique ID for this field that's used for the autosave feature.
     * Must be unique across all fields across all Django objects.
     *
     * e.g. if field['autosaveId'] is 'weblogs-post-body' and we're editing
     * a Post with an ID of 123, this returns 'weblogs-post-body-123'.
     * But if we're creating a new Post, it returns 'weblogs-post-body'.
     *
     * @param field An object with an 'autosaveId' element.
     * @return string
     */
    function getAutosaveId(field) {
      var autosaveId = field["autosaveId"];
      var objectId = getObjectId();

      if (objectId !== null) {
        autosaveId += "-" + objectId;
      }

      return autosaveId;
    }

    /**
     * Return the ID of the Django object that's being edited, if any.
     * Returns the numeric ID as a string, or null if there isn't one.
     *
     * @return string or null
     */
    function getObjectId() {
      var urlParts = window.location.href.split("/");
      var len = urlParts.length;
      if (urlParts[len - 2] == "change") {
        return urlParts[len - 3];
      } else {
        return null;
      }
    }

    function makeCite(editor) {
      _addInlineTag(editor, "<cite>", "</cite>");
    }

    /**
     * Insert a blockquote in a figure with a figcaption.
     */
    function makeQuoteWithCaption(editor) {
      var startStr =
        '\
<figure class="figure figure--blockquote">\n\
  <blockquote>\n\
    <p>';

      var endStr =
        "    </p>\n\
  </blockquote>\n\
  <figcaption></figcaption>\n\
</figure>";

      _formatBlock(editor, startStr, endStr);
    }

    function makeImageLeft(editor) {
      makeImage(editor, "left");
    }

    function makeImageStandard(editor) {
      makeImage(editor, "standard");
    }

    function makeImageFull(editor) {
      makeImage(editor, "full");
    }

    function makeImageRight(editor) {
      makeImage(editor, "right");
    }

    function makeVideoLeft(editor) {
      makeVideo(editor, "left");
    }

    function makeVideoRight(editor) {
      makeVideo(editor, "right");
    }

    function makeVideoFull(editor) {
      makeVideo(editor, "full");
    }

    /**
     * Insert the HTML for an image.
     * If a URL is selected, that will be used as the image URL.
     * @param editor The editor object
     * @param alignment string "standard", "left", "right" or 'full'.
     */
    function makeImage(editor, alignment) {
      var startStr = '\
<figure class="figure figure--img';

      if (["left", "right", "full"].indexOf(alignment) > -1) {
        startStr += " figure--" + alignment;
      }

      startStr += '">\n\
  <img src="';

      var endStr = '" alt="">\n\
  <figcaption></figcaption>\n\
</figure>';

      _formatBlock(editor, startStr, endStr);
    }

    /**
     * Insert the HTML for an embedded video.
     * If a URL is selected, that will be used as the embed URL.
     * YouTube and Vimeo URLs will be replaced with their embed versions.
     * @param editor The editor object
     * @param alignment string "left", "right" or 'full'.
     */
    function makeVideo(editor, alignment) {
      var startStr = '\
<figure class="figure figure--embed';

      if (["left", "right"].indexOf(alignment) > -1) {
        startStr += " figure--" + alignment;
      }

      startStr +=
        '">\n\
  <div class="figure--embed__16by9">\n\
    <iframe src="';

      var endStr =
        '" allowfullscreen></iframe>\n\
  </div>\n\
  <figcaption></figcaption>\n\
</figure>';

      // First, replace the URL with the embed version, if necessary.
      var cm = editor.codemirror;
      var text = cm.getSelection();
      if (text.startsWith("http")) {
        var url = _makeVideoEmbedUrl(text);
        _replaceSelectedText(editor, url);
      }

      // Then wrap the URL with the HTML.
      _formatBlock(editor, startStr, endStr);
    }

    /**
     * Wrap a piece of text in HTML tags.
     * Caniblaised from _toggleBlock() in
     * https://github.com/Ionaru/easy-markdown-editor/blob/master/src/js/easymde.js
     *
     * Suppy the editor instance and the start/end tags to wrap in.
     * e.g.  _addInlineTag(editor, "<cite>", "</cite>")
     */
    function _addInlineTag(editor, start_chars, end_chars) {
      if (
        /editor-preview-active/.test(
          editor.codemirror.getWrapperElement().lastChild.className
        )
      ) {
        return;
      }

      end_chars = typeof end_chars === "undefined" ? start_chars : end_chars;
      var cm = editor.codemirror;
      var stat = editor.getState(cm);

      var text;
      var start = start_chars;
      var end = end_chars;

      var startPoint = cm.getCursor("start");
      var endPoint = cm.getCursor("end");

      text = cm.getSelection();

      text = text.split(start_chars).join("");
      text = text.split(end_chars).join("");

      cm.replaceSelection(start + text + end);

      startPoint.ch += start_chars.length;
      endPoint.ch = startPoint.ch + text.length;

      cm.setSelection(startPoint, endPoint);
      cm.focus();
    }

    /**
     * Replace selected text with a different string, and re-set the selection
     * to cover the new string.
     * Seems to work. Doubt it handles line breaks.
     * @param editor The editor object
     * @param replacement The string replace the selected text with.
     */
    function _replaceSelectedText(editor, replacement) {
      var cm = editor.codemirror;
      var startPoint = {};
      var endPoint = {};
      Object.assign(startPoint, cm.getCursor("start"));
      Object.assign(endPoint, cm.getCursor("end"));

      var selected = cm.getSelection();
      cm.replaceSelection(replacement);
      endPoint.ch += replacement.length - selected.length;
      cm.setSelection(startPoint, endPoint);
      cm.focus();
    }

    /**
     * Mostly copied from bits of toggleCodeBlock() in
     * https://github.com/Inscryb/inscryb-markdown-editor/blob/master/src/js/inscrybmde.js
     * Surround the selected text with startStr and endStr.
     * @param editor The editor object
     * @param startStr The string to put before the selected text
     * @param endStr The string to put after the selected text
     */
    function _formatBlock(editor, startStr, endStr) {
      var cm = editor.codemirror;
      var cur_start = cm.getCursor("start");
      var cur_end = cm.getCursor("end");

      var start_line_sel = cur_start.line + 1,
        end_line_sel = cur_end.line + 1,
        sel_multi = cur_start.line !== cur_end.line,
        repl_start = startStr,
        repl_end = endStr;

      if (sel_multi) {
        end_line_sel++;
      }
      // handle last char including \n or not
      if (sel_multi && cur_end.ch === 0) {
        repl_end = endStr + "\n";
        end_line_sel--;
      }
      _replaceSelection(cm, false, [repl_start, repl_end]);

      cm.setSelection(
        {
          line: start_line_sel,
          ch: 0
        },
        {
          line: end_line_sel,
          ch: 0
        }
      );
    }

    /**
     * Copied from _replaceSeletion() in
     * https://github.com/Inscryb/inscryb-markdown-editor/blob/master/src/js/inscrybmde.js
     */
    function _replaceSelection(cm, active, startEnd, url) {
      if (
        /editor-preview-active/.test(cm.getWrapperElement().lastChild.className)
      ) {
        return;
      }

      var text;
      var start = startEnd[0];
      var end = startEnd[1];
      var startPoint = {};
      var endPoint = {};
      Object.assign(startPoint, cm.getCursor("start"));
      Object.assign(endPoint, cm.getCursor("end"));
      if (url) {
        end = end.replace("#url#", url);
      }
      if (active) {
        text = cm.getLine(startPoint.line);
        start = text.slice(0, startPoint.ch);
        end = text.slice(startPoint.ch);
        cm.replaceRange(start + end, {
          line: startPoint.line,
          ch: 0
        });
      } else {
        text = cm.getSelection();
        cm.replaceSelection(start + text + end);

        startPoint.ch += start.length;
        if (startPoint !== endPoint) {
          endPoint.ch += start.length;
        }
      }
      cm.setSelection(startPoint, endPoint);
      cm.focus();
    }

    return exports;
  };

  /**
   * Turns a video URL into the embed version of it.
   *
   * YouTube, from this:
   *  https://www.youtube.com/watch?v=0bYY8m1Lb2I&t=92
   * to this:
   *  https://www.youtube.com/embed/0bYY8m1Lb2I?start=92
   *
   * Vimeo, from this:
   *  https://vimeo.com/157218918
   * to this:
   *  https://player.vimeo.com/video/157218918
   *
   * If url isn't of the correct form, it's returned unchanged.
   */
  function _makeVideoEmbedUrl(url) {
    if (url.search(/youtube.com\/watch/) >= 0) {
      var urlObj = new URL(url.trim());
      // Get relevant URL args:
      var v = urlObj.searchParams.get("v");
      var t = urlObj.searchParams.get("t");

      if (v) {
        url = "https://www.youtube.com/embed/" + v;
        if (t) {
          // Indication the seconds is different on watch URLs vs embeds:
          url += "?start=" + t;
        }
      }
    } else if (url.search(/\/\/vimeo.com/) >= 0) {
      var matches = url.match(/vimeo.com\/(\w+)$/);
      if (matches.length > 1) {
        url = "https://player.vimeo.com/video/" + matches[1];
      }
    }

    return url;
  }
})(django.jQuery);

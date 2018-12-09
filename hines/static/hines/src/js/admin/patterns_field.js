/**
 * Adds some buttons above textareas in Django Admin that, when clicked, insert
 * our custom HTML patterns into the textarea.
 *
 * To use, include this JS in the Admin change page for a model, and add the
 * 'js-patterns' class to the textarea. eg:
 *
 * from django import forms
 * from django.contrib import admin
 * from myapp.models import Post
 *
 * class PostAdminForm(forms.ModelForm):
 *     class Meta:
 *         model = Post
 *         widgets = {
 *             'body': forms.Textarea(attrs={
 *                         'class': 'vLargeTextField js-patterns',
 *              })
 *         }
 *         fields = '__all__'
 *
 * @admin.register(Post)
 * class PostAdmin(admin.ModelAdmin):
 *     form = PostAdminForm
 *     # more here...
 */
;(function($) {
  'use strict';

  $(document).ready(function() {
    // GO!
    hines.admin.patternsField().init();
  });

  window.hines = window.hines || {};

  window.hines.admin = window.hines.admin || {};

  window.hines.admin.patternsField = function module() {

    var exports = {

      /**
       * Call this method to set everything up.
       */
      init: function() {
        if ($('.js-patterns').length === 0) {
          // No appropriate fields to prepare.
          return;
        };

        $('.js-patterns').each(function(idx) {
          initField($(this));
        });
      }
    };

    /**
     * Prepare a single textarea.
     * $field is the jQuery object representing the textarea.
     */
    function initField($field) {
      addButtons($field);
      initListeners($field);
    };

    /**
     * Add the buttons/links above the textarea.
     * $field is the jQuery object representing the textarea.
     */
    function addButtons($field) {
      $field.before('\
        <div style="margin-bottom: 0.5em;">\
          Video: \
          &nbsp; \
          <a href="#" class="js-patterns-button" data-pattern="video" data-options="left">Left</a> &nbsp;\
          <a href="#" class="js-patterns-button" data-pattern="video">Full</a> &nbsp;\
          <a href="#" class="js-patterns-button" data-pattern="video" data-options="right">Right</a> &nbsp;\
          &nbsp; \
          Image: \
          &nbsp; \
          <a href="#" class="js-patterns-button" data-pattern="img" data-options="left">Left</a> &nbsp;\
          <a href="#" class="js-patterns-button" data-pattern="img" data-options="">Standard</a> &nbsp;\
          <a href="#" class="js-patterns-button" data-pattern="img" data-options="full">Full</a> &nbsp;\
          <a href="#" class="js-patterns-button" data-pattern="img" data-options="right">Right</a> &nbsp;\
          • \
          &nbsp; \
          <a href="#" class="js-patterns-button" data-pattern="quote">Quote</a> &nbsp;\
          • \
          &nbsp; \
          <a href="#" class="js-patterns-button" data-pattern="code">Code</a> &nbsp;\
        </div>\
      ');
    };

    /**
     * Start listening for clicks on the buttons, and insert the appropriate
     * HTML when one is clicked.
     */
    function initListeners() {
      $('.js-patterns-button').on('click', function(ev) {
        ev.preventDefault();

        var $field = $(this).parent().siblings('.js-patterns');
        var pattern = $(this).data('pattern');
        var options = $(this).data('options');

        insertPattern($field, pattern, options);
      });
    };

    /**
     * Does the main job of inserting a pattern at the insertion point.
     *
     * $field is the textarea jQuery element.
     * pattern is a string like 'video', 'img', 'quote' or 'code'.
     * options is a string like 'left' or 'right'.
     */
    function insertPattern($field, pattern, options) {
      var text = $field.val();
      var start = $field.prop('selectionStart');
      var end = $field.prop('selectionEnd');

      var startText = text.substr(0, start);
      var selectedText = text.substr(start, (end-start));
      var endText = text.substr(end);

      // What we'll insert at selection point, if any:
      var html = '';

      // Get any options from the button's data-options attribute:
      var optionsArr = [options];

      // Work out what kind of thing we're inserting from the data-pattern attr:
      if (pattern) {
        html = makePattern(pattern, selectedText, optionsArr);
      };

      text = startText + html + endText;

      $field.val(text);
    };

    /**
     * Returns the HTML for a pattern.
     *
     * pattern is one of 'video'.
     * text is the selected text we're overwriting, if any.
     * options is an array of strings. Depends on the pattern type.
     *   'video' pattern could optionally have 'left' or 'right'.
     */
    function makePattern(pattern, text, options) {
      var html = getHtml(pattern);

      if (pattern === 'video') {
        if (options.includes('left')) {
          html = html.replace('--embed"', '--embed figure--left"');
        } else if (options.includes('right')) {
          html = html.replace('--embed"', '--embed figure--right"');
        };

        if (text && text.trim().startsWith('http')) {
          // If the selected text was a URL,
          var url = makeVideoEmbedUrl(text);
          html = html.replace('""', '"'+url+'"');
        };

      } else if (pattern === 'img') {
        if (options.includes('left')) {
          html = html.replace('--img"', '--img figure--left"');
        } else if (options.includes('full')) {
          html = html.replace('--img"', '--img figure--full"');
        } else if (options.includes('right')) {
          html = html.replace('--img"', '--img figure--right"');
        };

        if (text && text.trim().startsWith('http')) {
          // If the selected text was a URL, assume it's an image URL
          // and put it in.
          html = html.replace('src=""', 'src="'+text.trim()+'"');
        };

      } else if (pattern === 'quote') {
        // Replace multi-newlines with <p></p> tags.
        text = text.trim().replace(/\n\n/g, "</p>\n    <p>");
        // Add start and end <p></p> tags, and insert the text:
        html = html.replace("<p></p>",
                            "<p>" + text + "</p>");

      } else if (pattern === 'code') {
        // Replace multi-newlines with <p></p> tags.
        text = text.trim().replace(/\n\n/g, "</p>\n    <p>");
        // Add start and end <p></p> tags, and insert the text:
        html = html.replace("<code></code>",
                            "<code>" + text + "</code>");
      };

      return html;
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
    function makeVideoEmbedUrl(url) {

      if (url.search(/youtube.com\/watch/) >= 0) {
        var urlObj = new URL(url.trim());
        // Get relevant URL args:
        var v = urlObj.searchParams.get('v');
        var t = urlObj.searchParams.get('t');

        if (v) {
          url = 'https://www.youtube.com/embed/'+v
          if (t) {
            // Indication the seconds is different on watch URLs vs embeds:
            url += '?start='+t;
          };
        };

      } else if (url.search(/\/\/vimeo.com/) >= 0) {
        var matches = url.match(/vimeo.com\/(\w+)$/);
        if (matches.length > 1) {
          url = 'https://player.vimeo.com/video/' + matches[1];
        };
      };

      return url;
    };

    /**
     * Returns the basic HTML for a particular pattern.
     */
    function getHtml(pattern) {
      var html = '';

      if (pattern === 'video') {
        html = "\
<figure class=\"figure figure--embed\">\n\
  <div class=\"figure--embed__16by9\">\n\
    <iframe src=\"\" allowfullscreen></iframe>\n\
    <figcaption></figcaption>\n\
  </div>\n\
</figure>";
      } else if (pattern === 'img') {
        html = "\
<figure class=\"figure figure--img\">\n\
  <img src=\"\" alt=\"\">\n\
  <figcaption></figcaption>\n\
</figure>";
      } else if (pattern === 'quote') {
        html = "\
<figure class=\"figure figure--blockquote\">\n\
  <blockquote>\n\
    <p></p>\n\
  </blockquote>\n\
  <figcaption></figcaption>\n\
</figure>";
      } else if (pattern === 'code') {
        html = "\
<pre><code></code></pre>";
      };

      return html;
    };

    return exports;
  };

})(django.jQuery);

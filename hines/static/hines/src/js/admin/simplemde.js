;(function($) {
  'use strict';

  $(document).ready(function() {
    // Enable SimpleMDE on the Weblog Post Body element.
    // Requires the SimpleMDE JS and CSS to be loaded too.

    if ($("body.app-weblogs.model-post.change-form #id_body").length > 0) {
      var bodyMDE = new SimpleMDE({
        element: document.getElementById("id_body"),
        autosave: {
          enabled: true,
          uniqueId: "weblogs-post-body",
          delay: 1000, // milliseconds
        },
        indentWithTabs: false, // Use spaces
        promptURLs: true, // Show pop-up for URL when adding a link
      });
    };

  });

})(django.jQuery);

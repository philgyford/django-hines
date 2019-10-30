/**
 * Handles showing the navbar search form.
 *
 * 1. Adds a 'js-can-navbar' class to the body (useful for CSS).
 * 2. Adds a new <li><button></button></li> element to the navbar's <ul>.
 * 3. Listens for a click on that. If it happens...
 * 4. ...hides that <li> and shows the search form.
 *
 * The CSS should deal with:
 * 1. Hiding the <li> at wider widths and showing it at narrow ones.
 * 2. Hiding the form at narrow widths and showing it at wider ones.
 *
 * Initialise like:
 *
 *  var navbar = hines.navbar();
 *  navbar.init();
 *
 * Relies on our utils.js.
 */
(function() {
  "use strict";

  window.hines = window.hines || {};

  window.hines.navbar = function module() {
    // The nav <ul> that we'll add an <li> to:
    var navClass = "js-navbar-nav";

    // The nav <li> that we'll make and hide:
    var liClass = "js-navbar-item-search";

    // The mav <button> that we'll make, which will reveal the search form:
    var buttonClass = "js-navbar-nav-item-search";

    // The search form:
    var formClass = "js-navbar-form";
    var formId = "js-navbar-form";

    var exports = {
      init: function() {
        // Indicate to the CSS that this is running:
        $.addClass(document.body, "js-can-navbar");

        createSearchLink();

        initListener();
      }
    };

    /**
     * Creates the <li><a></a></li> for the 'Search' link, and appends to
     * the nav <ul>.
     */
    function createSearchLink() {
      var button = document.createElement("button");
      button.setAttribute("aria-expanded", "false");
      button.setAttribute("aria-controls", formId);
      button.setAttribute("type", "button");
      button.setAttribute("class", "button--link nav__link " + buttonClass);
      button.textContent = "Search";

      var li = document.createElement("li");
      li.setAttribute("class", "nav__item nav__item--split " + liClass);

      li.appendChild(button);

      var nav = $.getElByClass(navClass);

      nav.appendChild(li);
    }

    function initListener() {
      $.getElByClass(buttonClass).addEventListener("click", function(event) {
        event.preventDefault();

        $.hideEl(liClass);
        $.showEl(formClass, "block");

        var button = $.getElByClass(buttonClass);
        button.setAttribute("aria-expanded", "true");
      });
    }
    return exports;
  };
})();

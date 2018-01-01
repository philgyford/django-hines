"use strict";

var $ = {};

/**
 * Returns the element indicated by the CSS class name.
 * If there's more than one, returns them all in an HTMLCollection.
 * If there's only one, returns just that one element.
 * If there are none, returns an empty HTMLCollection.
 */
$.getElByClass = function(classname) {
  var el = document.getElementsByClassName(classname);
  if (el && el.length === 1) {
    el = el[0];
  };
  return el;
};

/**
 * Show the element with a CSS class of `classname`.
 * Optional displayVal will be used for the display style, otherwise ''.
 */
$.showEl = function(classname, displayVal) {
  if (displayVal) {
    $.getElByClass(classname).style.display = displayVal;
  } else {
    $.getElByClass(classname).style.display = '';
  };
};

/**
 * Hide the element with a CSS class of `classname`.
 */
$.hideEl = function(classname) {
  $.getElByClass(classname).style.display = 'none';
};

/**
 * Add className to el's CSS class(es).
 */
$.addClass = function(el, className) {
  if (el.classList) {
    el.classList.add(className);
  } else {
    el.className += ' ' + className;
  };
};

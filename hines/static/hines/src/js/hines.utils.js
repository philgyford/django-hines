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

/**
 * Apply a function to every matching element.
 *
 * e.g. This would display every 'a' element in the console:
 *
 *     $.each( 'a', function(el) { console.log(el); } );
 */
$.each = function(selector, fn) {
  var elements = document.querySelectorAll(selector);

  Array.prototype.forEach.call(elements, function(el, i){
    fn.call(i, el);
  });
};


/**
 * domready (c) Dustin Diaz 2014 - License MIT
 * https://github.com/ded/domready
 *
 * Use like:
 *
 * domready(function(){
 *  console.log("We're ready!");
 * });
 */
!function (name, definition) {

  if (typeof module != 'undefined') module.exports = definition()
  else if (typeof define == 'function' && typeof define.amd == 'object') define(definition)
  else this[name] = definition()

}('domready', function () {

  var fns = [], listener
    , doc = typeof document === 'object' && document
    , hack = doc && doc.documentElement.doScroll
    , domContentLoaded = 'DOMContentLoaded'
    , loaded = doc && (hack ? /^loaded|^c/ : /^loaded|^i|^c/).test(doc.readyState)


  if (!loaded && doc)
  doc.addEventListener(domContentLoaded, listener = function () {
    doc.removeEventListener(domContentLoaded, listener)
    loaded = 1
    while (listener = fns.shift()) listener()
  })

  return function (fn) {
    loaded ? setTimeout(fn, 0) : fns.push(fn)
  }

});

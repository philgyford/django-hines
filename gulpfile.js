/**
 * What this does:
 *
 * Compresses Sass files into a CSS file.
 * Creates a CSS sourcemap file.
 * Minifies and combines our JS files into one file.
 * Adds unique revision hashes into the JS and CSS filenames.
 * Injects the new JS and CSS file paths into the base.html tmeplate.
 *
 * Use like:
 *
 *  $ gulp
 *
 * Or, to watch for changes:
 *
 *  $ gulp watch
 */

'use strict';

var gulp        = require('gulp');
var gutil       = require('gulp-util');
var concat      = require('gulp-concat');
var del         = require('del');
var inject      = require('gulp-inject');
var rev         = require('gulp-rev');
var sass        = require('gulp-sass');
var series      = require('stream-series');
var sourcemaps  = require('gulp-sourcemaps');
var uglify      = require('gulp-uglify');
var autoprefixer  = require('gulp-autoprefixer');


/******************************************************************************
 * VARIABLES
 */

var SRC_DIR             = 'hines/static/hines/src';
var STATIC_DIR          = 'hines/static';
var TEMPLATES_DIR       = 'hines/templates/';
// Removed from the start of CSS/JS paths inserted into files by inject:
var INJECT_IGNORE_PATH  = 'hines';

var PATHS = {
  src: {
    sassFiles:      SRC_DIR + '/sass/**/*.scss',
    sassWatchFiles: SRC_DIR + '/sass/**/*.scss',
    // Already minified files to be copies as-is:
    cssVendorFiles: SRC_DIR + '/css/vendor/**/*.css',
    cssWatchFiles:  SRC_DIR + '/css/**/*.css',
    jsDir:          SRC_DIR + '/js',
    // Already minified files to be copies as-is:
    jsVendorFiles:  SRC_DIR + '/js/vendor/**/*.js',
    jsWatchFiles:   SRC_DIR + '/js/**/*.js',
    // Our custom file(s):
    jsSiteFiles:    SRC_DIR + '/js/*.js',
    jsAdminFiles:   SRC_DIR + '/js/admin/*.js',
  },
  dest: {
    cssDir:         STATIC_DIR + '/hines/css',
    cssFiles:       STATIC_DIR + '/hines/css/**/*.css',
    cssVendorDir:   STATIC_DIR + '/hines/css/vendor',
    jsDir:          STATIC_DIR + '/hines/js',
    jsVendorDir:    STATIC_DIR + '/hines/js/vendor',
    // All generated JS files:
    // NOTE: Doesn't include those in subdirectories like /vendor/
    jsFiles:        STATIC_DIR + '/hines/js/*.js'
  },
  templates: {
    files:          [TEMPLATES_DIR + '/hines_core/layouts/bare.html',]
  }
};


/******************************************************************************
 * Tasks that do the work.
 */


/**
 * Delete any existing files generated by this script.
 */

gulp.task('clean:css', function() {
  // .css and .css.map
  return del(PATHS.dest.cssFiles + '*');
});

gulp.task('clean:js', function() {
  return del(PATHS.dest.jsFiles);
});

gulp.task('clean', gulp.parallel('clean:css', 'clean:js'));


/**
 * Copy Vendor CSS files.
 * Create CSS file from Sass files.
 * Autoprefix the CSS.
 * Create a sourcemap file.
 * Add a revision code to each file.
 */
gulp.task('sass', gulp.series('clean:css', function buildSass() {

  // First, just copy our already-minified and not-used-everywhere
  // 3rd-party CSS files:
  gulp.src([
    PATHS.src.cssVendorFiles
  ])
    .pipe(gulp.dest(PATHS.dest.cssVendorDir));

  var sassOptions = {
    outputStyle: 'compressed',
    sourceComments: false
  };

  return gulp.src(PATHS.src.sassFiles)
    .pipe(sourcemaps.init())
      .pipe(sass(sassOptions).on('error', sass.logError))
      .pipe(rev())
      .pipe(gulp.dest(PATHS.dest.cssDir))
    .pipe(autoprefixer())
    .pipe(sourcemaps.write('.'))
    .pipe(gulp.dest(PATHS.dest.cssDir));
}));


/**
 * Minify and combine all the JS files used for all browsers.
 */
gulp.task('js', gulp.series('clean:js', function buildJS() {

  gulp.src([
    PATHS.src.jsAdminFiles
  ])
    .pipe(concat('admin.min.js'))
    .pipe(uglify())
    .pipe(gulp.dest(PATHS.dest.jsDir));

  // First, just copy our already-minified and not-used-everywhere
  // 3rd-party JS files:
  gulp.src([
    PATHS.src.jsVendorFiles
  ])
    .pipe(gulp.dest(PATHS.dest.jsVendorDir));


  // A stream of our custom JS files, minified.
  var customStream = gulp.src(PATHS.src.jsSiteFiles)
    .pipe(uglify())

  // A stream of the already-minified vendor files.
  //var vendorStream = gulp.src([
    ////PATHS.src.jsVendorDir + '/jquery.timeago.min.js',
    ////PATHS.src.jsVendorDir + '/bootstrap.min.js'
  //]);

  // Combine both streams of minified JS into one file.
  // Need to be in this order, so jQuery is loaded before our custom JS.
  //return series(vendorStream, customStream)
  return series(customStream)
    .pipe(concat('site.min.js'))
    .pipe(rev())
    .pipe(gulp.dest(PATHS.dest.jsDir));
}));


/**
 * Add links to generated CSS files into templates.
 * We just add conventional paths, rather than adding Django's {% static ... %}
 * tags using a transform function, because then it also works for templates
 * like the static 404.html, 500.html, etc.
 */
gulp.task('inject', function doInjection() {
  var sources = gulp.src([
    PATHS.dest.cssFiles,
    PATHS.dest.jsFiles
  ], {read: false});

  var options = {
    ignorePath: INJECT_IGNORE_PATH
  };

  return gulp.src(PATHS.templates.files, {'base': TEMPLATES_DIR})
    .pipe(inject(sources, options))
    .pipe(gulp.dest(TEMPLATES_DIR))
});



/******************************************************************************
 * The Tasks we're most likely to call from the command line.
 */

// For all the below, we must have usePolling if running this in a VM, and
// editing the files on the host, because changes won't be noticed otherwise.

gulp.task('js:watch', function () {
  gulp.watch(PATHS.src.jsWatchFiles, {usePolling: true}, gulp.series(
    'js',
    'inject'
  ));
});


gulp.task('sass:watch', function () {
  gulp.watch(PATHS.src.sassWatchFiles, {usePolling: true}, gulp.series(
    'sass',
    'inject'
  ));
});


/**
 * Watch both JS and Sass files for changes.
 */
gulp.task('watch', gulp.parallel(
  'js:watch',
  'sass:watch'
));


/**
 * Run everything, one time only.
 */
gulp.task('default', gulp.series(
  gulp.parallel(
    'js',
    'sass'
  ),
  'inject'
));

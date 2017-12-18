<?
// Photo handler
// Should be named 'index.php3' and placed in a directory of images.
// Displays a directory list and nice photo pages.



// YOU JUST NEED TO EDIT THESE 3 VARIABLES:

$page_title = "Thesis Images";
$email_address = "phil@gyford.com";
$style_sheet = "/style/global.css";



// $photo contains the image name - or 'none' if this should be a directory listing.
if (!$photo) {
	$photo = "none";
}

// Rounds the sizes of files for the directory list.
function round_size ($size) {
	// Rounds the sizes of files for the directory list.
	if ($size >= 1073741824) { 
		return sprintf ("%.1f Gb", (round ($size / 1073741824 * 100) / 100)); 
	} elseif ($size >= 1048576) { 
		return sprintf ("%.1f Mb", (round (size / 1048576 * 100) / 100)); 
	} elseif ($size >= 1024) { 
		return sprintf ("%.1f Kb", (round ($size / 1024 * 100) / 100)); 
	} else { 
		return sprintf ("%.1f b", ($size)); 
	} 
}


$path = ereg_replace ("/(.*/)index.php3", "\\1", $PHP_SELF);
$path_elements = explode ("/", $path);
$current_dir = $path_elements[count($path_elements)-2];

print "<HTML>\n<HEAD>\n<TITLE>$page_title</TITLE>\n<link title=\"Photos Style\" rel=stylesheet href=\"$style_sheet\" type=\"text/css\">\n</HEAD>\n<BODY bgcolor=\"#FFFFFF\">\n";

$handle=opendir(".");

while ($file = readdir($handle)) {
	// We don't want to list the directory itself, the parent or this page.
	if (!is_dir($file) && $file!="index.php3") {
		$num_files++;
		// $xfile is an array containing the list of file names.
		$xfile[$num_files] = $file;
		if ($photo == $file) {
			// If we're looking at a photo, grab its index in the list of photos.
			$file_index = $num_files;
		}
	}
}

//if ($xfile) {
//	sort ($xfile);
//}


// -----------------
// DIRECTORY LISTING
// -----------------

// Build the full path to this directory.
$print_path = "<a href=\"http://$HTTP_HOST\">$HTTP_HOST</a>";
$file_path = "";
$n = 0;
while (list(, $element) = each ($path_elements)) {
	$file_path .= "/$element";
	if ($n != (count($path_elements) - 2)) {
		$print_path .= "/<a href=\"$file_path/\">$element</a>";
	} else {
		// If this is the current directory, don't make it a link.
		$print_path .= "/$element";
		$current_dir = $element;
	}
	$n++;
}
		
// Header and clickable path.
print "<H1>$page_title</H1>\n";
	print "$print_path<p>\n";
print "\n<p>&nbsp;<br>\n<table border=0>\n";

// Print the directory list.
for ($n = 1; $n <= $num_files; $n++) {
		$filemodtime = date("F j Y h:i a", filemtime($xfile[$n])); 
		print "<tr><td>&nbsp;&nbsp;&nbsp;&nbsp;<A HREF=\"$xfile[$n]\">$xfile[$n]</A></td><td>&nbsp;&nbsp;</td><td align=\"right\">" . round_size(filesize($xfile[$n])) . "</td><td>&nbsp;&nbsp;</td><td>" . $filemodtime ."</td></tr>\n";
}
	
print "</table>\n<p>&nbsp;<p>\n";

closedir($handle); 
print "<p><a href=\"mailto:$email_address\">$email_address</a>";
print "</BODY></HTML>";


?>

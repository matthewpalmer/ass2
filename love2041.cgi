#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;
use List::Util qw/min max/;
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 1;
$students_dir = "./students/students";

display_profile("AwesomeAngel57");
print page_trailer();
exit 0;

sub display_profile {
	my $username = shift;
	my $html = profile_html($username);
	print $html;
}

sub browse_screen {
	my $n = param('n') || 0;
	my @students = glob("$students_dir/*");
	$n = min(max($n, 0), $#students);
	param('n', $n + 1);
	my $student_to_show  = $students[$n];
	my $profile_filename = "$student_to_show/profile.txt";
	open my $p, "$profile_filename" or die "can not open $profile_filename: $!";
	$profile = join '', <$p>;
	close $p;

	return p,
		start_form, "\n",
		pre($profile),"\n",
		hidden('n', $n + 1),"\n",
		submit('Next student'),"\n",
		end_form, "\n",
		p, "\n";
}

#
# HTML production
# ===============

#
# HTML placed at top of every screen
#
sub page_header {
	return header,
   		start_html("-title"=>"LOVE2041", -style=>{'src'=>"styles.css"}),
 		center(h1("LOVE2041"));
}

#
# HTML placed at bottom of every screen
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
	my $html = "";
	$html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
	$html .= end_html;
	return $html;
}

#
# HTML for images
# Takes an image URL as the only parameter
#
sub image_html($) {
	my $url = shift @_;
	my $html = "<img src = '" . $url . "'/>";
	return $html;
}

#
# HTML for the person's profile
#
sub profile_html($) {
	# Username
	my $username = shift;

	# Profile photo URL
	# Degree
	# Birthdate
	# Favourite Books
	#   TV Shows
	#   Bands
	#   Movies
	# Weight
	# Hair Color
 	my $html = "<div class = 'profile'>";
	$html .= "<h2>" . $username . "</h2>";

	# Display the profile photo if they have one.
	if (-e profilePhotoURL($username)) {
		$html .= image_html(profilePhotoURL($username));
	}

	# Display the degree
	$html .= degree_html(degrees($username));

	# Display favorite books, movies, tv shows, bands, hobbies, etc.
	# ...

	# Display physical attributes
	# - hair color
	# - weight
	# - age
	# - height
	$html .= hair_color_html(hairColor($username));
	$html .= weight_html(weight($username));
	$html .= age_html(age($username));
	$html .= height_html(height($username));


	$html .= "</div>";
}

#
# HTML for the person's favourite X sections
# Takes the type of preference (TV, Book, etc.) and a list of preferences
#
sub preferences_html($@) {
	my $type = shift;
	my $html = "<h3>" . $type . "</h3><ul>";

	foreach (@_) {
		$html .= "<li>" . $_ . "</li>";
	}

	$html .= "</ul>";
}

#
# HTML to display the user's degree(s?)
# Takes a list of degrees
#
sub degree_html(@) {
	my $html = "<h4>";

	$html .= $_ . ". " foreach (@_);

	$html .= "</h4>";
	return $html;
}

#
# HTML to display generic attributes consistently
# Takes the kind of attribute, and the value
#
sub attribute_html($$) {
	my $type = shift;
	my $value = shift;
	if (defined $type && defined $value) {
		my $html = "<strong>" . $type . "</strong>: ";
		$html .= $value . "<br/>";
		return $html;
	}
}

#
# HTML to display the user's hair color
# Takes the hair color
#
sub hair_color_html($) {
	my $hairColorKey = "Hair color";
	return attribute_html($hairColorKey, $_) if defined $_;
}

#
# HTML to display the user's height
# Takes the height
#
sub height_html($) {
	my $heightKey = "Height";
	return attribute_html($heightKey, $_) if defined $_;
}

#
# HTML to display the user's weight
# Takes the weight
#
sub weight_html($) {
	my $weightKey = "Weight";
	return attribute_html($weightKey, $_) if defined $_;
}

#
# HTML to display the user's age
# Takes the age
#
sub age_html($) {
	my $ageKey = "Age";
	return attribute_html($ageKey, $_) if defined $_;
}

#
# Data Access
# ===========

#
# The user's profile photo URL
#
sub profilePhotoURL($) {
 	my $username = shift;
	my $profilePhotoURL = $students_dir . "/" . $username . "profile.jpg";
	return $profilePhotoURL;
}

#
# A list of the user's other photos
#
sub otherPhotos($) {
	my $username = shift;
	my @photos = ();
	# ...
	return @photos;
}

#
# A list of the user's degrees
#
sub degrees($) {
	my $username = shift;
	my @degrees = ();
	# ...
	return @degrees;
}

#
# The user's hair color
#
sub hairColor($) {
	my $username = shift;
	my $hairColor = "something?";
	return $hairColor;
}

#
# The user's height
#
sub height($) {
	my $username = shift;
	my $height = "something?";
	return $height;
}

#
# The user's weight
#
sub weight($) {
	my $username = shift;
	my $weight = "something?";
	return $weight;
}

#
# The user's age
#
sub age($) {
	my $username = shift;
	my $age = "something?";
	return $age;
}

#
# A list of the user's favourite books
#
sub favoriteBooks($) {
	my @books = ();
	# ...
	return @books;
}


#
# A list of the user's favourite bands
#
sub favoriteBands($) {
	my @bands = ();
	return @bands;
}

#
# A list of the user's favourite tv shows
#
sub favouriteTVShows($) {
	my @shows = ();
	return @shows;
}

#
# A list of the user's favourite hobbies
#
sub favoriteHobbies($) {
	my @hobbies = ();
	return @hobbies;
}

#
# A list of the user's favourite movies
#
sub favoriteMovies($) {
	my @movies = ();
	return @movies;
}
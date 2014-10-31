#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/


### Structure
# There are 3 main files to this project:
# 	1. This file (love2041.cgi)
# 	2. ProfileImporter, which imports the data about the user's from the text files.
# 	3. Matchmaker, which decides which users are good matches for eachother.
#
# This file is structured in the following way:
# 	Section 1 — Setup
# 	Section 2 — Determining state
# 	Section 3 — HTML display
# 	Section 4 — Data retrieval
# 	Section 5 — Data updating
#
# You can easily navigate between the sections by search for 'Section X'


# Section 1 — Set up
# ##################

use FindBin qw( $RealBin );
use lib $RealBin;

# Import my modules
use ProfileImporter qw(loadHashes);
use Matchmaker qw(matches);

# Import core modules
use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;
use List::Util qw/min max/;
use Scalar::Util qw(looks_like_number);

# Config
warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# Globals used throughout the script
$debug = 1;
$students_dir = "./students";
$suspended_dir = "./suspended";
$deleted_dir = "./deleted";
$reset_file = "./reset.txt";
$scripts_file = "scripts.js";

# Hashes to store our data
my ($studentsRef, $preferencesRef) = loadHashes();
my %studentsHash = %{$studentsRef};
my %preferencesHash = %{$preferencesRef};

# Keys to access these hashes
my $profilePhotoKey = "profile_photo";
my $photosKey = "photos";
my $realNameKey = "name";
my $birthdateKey = "birthdate";
my $heightKey = "height";
my $genderKey = "gender";
my $weightKey = "weight";
my $passwordKey = "password";
my $hairColorKey = "hair_color";
my $emailKey = "email";
my $degreeKey = "degree";
my $bandsKey = "favourite_bands";
my $moviesKey = "favourite_movies";
my $tvShowsKey = "favourite_TV_shows";
my $hobbiesKey = "favourite_hobbies";
my $booksKey = "favourite_books";
my $coursesKey = "courses";
my $profileTextKey = "profile_text";

# Preferences
my $ageKey = "age";
my $hairColorPrefKey = "hair_colours";
my $minKey = "min";
my $maxKey = "max";



# Section 2 — Determine state
#############################

# Go into our state decider.
# This re-routes our display and handling of data
# based on the parameters passed with the request.

# If there's an email parameter, the user's just signed up.
if (param('email')) {
	my $username = param('username');
	my $password = param('password');
	my $email = param('email');

  print "Signing up $username, $password, $email<br/>\n";
  my ($isValid, $errorMessage) = valid_user($username, $password, $email);
	if ($isValid) {
		register($username, $password, $email);
		print "<strong>Registering $username, $password, $email. Check your emails.</strong>\n";
	} else {
		print "Data entered was not valid '$errorMessage'\n";
		print sign_up_form();
	}
} elsif (isLoggedIn()) {
	print logged_in_header();

	my $searchTerm = searchPhrase();
	my $viewingProfileOf = isViewingProfile();

	if ($viewingProfileOf) {
		# Viewing the profile of a specific user
		print display_profile($viewingProfileOf);
	} elsif ($searchTerm) {
		# Searched for a username
		print search_results($searchTerm);
	} elsif (param('matches')) {
		# Viewing preference matches
		print show_matches();
	} elsif (param('editProfile')) {
		# Editing my profile
		print edit_profile();
	} elsif (param('email_message') && param('send_email_to')) {
		# Sending a message to the owner of a profile
		my $from = param('username');
		my $to = param('send_email_to');
		my $message = param('email_message');

		send_message($from, $to, $message);
		print p("Message sent!");
		print browse_screen();
	} else {
		# User not logged in.

		my $username = param('username');
		if (param('did_edit_profile')) {
			# Just finished editing our profile. We need to update the data stores.
			print p("Profile updated.");
			my $profile_text = param('profile_text');
			my $file_handle = param('filename');
			my $other_photo_filehandle = param('other_photo_filename');
			my $photo_to_delete = param('photo_to_delete');

			my $degree = param('degree');
			my $hair_colour = param('hair_colour');
			my $weight = param('weight');
			my $birthdate = param('birthdate');
			my $height = param('height');

			upload_profile_photo($username, $file_handle) if $file_handle;
			upload_other_photo($username, $other_photo_filehandle) if $other_photo_filehandle;
			delete_photo($username, $photo_to_delete) if $photo_to_delete;
			update_profile_text($username, $profile_text) if $profile_text;
			update_degree($username, $degree) if $degree;
			update_hair_colour($username, $hair_colour) if $hair_colour;
			update_weight($username, $weight) if $weight;
			update_birthdate($username, $birthdate) if $birthdate;
			update_height($username, $height) if $height;
		} elsif (param('did_suspend_account')) {
			# Suspended our account
			suspend_user($username);
			print p("Account suspended.");
		} elsif (param('did_delete_account')) {
			# Deleted our account
			delete_user($username);
			print p("Account deleted.");
		} else {
			# Home page
			print browse_screen();
		}
	}
} elsif (param('signUp')) {
	# Sign up
	print sign_up_form();
} elsif (param('recover_account')) {
	# Unsuspending an account
	my $username = param('username');
	if ($username && param('password')) {
		unsuspend_user($username);
		print p("Unsuspended $username. Please log in again to access the site.");
	} else {
	 	print p("Please provide your username and password.");
	}
} else {
	# Resetting a password
	if (param('reset_password') && param('reset_username')) {
		print "Resetting password now...";
		reset_password(param('reset_username'));
	} elsif (param('reset')) {
		print "we have a reset request";
		my $username = username_for_reset(param('reset'));
		print reset_html($username);
	} elsif (param('password_for_reset') && param('username_for_reset')) {
		print "Saving reset password\n";
		save_reset_password(param('username_for_reset'), param('password_for_reset'));
	} else {
		# Not logged in. Display the log in page.
		print log_in_screen();
	}
}

# Get the search phrase if there is one, false otherwise.
sub searchPhrase {
	if (defined param('search')) {
		return param('search');
	}

	return 0;
}

# Checks whether a user is logged in properly
sub isLoggedIn {
	my $username = param('username');
	my $password = param('password');

	if (defined $username && defined $password) {
		return isCorrectPassword($username, $password);
	} else {
		return 0;
	}
}

# Validates the given username and password
sub isCorrectPassword {
	my $username = shift;
	my $password = shift;

	if (get_password($username)) {
		if ($password eq get_password($username)) {
			return 1;
		}
	} else {
		# print "password not defined for '$username'\n";
	}

	return 0;
}

# Checks whether the user wants to view a profile.
# Returns the username to display if so.
sub isViewingProfile {
	return param('profile');
}

print page_trailer();
exit 0;



# Section 3 — HTML display
# ########################

#
# Gets the HTML to reset a password
#
sub reset_html {
	my $username = shift;
	chomp $username;
	return start_form , p("Password") , textfield("password_for_reset"),
				 hidden(-name => 'username_for_reset',  -default => [$username]),
				 submit("Submit"), end_form;
}


#
# Gets the HTML search results
#

sub search_results {
	my $searchTerm = shift;
	print p("Searching for '$searchTerm'...<br/>\n");
	my @results = searchData($searchTerm);
	my $html = ul(li(\@results)) . "\n";
	foreach $user (@results) {
		$html .= profile_snippet_html($user);
	}
	return $html;
}

# HTML placed at top of every screen
sub page_header {
	# return header, "<html><head><title>LOVE2041</title><style src = 'styles.css'>",
	# "<meta name = 'viewport' content = 'width=device-width'/></head><body>",
	# "<center><h1>LOVE2041</h1></center>";
	return header,
   		start_html("-title"=>"LOVE2041", -style=>{'src'=>"styles.css"}),
   		'<meta name="viewport" content="width=device-width"/>', # Responsive design
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

	$html .= "<script>";
	$html .= scripts();
	$html .= "</script>";
	$html .= hidden(-name => 'username',  -default => [param('username')], -id => "usernameSecret");
	$html .= hidden(-name => 'password',  -default => [param('password')], -id => "passwordSecret");
	$html .= end_form . "\n";
	$html .= end_html;
	return $html;
}

#
# The header for logged in users.
#
sub logged_in_header {
	return "<div class = 'loggedInHeader'>", search_field(), home_button(), matches_button(), edit_profile_button(),  logout_button(), "</div>";
}

#
# Our log in page
#
sub log_in_screen {
	return "<div class = 'login'>", start_form, "\n",
	p("Username"), textfield('username'), "<br/>\n",
	p("Password"), input({-name => 'password', -type => 'password'}), "<br/>\n",
	submit({ -value => 'Log in', -class => 'loginButton'}), "\n",
	"<br/>",
	"<button name = 'signUp' value = 'true' class = 'signUpButton'>Sign Up</button>",
	"<br/><br/>", "\n",
	"<button name = 'recover_account' value = 'true' class = 'renew'>Renew suspended account.</button>",
	"<br/>", "<br/>", "\n",
	"<div class = 'resetPassword'>",
	"<strong>Reset password</strong>",
	p("Username"), textfield('reset_username'),
	"<button name = 'reset_password' value = 'true'>Reset password</button>", "</div>",
	end_form, "\n", "</div>";
}

#
# Our sign up form
#
sub sign_up_form {
	return start_form, "\n",
	"Username", textfield('username'), "<br/>\n",
	"Password", textfield('password'), "<br/>\n",
	"Email", textfield('email'), "<br/>\n",
	submit('Sign up'), "\n",
	end_form, "\n";
}

#
# Display of full profiles
#
sub display_profile {
	my $username = shift;
	my $html = full_profile_html($username);
	print $html;
}

#
# The matches for this user
#
sub show_matches {
	my $username = param('username');
	my $value = param('matches');

	my @myMatches = matches(\%studentsHash, \%preferencesHash, $username);

	my $limit = looks_like_number($value) ? $value : 10;
	my $html = match_html($limit, @myMatches);
	print $html;
}

#
# The 'news feed' style home page.
# Lists all of the users with a photo and minimal information.
# Includes links to their full profiles.
#
sub browse_screen {
	my $n = param('n') || 0;
	my @students = sort keys %studentsHash;
	my $listOfProfiles = "";
	my $stopLimit = $n + 10;

	if ($stopLimit > (keys %studentsHash)) {
		return p("End of the road."),
			start_form,
			hidden(-name => 'username',  -default => [param('username')], -id => "usernameSecret"),
			hidden(-name => 'password',  -default => [param('password')], -id => "passwordSecret");
			end_form;
	}

	foreach $i ($n..$n+10) {
		my $student = $students[$i];
		$listOfProfiles .= profile_snippet_html($student) . "\n\n";
	}

	return $listOfProfiles,
		"\n",
		"<input type = 'hidden' name = 'n' value = '$stopLimit'/>",
		submit('Next'),"\n",
		p, "\n";
}

#
# Edit profile page
#
sub edit_profile {
	# my $form .= "<p>Photo: <input type = 'file' name = 'photo'/></p>";

	my $delete_section = h3("Delete images") . p("Please select an image to delete");
	my @photos = other_photos(param('username'));
	foreach (@photos) {
		$delete_section .= "<input type = 'radio' name = 'photo_to_delete' value = '$_'>";
		$delete_section .= "<img src = '$_' width = '75px' height = '75px'/>";
		$delete_section .= "<br/>";
	}

	return h1("Edit Profile"), h3("Profile Photo"), filefield('filename'),
	h3("Profile text"), textfield('profile_text'), $delete_section,
	"<br/><br/>",
	h3("Degree"), textfield('degree'),
	h3("Hair Colour"), textfield('hair_colour'),
	h3("Weight"), textfield('weight'),
	h3("Birthdate"), textfield('age'),
	h3("Height"), textfield('height'),
	h3("Other photos"), filefield('other_photo_filename'),
	"<br/>", "<br/>",
	"<input type = 'submit' name = 'did_edit_profile' value = 'Submit' class = 'submitButton'></input>", "<br/>", "<br/>",
	h1("Account Management"),
	h3("Suspend Account"),
	"<input type = 'submit' name = 'did_suspend_account' value = 'Suspend Account'/>", "<br/><br/>", "\n",
	h3("Delete Account"),
	"<input type = 'submit' name = 'did_delete_account' value = 'Delete Account'/>", "\n";
}

#
# Search box
#
sub search_field {
	# return start_form, "<div class = 'search_area'>", textfield({-name => "search", -class => "search_bar"}), "\n",
				 # submit('Search'), "</div>", end_form "\n";
	return "<div class = 'search_area'>", start_form, "\n", textfield({-name => "search", -class => "search_bar", -placeholder => "Search for users...", -id => "search_field"}), "\n",
				 submit({-name => 'Search', -class => 'search_button'}), "</div>", "\n";
}

#
# Matches button
#
sub matches_button {
	return "<button method = 'GET' name = 'matches' value = '10'>Matches</button>";
}

#
# Edit profile button
#
sub edit_profile_button {
	return "<button method = 'GET' name = 'editProfile' value = 'true'>Edit profile</button>";
}

#
# Log out button
#
sub logout_button {
	my $html = "<button onclick = 'logout(this)'>Log out</button>";
	return $html;
}

#
# Home button
#
sub home_button {
	my $html = "<button onclick = 'goHome()'>Home</button>";
	return $html;
}

#
# Scripts we use for the dynamic content.
# We could access external files using <script src='..'>
# We might switch to that if this approach isn't enough.
# Note that this has to be added at the end so the DOM is fully
# constructed.
#
sub scripts {
	open F, "<", "$scripts_file";
	my @lines = <F>;
	return join "", @lines;
}

#
# HTML for images
# Takes an image URL as the only parameter
#
sub image_html($) {
	my $url = shift @_;
	my $html = img({src=>$url});
	return $html;
}

#
# HTML for the person's full profile
#
sub full_profile_html($) {
	my $username = shift;
 	my $html .= "<div class = 'profile'>";
	$html .=  h2($username);

	# Display the profile photo if they have one.
	if (-e profilePhotoURL($username)) {
		$html .= image_html(profilePhotoURL($username));
	}

	# Display the degree
	$html .= degree_html(degree($username));
	$html .= "<div class = 'detailProfile' id = '$username'>";
	$html .= profile_text_html(profile_text($username));
	# Display physical attributes
	$html .= hair_color_html(hairColor($username));
	$html .= weight_html(weight($username));
	$html .= age_html(birthdate($username));
	$html .= height_html(height($username));

	# Display favorite books, movies, tv shows, bands, hobbies, etc.
	$html .= hobbies_html(favourite_hobbies($username));
	$html .= books_html(favourite_books($username));
	$html .= tv_shows_html(favourite_TV_shows($username));
	$html .= bands_html(favourite_bands($username));
	$html .= movies_html(favourite_movies($username));

	$html .= other_photos_html(other_photos($username));

	$html .= "<br/><br/>";

	$html .= h3("Send message");
	$html .= textarea('email_message');
	$html .= hidden(-name => 'send_email_to',  -default => [$username]);
	$html .= submit('Send message');

	$html .= "</div>";
	return $html;
}

#
# HTML for a snippet of the person's profile.
# Used whenever we display a list of profiles.
# (e.g. main feed, search results, matches)
#
sub profile_snippet_html($) {
	# Username
	my $username = shift;

 	my $html .= "<div class = 'profile'>";
	$html .=  h2($username);

	# Display the profile photo if they have one.
	if (-e profilePhotoURL($username)) {
		$html .= image_html(profilePhotoURL($username));
	}

	# Display the degree
	$html .= degree_html(degree($username));

	# Our collapse/expand button
	# $html .= "<button id = 'show$username' onclick = 'toggleProfile(this); return false;'>More info</button>";
	$html .= "<button method = 'GET' name='profile' value='$username'>More info</button>";
	$html .= "</div>";

	return $html;
}

#
# HTML for the person's favourite X sections
# Takes the type of preference (TV, Book, etc.) and a list of preferences
#
sub preferences_html($@) {
	my $type = shift;
	my $html = h3($type) . "\n";

	if (@_) {
		$html .= ul(li(\@_));
	} else {
		$html .= "They don't have any $type." . "\n";
	}

	return $html . "\n";
}

sub hobbies_html {
	return preferences_html("Hobbies", @_);
}

sub books_html {
	return preferences_html("Favourite books", @_);
}

sub movies_html {
	return preferences_html("Favourite movies", @_);
}

sub tv_shows_html {
	return preferences_html("Favourite TV shows", @_);
}

sub bands_html {
	return preferences_html("Favourite bands", @_);
}

#
# Generic function to display a list of images
#
sub image_list_html {
	if (@_) {
		my $html = h3("Images") . "\n";
		# $html .= ul(li(\@_)));
		foreach (@_) {
			if (-e $_) {
				$html .= img({src=>$_})
			}
		}
		return $html;
	}
}

#
# Display a list of the user's other photos
#
sub other_photos_html {
	return image_list_html(@_);
}

#
# HTML to display the user's degree(s?)
# Takes a list of degrees
#
sub degree_html($) {
	my $degree = shift;
	return h4($degree) . "\n" if $degree ne "0";
}

#
# HTML to display generic attributes consistently
# Takes the kind of attribute, and the value
#
sub attribute_html($$) {
	my $type = shift;
	my $value = shift;

	if (defined $type && defined $value && $value ne "0") {
		my $html = strong($type). ": ";
		$html .= $value . "<br/>\n";
		return $html;
	}
}

#
# HTML to display the user's hair color
# Takes the hair color
#
sub hair_color_html($) {
	my $hairColorKey = "Hair color";
	my $value = shift;
	return attribute_html($hairColorKey, $value);
}

#
# HTML to display the user's height
# Takes the height
#
sub height_html($) {
	my $heightKey = "Height";
	my $value = shift;
	return attribute_html($heightKey, $value);
}

#
# HTML to display the user's weight
# Takes the weight
#
sub weight_html($) {
	my $weightKey = "Weight";
	my $value = shift;
	return attribute_html($weightKey, $value);
}

#
# HTML to display the user's age
# Takes the age
#
sub age_html($) {
	my $ageKey = "Age";
	my $value = shift;
	return attribute_html($ageKey, $value);
}

#
# HTML to display the user's gender
# Takes the gender
#
sub gender_html($) {
	my $genderKey = "Gender";
	my $value = shift;
	return attribute_html($genderKey, $value);
}

#
# HTML to display the user's profile text
# Takes the profile text
#
sub profile_text_html($) {
	my $textKey = "Profile text";
	my $value = shift;
	return attribute_html($textKey, $value);
}

#
# Displays the list of matches for a user.
# Takes the number of matches to return (< matches.length)
# and the list of matches.
#
sub match_html {
	my $limit = shift;
	my @matches = @_;
	my $html = "";
	$html .= h2("Matches");
	my $i = 0;
	while ($i < $limit && $matches[$i]) {
		my $username = $matches[$i];
		$html .= profile_snippet_html($username);

		$i++;
	}
	return $html;
}

# Section 4 — Data Retrieval
# ##########################

#
# The user's profile photo URL
#
sub profilePhotoURL($) {
 	my $username = shift;
	my $profilePhotoURL = $students_dir . "/" . $username . "/profile.jpg";
	return $profilePhotoURL;
}

#
# A list of the user's other photos
#
sub other_photos($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$photosKey}) {
		return @{$studentsHash{$username}{$photosKey}};
	}
}

#
# The user's degree
#
sub degree($) {
	my $username = shift;
	return $studentsHash{$username}{$degreeKey};
}

#
# The user's hair color
#
sub hairColor($) {
	my $username = shift;
	my $hairColor = $studentsHash{$username}{$hairColorKey};
	return $hairColor;
}

#
# The user's height
#
sub height($) {
	my $username = shift;
	my $height = $studentsHash{$username}{$heightKey};
	return $height;
}

#
# The user's weight
#
sub weight($) {
	my $username = shift;
	my $weight = $studentsHash{$username}{$weightKey};
	return $weight;
}

#
# The user's age
#
sub birthdate($) {
	my $username = shift;
	my $date = $studentsHash{$username}{$birthdateKey};
	return $date;
}

#
# The user's gender
#
sub gender($) {
	my $username = shift;
	my $gender = $studentsHash{$username}{$genderKey};
	return $gender;
}

#
# The user's profile text
#
sub profile_text($) {
	my $username = shift;
	my $text = $studentsHash{$username}{$profileTextKey};
	return $text;
}

#
# The user's password
# [PRIVATE]
#
sub get_password($) {
	my $username = shift;
	my $password = $studentsHash{$username}{$passwordKey};
	return $password;
}

#
# The user's email
# [PRIVATE]
#
sub get_email($) {
	my $username = shift;
	my $email = $studentsHash{$username}{$emailKey};
	return $email;
}

#
# A list of the user's favourite books
#
sub favourite_books($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$booksKey}) {
		return @{$studentsHash{$username}{$booksKey}}
	}
}


#
# A list of the user's favourite bands
#
sub favourite_bands($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$bandsKey}) {
		return @{$studentsHash{$username}{$bandsKey}}
	}
}

#
# A list of the user's favourite tv shows
#
sub favourite_TV_shows($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$tvShowsKey}) {
		return @{$studentsHash{$username}{$tvShowsKey}}
	}
}

#
# A list of the user's favourite hobbies
#
sub favourite_hobbies($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$hobbiesKey}) {
		return @{$studentsHash{$username}{$hobbiesKey}}
	}
}

#
# A list of the user's favourite movies
#
sub favourite_movies($) {
	my $username = shift;
	if (defined $studentsHash{$username}{$moviesKey}) {
		return @{$studentsHash{$username}{$moviesKey}}
	}
}

#
# Searching for a person's name
#
sub searchData($) {
	my $searchTerm = shift;
	my @results = ();

	foreach $key (keys %studentsHash) {
		if ($key =~ /$searchTerm/i) {
			push @results, $key;
		}
	}

	return @results;
}

# Section 5 — Data updating
# #########################

#
# User account updating and creation.
#
#
# Register a new user.
# Takes username, password, and email.
#
sub register {
	my $username = shift;
	my $password = shift;
	my $email = shift;

	# Send the email to confirm their account.
	my $secret = confirmation_email($username, $email);

	# Save their details to file.
	save_data($username, $password, $email, $secret);
}

#
# Update a user's information
#
sub update_single_attribute {
	my $username = shift;
	my $key = shift;
	my $value = shift;

	open G, "<", "$students_dir/$username/profile.txt" or die "Couldn't open user '$username' profile.";
	my @profile = <G>;
	my $i = 0;
	# Find whether the user has a value for this key already
	while ($i < @profile) {
		if ($profile[$i] eq "$key:\n") {
			splice @profile, $i, 1;
			splice @profile, $i, 1;
			last;
		}

		$i++;
	}
	close G;
	open F, ">", "$students_dir/$username/profile.txt" or die "Couldn't open user's profile.";

	splice @profile, $i, 0, data_field($key, $value);

	foreach (@profile) {
		print F $_;
	}

	close F;
}

#
# Update profile text
#
sub update_profile_text {
	my $username = shift;
	my $text = shift;
	$text = clean_input($text);
	update_single_attribute($username, "profile_text", $text);
}

#
# A series of functions to update simple attributes about the user
#
sub update_degree {
	update_single_attribute(shift, $degreeKey, clean_input(shift));
}

sub update_hair_colour {
	update_single_attribute(shift, $hairColorKey, clean_input(shift));
}

sub update_birthdate {
	update_single_attribute(shift, $birthdateKey, clean_input(shift));
}

sub update_weight {
	update_single_attribute(shift, $weightKey, clean_input(shift));
}

sub update_height {
	update_single_attribute(shift, $heightKey, clean_input(shift));
}

#
# Sanitizes input to help prevent XSS attacks.
#
sub clean_input {
	my $text = shift;

	# Switch all of the angle brackets for lt and gt
	$text =~ s/</&lt;/g;
	$text =~ s/>/&gt;/g;

	# We only want to allow some basic HTML tags, so we swap these back
	$text =~ s/&lt;(strong|b|i|em)&gt;/<$1>/g;
	$text =~ s/&lt;\/(strong|b|i|em)&gt;/<\/$1>/g;

	return $text;
}

#
# Saves the user's details to the file
#
sub save_data {
	my $username = shift;
	my $password = shift;
	my $email = shift;
	my $secret = shift;

	if (-d "$students_dir/$username") {
		# This user already exists.
		print "<strong>This user couldn't be saved.</strong>";
	} else {
		# The user doesn't have a directory. Create it.
		mkdir "$students_dir/$username" or die "ERROR: Couldn't create directory";

		# Now save to their profile.
		open F, ">", "$students_dir/$username/profile.txt" or die "ERROR: Couldn't open file";

		print F data_field("username", $username);
		print F data_field("password", $password);
		print F data_field("email", $email);
		print F data_field("secret", $secret);
		close F;
	}
}

#
# Get a nicely formatted version of a key-value pair
#
sub data_field {
	my $key = shift;
	my $value = shift;
	return "$key:\n        $value\n";
}

#
# Validate whether the user trying to be registered is valid.
# Takes username, password, and email.
#
sub valid_user {
	my ($username, $password, $email) = (shift, shift, shift);

	if (!valid_username($username)) {
		return (0, "The username was not valid");
	} elsif (!valid_password($password)) {
		return (0, "The password was not valid");
	} elsif (!valid_email($email)) {
		return (0, "The email was not valid");
	} elsif (user_exists($username)) {
		return (0, "That username is taken");
	}

	return 1;
}

#
# Usernames have to be 1-20 characters long, containing letters, numbers
# and underscores only.
#
sub valid_username {
	my $username = shift;
	return 1 if ($username =~ /[A-Za-z0-9_]{1,20}/);
}

#
# Passwords have to be 1-128 characters long.
#
sub valid_password {
	return 1 if (shift =~ /.{1,128}/);
}

#
# Emails have to be of a standard form.
#
sub valid_email {
	return 1 if (shift =~ /^\w+@\w+(\.\w+)+/);
}

#
# Checks whether the given username already exists
#
sub user_exists {
	my $username = shift;
	return 1 if (defined $studentsHash{$username});
}

#
# Get the current URL of this script.
# Used for sending links in emails mostly
#
sub my_url {
	return $url = "http://cgi.cse.unsw.edu.au" . $ENV{"SCRIPT_URL"};
}

#
# Send a confirmation email to the person registering
#
sub confirmation_email {
	my $username = shift;
	my $address = shift;

	my $suffix = random_letters();

	my $url = my_url() . "?confirm=$suffix";
	my $content = "Hi $username,\n\nThanks for signing up for LOVE2041.\n";
	$content .= "Here's the link to confirm your account: $url.\n";

	send_email($address, $content);

	return $suffix;
}

#
# Email snippet by Andrew Taylor
#
sub send_email {
	my $recipient = shift;
	my $message = shift;

	# Remove all but characters legal in e-mail addresses
	# and reduce to maximum allowed length
	$recipient = substr($recipient, 0, 256);
	$recipient =~ s/[^\w\.\@\-\!\#\$\%\&\'\*\+\-\/\=\?\^_\`\{\|\}\~]//g;
	$message =~ s/\`//g;
	$message =~ s/</&lt;/g;
	$message =~ s/>/&gt;/g;

	open F, '|-', 'mail', '-s', 'LOVE2041', $recipient or die "Can not run mail";
	print F "$message\n";
	close F;
}

#
# Generate some random letters to be sent as tokens to emails
#
sub random_letters {
	my @chars = ("A".."Z", "a".."z");
	my $string;
	$string .= $chars[rand @chars] for 1..8;
	return $string;
}

#
# Given a file name and file handle, saves that file as the user's profile photo
#
sub upload_file {
	my $filename = shift;
	my $file_handle = shift;

	open F, ">", $filename or die "Couldn't open file to save photo.";

	my $data = join("", <$file_handle>);
	print F $data;
	close F;

	print "Uploaded photo.";
}

#
# Update a user's profile photo
#
sub upload_profile_photo {
	my $username = shift;
	my $file_handle = shift;
	my $file = "$students_dir/$username/profile.jpg";
	upload_file($file, $file_handle);
}

#
# Add a photo to the user's other photos
#
sub upload_other_photo {
	my $username = shift;
	my $file_handle = shift;

	my @other_photos = other_photos($username);
	my $i = 0;

	# Get the last other photo filename in the directory
	my $lastFile = $other_photos[@other_photos - 1];
	print "last file '$lastFile'\n";
	# Photo filenames are of the format photo01.jpg (for example)
	$lastFile =~ /([0-9]{2})\.jpg$/;
	my $num = $1 + 1;
	print "num is '$num'\n";

	my $new_filename = "$students_dir/$username/photo";

	if ($num < 10) {
		$new_filename .= "0$num";
	} else {
		$new_filename .= $num;
	}

	$new_filename .= ".jpg";
	print "fn '$new_filename'\n";
	upload_file($new_filename, $file_handle);
}

#
# Given a filename and username, delete's the file.
#

sub delete_photo {
	my $username = shift;
	my $filename = shift;

	# We can't just use the filename path directly because a user could
	# mess with us. We grab the file's actual name, then reconstruct the path
	# to it using the username.
	$filename =~ /\/([^\/]+).jpg$/;
	my $name = $1;
	my $path = "$students_dir/$username/$name.jpg";

	if (-e $path) {
		# Delete the file
		unlink $path;
		print "Deleted file $path";
	} else {
		print "didn't delete file $path";
	}
}

#
# Given a username, suspend that account.
# We do this by moving the directory into a 'suspended' folder.
#
sub suspend_user {
	my $username = shift;

	if (-d "$students_dir/$username") {
		rename ("$students_dir/$username", "$suspended_dir/$username");
	}
}

#
# Given a username, unsuspends that account.
#
sub unsuspend_user {
	my $username = shift;

	if (-d "$suspended_dir/$username") {
		rename("$suspended_dir/$username", "$students_dir/$username");
	}
}


#
# Delete a user
#
sub delete_user {
	my $username = shift;
	if (-d "$students_dir/$username") {
		rename("$students_dir/$username", "$deleted_dir/$username");
	}
}

#
# Reset a user's password
#
sub reset_password {
	print "In the reset subro";
	my $username = shift;
	my $email = $studentsHash{$username}{$emailKey};
	if ($email) {
		my $random = random_letters();
		my $url = my_url . "?reset=" . $random;
		print "Sending you an email...";
		my $message = "Hi $username,\nA request to reset your account for LOVE2041 was made recently.\n" .
		              "If you'd like to continue with this request, please click this link: $url." .
		              "\n\n" .
		              "Ignore this message if it was sent to you by mistake.";
    send_email($email, $message);
    open F, ">>", $reset_file;
    print F "$random:$username\n";
    close F;
	} else {
		print p("We can't reset this account because there is no email address associated with it.");
	}
}

#
# Gets the username from the reset requests file for the code we received.
#
sub username_for_reset {
	my $code = shift;
	open F, "<", $reset_file;
	while (<F>) {
		if ($_ =~ /^$code/) {
			# Now get the username from here.
			my $line = $_;
			$line =~ s/$code://;
			return $line;
		}
	}
}

#
# Complete the reset password request
#
sub save_reset_password {
	my $username = shift;
	my $password = shift;
	print "Saving '$username' '$password'\n";
	update_single_attribute($username, "password", $password);
}

#
# Send an email message from one user to another
# from, to, message
#
sub send_message {
	my $from = shift;
	my $to = shift;
	my $message = shift;

	my $email = "Hi $to,\n$from sent you a message!\n\n$message";
	my $to_email = get_email($to);
	send_email($to_email, $email);
}

#
# Display the contents of the hashes.
# Useful for debugging mostly.
#
sub printHashes {
  foreach $key (keys %studentsHash) {
    print $key, " => ", $studentsHash{$key}, "\n";

    my %user = %{$studentsHash{$key}};
    foreach $k (keys %user) {
      if (ref($user{$k}) eq 'ARRAY') {
          my @arr = @{$user{$k}};
          print "    ", $k, " => ";
          foreach $i (@arr) {
            print $i, ", ";
          }
          print "\n";
        } else {
          print "    ", $k, " => ", $user{$k}, "\n";
        }
    }

    print "\nPreferences\n";
    my %preferences = %{$preferencesHash{$key}};
    foreach $pref (keys %preferences) {
      print "         ", $pref, " => ", $preferences{$pref}, "\n";
    }
    print "\n\n\n";
  }
}
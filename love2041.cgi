#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use FindBin qw( $RealBin );
use lib $RealBin;

use ProfileImporter qw(loadHashes);
use Matchmaker qw(matches);

use CGI qw/:all/;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
use Data::Dumper;
use List::Util qw/min max/;
use Scalar::Util qw(looks_like_number);

warningsToBrowser(1);

# print start of HTML ASAP to assist debugging if there is an error in the script
print page_header();

# some globals used through the script
$debug = 1;
$students_dir = "./students";
my $scripts_file = "scripts.js";

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

# printHashes();

print "<!-- ", matches(\%studentsHash, \%preferencesHash, "AwesomeGenius60"), "-->\n\n";


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
	print "Welcome to LOVE2041\n";
	my $searchTerm = searchPhrase();
	my $viewingProfileOf = isViewingProfile();

	if ($viewingProfileOf) {
		print display_profile($viewingProfileOf);
	} elsif ($searchTerm) {
		print search_results($searchTerm);
	} elsif (param('matches')) {
		print show_matches();
	} elsif (param('editProfile')) {
		print edit_profile();
	} else {
		if (param('did_edit_profile')) {
			my $username = param('username');
			my $profile_text = param('profile_text');
			print "editing profile for $username $profile_text";
			update_profile_text($username, $profile_text) if $profile_text;

		} else {
			print browse_screen();
		}
	}
} elsif (param('signUp')) {
		print sign_up_form();
} else {
	print log_in_screen();
}

print page_trailer();
exit 0;

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

sub logged_in_header {
	return logout_button(), search_field(), home_button(), matches_button(), edit_profile_button();
}

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
		print "password not defined for '$username'\n";
	}

	return 0;
}

# Checks whether the user wants to view a profile.
# Returns the username to display if so.
sub isViewingProfile {
	return param('profile');
}

sub log_in_screen {
	return start_form, "\n",
	"Username", textfield('username'), "<br/>\n",
	"Password", textfield('password'), "<br/>\n",
	"<button name = 'signUp' value = 'true'>Sign Up</button>",
	submit('Log in'), "\n",
	end_form, "\n";
}

sub sign_up_form {
	return start_form, "\n",
	"Username", textfield('username'), "<br/>\n",
	"Password", textfield('password'), "<br/>\n",
	"Email", textfield('email'), "<br/>\n",
	submit('Sign up'), "\n",
	end_form, "\n";
}

sub display_profile {
	my $username = shift;
	my $html = full_profile_html($username);
	print $html;
}

sub show_matches {
	my $username = param('username');
	my $value = param('matches');

	my @myMatches = matches(\%studentsHash, \%preferencesHash, $username);

	my $limit = looks_like_number($value) ? $value : 10;
	my $html = match_html($limit, @myMatches);
	print $html;
}



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

sub edit_profile {
	return "Profile text", textfield('profile_text'),
	"<button type = 'submit' name = 'did_edit_profile' value = 'true'>Submit</button>", "\n";
}

#
# Search box
#
sub search_field {
	return start_form, "\n", textfield("search"), "\n",
				 submit('Search'), "\n";
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

	$html .= "<script>";
	$html .= scripts();
	$html .= "</script>";
	$html .= hidden(-name => 'username',  -default => [param('username')], -id => "usernameSecret");
	$html .= hidden(-name => 'password',  -default => [param('password')], -id => "passwordSecret");
	$html .= end_form . "\n";
	$html .= end_html;
	return $html;
}

sub logout_button {
	my $html = "<button onclick = 'logout(this)'>Log out</button>";
	return $html;
}

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
	$html .= "</div>";
	return $html;
}

#
# HTML for a snippet of the person's profile
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

sub gender_html($) {
	my $genderKey = "Gender";
	my $value = shift;
	return attribute_html($genderKey, $value);
}

sub profile_text_html($) {
	my $textKey = "Profile text";
	my $value = shift;
	return attribute_html($textKey, $value);
}

# Displays the list of matches for a user.
# Takes the number of matches to return (< matches.length)
# and the list of matches.
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

#
# Data Access
# ===========

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
sub otherPhotos($) {
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
		if ($key =~ /$searchTerm/) {
			push @results, $key;
		}
	}

	return @results;
}

#
# User account updating and creation.
#

# Register a new user.
# Takes username, password, and email.
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
sub update_profile_text {
	my $username = shift;
	my $text = shift;
	print "Updating profile text....";
	open F, ">>", "$students_dir/$username/profile.txt" or die "Couln't open user's profile.";
	print F data_field("profile_text", $text);
	close F;
}

# Saves the user's details to the file
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

sub data_field {
	my $key = shift;
	my $value = shift;
	return "$key:\n        $value\n";
}

# Validate whether the user trying to be registered is valid.
# Takes username, password, and email.
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

# Usernames have to be 1-20 characters long, containing letters, numbers
# and underscores only.
sub valid_username {
	my $username = shift;
	return 1 if ($username =~ /[A-Za-z0-9_]{1,20}/);
}

# Passwords have to be 1-128 characters long.
sub valid_password {
	return 1 if (shift =~ /.{1,128}/);
}

# Emails have to be of a standard form.
sub valid_email {
	return 1 if (shift =~ /^\w+@\w+(\.\w+)+/);
}

# Checks whether the given username already exists
sub user_exists {
	my $username = shift;
	return 1 if (defined $studentsHash{$username});
}

# Send a confirmation email to the person registering
sub confirmation_email {
	my $username = shift;
	my $email = shift;

	my $suffix = random_letters();

	my $url = "http://cgi.cse.unsw.edu.au" . $ENV{"SCRIPT_URL"} . "?confirm=$suffix";
	my $content = "Hi $username,\n\nThanks for signing up for LOVE2041.\n";
	$content .= "Here's the link to confirm your account: $url.\n";

	# Cleanup input just in case
	$username =~ s/;\`\'\"//g;
	$email =~ s/;\`\'\"//g;

	# Send the email
	`echo "$content" | mail -s LOVE2041 $email`;

	return $suffix;
}

sub random_letters {
	my @chars = ("A".."Z", "a".."z");
	my $string;
	$string .= $chars[rand @chars] for 1..8;
	return $string;
}

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
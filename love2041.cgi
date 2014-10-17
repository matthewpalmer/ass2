#!/usr/bin/perl -w

# written by andrewt@cse.unsw.edu.au September 2013
# as a starting point for COMP2041/9041 assignment 2
# http://cgi.cse.unsw.edu.au/~cs2041/assignments/LOVE2041/

use FindBin qw( $RealBin );
use lib $RealBin;

use ProfileImporter qw(loadHashes);

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

# Preferences
my $ageKey = "age";
my $hairColorPrefKey = "hair_colours";
my $minKey = "min";
my $maxKey = "max";

# printHashes();

my $pass = $studentsHash{'AwesomeGenius60'}{$passwordKey};
print "password: '", $pass, "'\n<br/>";

if (isLoggedIn()) {
	print logged_in_header();
	print browse_screen();
} else {
	print log_in_screen();
}

print page_trailer();
exit 0;

sub logged_in_header {
	return logout_button();
}

# Checks whether a user is logged in properly
sub isLoggedIn {
	my $username = param('username');
	my $password = param('password');

	if (defined $username && defined $password) {
		print "checking password...";
		return isCorrectPassword($username, $password);
	} else {
		return 0;
	}
}

# Validates the given username and password
sub isCorrectPassword {
	my $username = shift;
	my $password = shift;

	# if (password($username)) {
		print "password '$password' '", password($username), "'\n";
		if ($password eq password($username)) {
			print "<strong>Logged in...</strong><br/>\n";
			return 1;
		}
	# } else {
		# print "password not defined for '$username'\n";
	# }

	print "Not logged in usernme '$username' password '$password' data '", $studentsHash{$username}{$passwordKey}, "'\n";

	return 0;
}

sub log_in_screen {
	return start_form, "\n",
	"Username", textfield('username'), "<br/>\n",
	"Password", textfield('password'), "<br/>\n",
	submit('Log in'), "\n",
	end_form, "\n";
}

sub display_profile {
	my $username = shift;
	my $html = profile_html($username);
	print $html;
}

sub browse_screen {
	my $n = param('n') || 0;
	my @students = sort keys %studentsHash;
	my $listOfProfiles = "";
	my $stopLimit = $n + 10;

	foreach $i ($n..$n+10) {
		my $student = $students[$i];
		$listOfProfiles .= profile_html($student) . "\n\n";
	}

	return $listOfProfiles,
		hidden('n', $n + 1),"\n",
		submit('Next'),"\n",
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

	$html .= "<script>";
	$html .= scripts();
	$html .= "</script>";

	$html .= login_secret_fields();

	$html .= end_html;
	return $html;
}

sub logout_button {
	my $html = "<button onclick = 'logout(this)'>Log out</button>";
	return $html;
}

sub login_secret_fields {
	my $html = "";

	#NOTE: This might override the log in form's params??
	$html .= hidden(-name => 'username',  -default => [param('username')], -id => "usernameSecret");
	$html .= hidden(-name => 'password',  -default => [param('password')], -id => "passwordSecret");
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
	return join "\n", @lines;
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
# HTML for the person's profile
#
sub profile_html($) {
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
	$html .= "<button id = 'show$username' onclick = 'toggleProfile(this);'>Show more</button>";

	$html .= "<div class = 'detailProfile' id = '$username'>";
	# Display physical attributes
	$html .= hair_color_html(hairColor($username));
	$html .= weight_html(weight($username));
	$html .= age_html(age($username));
	$html .= height_html(height($username));

	# Display favorite books, movies, tv shows, bands, hobbies, etc.
	$html .= hobbies_html(favourite_hobbies($username));
	$html .= books_html(favourite_books($username));
	$html .= tv_shows_html(favourite_TV_shows($username));
	$html .= bands_html(favourite_bands($username));
	$html .= movies_html(favourite_movies($username));
	$html .= "</div>";
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
sub age($) {
	my $username = shift;
	my $age = $studentsHash{$username}{$ageKey};
	return $age;
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
# The user's password
# [PRIVATE]
#
sub password($) {
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
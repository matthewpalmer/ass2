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

display_profile("AwesomeGenius60");
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
	my $html = img({src=>$url});
	return $html;
}

#
# HTML for the person's profile
#
sub profile_html($) {
	# Username
	my $username = shift;

 	my $html = "<div class = 'profile'>";
	$html .=  h2($username);

	# Display the profile photo if they have one.
	if (-e profilePhotoURL($username)) {
		$html .= image_html(profilePhotoURL($username));
	}

	# Display the degree
	$html .= degree_html(degrees($username));

	# Display physical attributes
	$html .= hair_color_html(hairColor($username));
	$html .= weight_html(weight($username));
	$html .= age_html(age($username));
	$html .= height_html(height($username));
	$html .= degree_html(degrees($username));

	# Display favorite books, movies, tv shows, bands, hobbies, etc.
	# ...

	$html .= "</div>";

	return $html;
}

#
# HTML for the person's favourite X sections
# Takes the type of preference (TV, Book, etc.) and a list of preferences
#
sub preferences_html($@) {
	my $type = shift;
	my $html = h3($type);
	$html .= ul(li(@_));
	return $html;
}

#
# HTML to display the user's degree(s?)
# Takes a list of degrees
#
sub degree_html(@) {
	my $html = "";
	$html .= h4($_) . ". " foreach @_;
	return $html . "\n";
}

#
# HTML to display generic attributes consistently
# Takes the kind of attribute, and the value
#
sub attribute_html($$) {
	my $type = shift;
	my $value = shift;
	if (defined $type && defined $value) {
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
# A list of the user's degrees
#
sub degrees($) {
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
# A list of the user's favourite books
#
sub favoriteBooks($) {
	if (defined $studentsHash{$username}{$booksKey}) {
		return @{$studentsHash{$username}{$booksKey}}
	}
}


#
# A list of the user's favourite bands
#
sub favoriteBands($) {
	if (defined $studentsHash{$username}{$bandsKey}) {
		return @{$studentsHash{$username}{$bandsKey}}
	}
}

#
# A list of the user's favourite tv shows
#
sub favouriteTVShows($) {
	if (defined $studentsHash{$username}{$tvShowsKey}) {
		return @{$studentsHash{$username}{$tvShowsKey}}
	}
}

#
# A list of the user's favourite hobbies
#
sub favoriteHobbies($) {
	if (defined $studentsHash{$username}{$hobbiesKey}) {
		return @{$studentsHash{$username}{$hobbiesKey}}
	}
}

#
# A list of the user's favourite movies
#
sub favoriteMovies($) {
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
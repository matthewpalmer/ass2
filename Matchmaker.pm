#!/usr/bin/perl -w

package Matchmaker;
require Exporter;
use warnings;

@ISA = qw(Exporter);
@EXPORT = qw(&matches);
@EXPORT_OK = qw(&matches);

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

# Get a list of the user's matches
#
# 'Desperation level' will increase the range of matches. A level of 0 will
# match the critera specified below, a level of 2 will allow +- 2, etc.
# 0 is the default
#
# High rated matches
# - age preferences +- 3 years
# - hair colour preferences -- exact match
# - height +- 15 cm
# - weight +- 10kg
# - gender -- exact match
#
# Low rated matches
# - similar books, tv shows, movies, hobbies, bands
# - studying the same degree, courses
#
sub matches {
  print "\n\n<!-- START MATCHING\n";
  my $studentsRef = shift;
  my $prefsRef = shift;
  my %studentsHash = %{$studentsRef};
  my %preferencesHash = %{$prefsRef};
  my $username = shift;
  my $desperationLevel = shift || 0;

  if ($username) {
    print "username exists $username";
  } else {
    print "usernoame no eway";
  }
  return if (!$username);

  # Height matching
  my $loHeight = $preferencesHash{$username}{$heightKey}{$minKey};
  my $hiHeight = $preferencesHash{$username}{$heightKey}{$maxKey};
  $loHeight =~ s/[a-zA-Z]//g;
  $hiHeight =~ s/[a-zA-Z]//g;
  my @heightMatches = usersInHeightRange($loHeight - $desperationLevel,
                                         $hiHeight + $desperationLevel,
                                         \%studentsHash);

  # Hair matching
  my %prefs = %{$preferencesHash{$username}};
  my @hairColours = @{$prefs{$hairColorPrefKey}};
  my @hairMatches = usersWithHairColours(@hairColours, \%studentsHash);

  # Gender matching
  my $genderPreference = $preferencesHash{$username}{$genderKey};
  my @genderMatches = usersWithGender($genderPreference, \%studentsHash);

  # Weight matching
  my $loWeight = $preferencesHash{$username}{$weightKey}{$minKey};
  my $hiWeight = $preferencesHash{$username}{$weightKey}{$maxKey};
  $loWeight =~ s/[a-zA-Z]//g;
  $hiWeight =~ s/[a-zA-Z]//g;
  my @weightMatches = usersInWeightRange($loWeight - $desperationLevel,
   $hiWeight + $desperationLevel, \%studentsHash);

  # Age matching
  my $loAge = $preferencesHash{$username}{$ageKey}{$minKey} + $desperationLevel;
  my $hiAge = $preferencesHash{$username}{$ageKey}{$maxKey} + $desperationLevel;

  my @ageMatches = usersInAgeRange($loAge - $desperationLevel,
    $hiAge + $desperationLevel, \%studentsHash);

  # Interest matching
  my $interests = allInterests($username, \%studentsHash);
  my %interestMatchesHash = interestMatches($interests, \%studentsHash);
  my @usersWithSimilarInterests = keys %interestMatchesHash;

  # Education matching

  print "\nHair matches\n", join ", ", @hairMatches, "\n\n";
  print "\nHeight matches\n", join ", ", @heightMatches, "\n\n";
  print "\nGender matches\n", join ", ", @genderMatches, "\n\n";
  print "\nWeight matches\n", join ", ", @weightMatches, "\n\n";
  print "\nAge matches\n", join ", ", @ageMatches, "\n\n";

  print "\n\nMy interests are: $interests\n\n";
  print "\nInterest matches\n", join ", ", @usersWithSimilarInterests, "\n\n";

  my %attributeMatches = ();
  my @attributes = (@ageMatches, @weightMatches, @genderMatches, @hairMatches, @heightMatches);
  # Get a count of how many times each user has the attribute we want.
  # Attribute matches are worth twice as much as interest-based matches.
  $attributeMatches{$_} = ($attributeMatches{$_} || 0) + 2 foreach (@attributes);
  $attributeMatches{$_} = ($attributeMatches{$_} || 0) + 1 foreach (@usersWithSimilarInterests);
  # Sort the users based on number of matching attributes.
  my @keys = sort {$attributeMatches{$b} <=> $attributeMatches{$a}} keys (%attributeMatches);

  print "\n\n";
  foreach $key (@keys) {
    print "username: $key, match strength: ", $attributeMatches{$key}, "\n";
  }
  print "\n\n";

  # Get the first 10 matches
  @keys = @keys[0 .. 10];
  print "\nEND MATCHING-->\n\n";
  return @keys;
}

sub usersWithProperty {
  my $key = shift;
  my $desiredValue = shift;
  my $href = shift;
  my %studentsHash = %{ $href };

  my @matches = ();
  foreach $username (keys %studentsHash) {
    my %student = %{$studentsHash{$username}};
    my $value = $student{$key};

    if ($value) {
      if ($value eq $desiredValue) {
        push @matches, $username;
      }
    }
  }

  return @matches;
}

sub usersInRange {
  my $criteria = shift;
  my $min = shift;
  my $max = shift;

  my $href = shift;
  my %studentsHash = %{ $href };

  my @matches = ();
  foreach $username (keys %studentsHash) {
    my %student = %{$studentsHash{$username}};
    my $value = $student{$criteria};

    if ($value) {
      $value =~ s/[a-zA-Z]//g;
      if ($max >= $value && $min <= $value) {
        push @matches, $username;
      }
    }
  }

  return @matches;
}

sub usersInHeightRange {
  return usersInRange($heightKey, shift, shift, shift);
}

sub usersInWeightRange {
  return usersInRange($weightKey, shift, shift, shift);
}

sub usersWithGender {
  return usersWithProperty($genderKey, shift, shift);
}

sub usersInAgeRange {
  return usersInRange($ageKey, shift, shift, shift);
}

sub interestMatches {
  my $allInterests = shift;
  my $href = shift;
  my %studentsHash = %{ $href };

  my @categories = ($moviesKey, $booksKey, $hobbiesKey, $tvShowsKey, $bandsKey);
  my %matches = ();
  foreach $student (keys %studentsHash) {
    foreach $category (@categories) {
      my @arr = @{$studentsHash{$student}{$category}};
      if (@arr) {
        foreach $element (@arr) {
          if ($allInterests =~ /$element/) {
            $matches{$student}++;
          }
        }
      }
    }
  }

  return %matches;
}

# Gets all of a user's interests into a single string
# - movies
# - books
# - hobbies
# - tv shows
# - bands
sub allInterests {
  my $username = shift;
  my $href = shift;
  my %studentsHash = %{ $href };
  my @categories = ($moviesKey, $booksKey, $hobbiesKey, $tvShowsKey, $bandsKey);
  my $interests = "";

  my %student = %{$studentsHash{$username}};

  foreach $category (@categories) {
    $interests .= "---";
    my @values = @{$student{$category}};
    if (@values) {
      $interests .= join ";-;", @values;
    }
  }

  return $interests;
}

sub usersWithHairColours {
  my $href = shift;
  my %studentsHash = %{ $href };
  my @desiredValues = @_;

  my %colours = ();
  $colours{$_} = 1 foreach @desiredValues;

  my @matches = ();
  foreach $username (keys %studentsHash) {
    my %student = %{$studentsHash{$username}};
    my $value = $student{$hairColorKey};

    if ($colours{$value}) {
      push @matches, $username;
    }
  }

  return @matches;
}
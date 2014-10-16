#!/usr/bin/perl -w

package ProfileImporter;
use Sub::Exporter;
use warnings;

Sub::Exporter::setup_exporter({ exports => [ qw(loadHashes) ]});

# Globals
my $students_dir = "students";

# Our hashes for storing the users' data. Both are indexed by username.
# my %preferencesHash = ();
# my %studentsHash = ();

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

# loadHashes();
# printHash();

sub loadHashes {
  my %studentsHash = ();
  my %preferencesHash = ();

  # Our data directory
  my @students = glob("$students_dir/*");

  # Load each student's information into the studentsHash
  foreach $student (@students) {
    print "Getting $student...\n";
    $student =~ /\/([a-zA-Z_0-9]+)/;
    my $username = $1;
    my @photos = ();

    foreach $file (glob("$student/*")) {
      if ($file =~ /\.jpg$/) {
        if ($file =~ /profile.jpg$/) {
          $studentsHash{$username}{$profilePhotoKey} = $file;
        } else {
          push @photos, $file;
        }
      } elsif ($file =~ /profile.txt$/) {
        # Load the contents of their profiles into the hashes.
        open F, "<", $file or die "Couldn't open file.\n";
        my @profile = <F>;

        $studentsHash{$username}{$realNameKey} = realName(@profile);
        $studentsHash{$username}{$birthdateKey} = birthdate(@profile);
        $studentsHash{$username}{$heightKey} = height(@profile);
        $studentsHash{$username}{$genderKey} = gender(@profile);
        $studentsHash{$username}{$weightKey} = weight(@profile);
        $studentsHash{$username}{$passwordKey} = password(@profile);
        $studentsHash{$username}{$hairColorKey} = hairColor(@profile);
        $studentsHash{$username}{$emailKey} = email(@profile);
        $studentsHash{$username}{$degreeKey} = degree(@profile);

        my @bands = bands(@profile);
        my @shows = tvShows(@profile);
        my @movies = movies(@profile);
        my @hobbies = hobbies(@profile);
        my @books = books(@profile);
        my @courses = courses(@profile);

        $studentsHash{$username}{$bandsKey} = \@bands;
        $studentsHash{$username}{$tvShowsKey} = \@shows;
        $studentsHash{$username}{$moviesKey} = \@movies;
        $studentsHash{$username}{$hobbiesKey} = \@hobbies;
        $studentsHash{$username}{$booksKey} = \@books;
        $studentsHash{$username}{$coursesKey} = \@courses;

        close F;
      } elsif ($file =~ /preferences.txt$/) {
        # Load the contents of their preferences into the hashes.

        open F, "<", $file or die "Couldn't open file.\n";
        my @preferences = <F>;

        my ($minWeight, $maxWeight) = weightPreferences(@preferences);
        my ($minAge, $maxAge) = agePreferences(@preferences);
        my ($minHeight, $maxHeight) = heightPreferences(@preferences);
        my $genderPref = genderPreference(@preferences);
        my @hairColorPreferences = hairColorPreferences(@preferences);

        $preferencesHash{$username}{$weightKey}{$minKey} = $minWeight;
        $preferencesHash{$username}{$weightKey}{$maxKey} = $maxWeight;
        $preferencesHash{$username}{$ageKey}{$minKey} = $minAge;
        $preferencesHash{$username}{$ageKey}{$maxKey} = $maxAge;
        $preferencesHash{$username}{$heightKey}{$minKey} = $minHeight;
        $preferencesHash{$username}{$heightKey}{$maxKey} = $maxHeight;
        $preferencesHash{$username}{$genderKey} = $genderPref;
        $preferencesHash{$username}{$hairColorPrefKey} = \@hairColorPreferences;
      }

      $studentsHash{$username}{$photosKey} = \@photos;
    }
  }

  return (\%studentsHash, \%preferencesHash);
}

# Generic (min, max) tuple getter
sub minMaxTuple {
  my $min;
  my $max;
  my $i = 0;
  my $keyword = shift;
  my @values = listOfAttributes($keyword, @_);

  if (@values) {
    while ($i < @values) {
      if ($values[$i] =~ "min") {
        $min = $values[$i + 1];
      } elsif ($values[$i] =~ "max") {
        $max = $values[$i + 1];
      }

      $i++;
    }

    $min =~ s/\s+//;
    $max =~ s/\s+//;
    chomp $min;
    chomp $max;
    return ($min, $max);
  }
}

# Returns a (min, max) tuple
sub weightPreferences {
  my ($min, $max) = minMaxTuple("weight", @_);
  return ($min, $max);
}

sub agePreferences {
  return minMaxTuple("age", @_);
}

sub heightPreferences {
  return minMaxTuple("height", @_);
}

sub hairColorPreferences {
  my @values = listOfAttributes("hair_colours");
  print @values;
  return @values;
}

sub genderPreference {
  return singleAttribute("gender", @_);
}

# Captures the series of lines following the given keyword, up until the next
# non-indented line.
sub listOfAttributes($@) {
  my $keyword = shift;

  my @lines = ();
  my $i = 0;

  while ($i < @_) {
    if ($_[$i] eq $keyword . ":\n") {
      $i++;

      # We've matched a keyword.
      # Go on a run, adding all of the lines up to the next non-indented line
      # to the array.
      while ($i < @_) {
        my $line = $_[$i];

        if ($line !~ /^\s{1,}/) {
          last;
        }

        $line =~ s/^\s+//;
        chomp $line;
        push @lines, $line;
        $i++;
      }
    }

    $i++;
  }

  return @lines;
}

# A convenient way to get single line attributes, e.g. real name, birthdate.
sub singleAttribute($@) {
  my $keyword = shift;
  my @attributes = listOfAttributes($keyword, @_);
  return $attributes[0] if scalar(@attributes);
}

# Get data about the user from their profile
sub realName {
  return singleAttribute("name", @_);
}

sub birthdate {
  return singleAttribute("birthdate", @_);
}

sub height {
  return singleAttribute("height", @_);
}

sub weight {
  return singleAttribute("weight", @_);
}

sub gender {
  return singleAttribute("gender", @_);
}

sub password {
  return singleAttribute("password", @_);
}

sub hairColor {
  return singleAttribute("hair_color", @_);
}

sub email {
  return singleAttribute("email", @_);
}

sub degree {
  return singleAttribute("degree", @_);
}

sub tvShows {
  return listOfAttributes("favourite_TV_shows", @_);
}

sub movies {
  return listOfAttributes("favourite_movies", @_);
}

sub hobbies {
  return listOfAttributes("favourite_hobbies", @_);
}

sub books {
  return listOfAttributes("favourite_books", @_);
}

sub courses {
  return listOfAttributes("courses", @_);
}

sub bands {
  return listOfAttributes("favourite_bands", @_);
}

sub printHash {
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

# Return true for the package.
return 1;
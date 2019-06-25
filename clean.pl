#!/usr/bin/perl
# clean.pl
#
# Make ugly Latin look good (by putting js and vs back in)
#
# Usage: perl latin.pl filename.html
#
# There must be a subdirectory named "fixed" in your working directory
# (that's where the fixed file will go, logically enough).
#
# AUTHOR: Jonathan Craven
#
#    This program is free software; you can redistribute it and/or modify it
#    under the terms of the GNU General Public License as published by the
#    Free Software Foundation; either version 2 of the License, or (at your
#    option) any later version.
#
#    This program is distributed in the hope that it will be useful, but
#    WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY
#    or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
#    for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program (gpl.license.txt); if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
use strict;

my $ucv = "AEIOUY";
my $lcv = "aeiouy";
my $i;
foreach $i (0 .. $#ARGV) {

    my $infile = $ARGV[$i];
    $infile =~ m/^(.*)\..*$/;
    my $outfile = "fixed/$1.html";
    open(INFILE, "<", $infile)
    or die "Couldn't open infile: $infile";
    open(OUTFILE, ">", $outfile)
    or die "Couldn't open outfile: $outfile";
    while (<INFILE>) {

	########################################
	# Preliminary steps
	########################################
	
	# HTML reworking for the Latin Library
	s|href="http://www.thelatinlibrary.com/latinlibrary.css"|href="../latin.css"|;
	s|href="http://www.thelatinlibrary.com/latinlibrary_print.css"|href="../print.css"|;
	s|href="http://www.thelatinlibrary.com/|href="http://latin.craven.fr/|g;
	s|The Latin Library|Index|;
	s|The Classics Page||;
	
	# This simplifies later regexps
	s/^/ /; 
	s/<p>/<p> /; 
	s/<span class="pentameter_line">/<span class="pentameter_line"> /;
	
	########################################
	# Now on to the Latin     
	########################################
	
	# Change i to j when a semivowel
	s/ i([aeouy])/ j$1/g;
	s/ I([aeouy])/ J$1/g;
	s/ I([AEOUVY])/ J$1/g;
	s/ (ab|ad|in|de|con|ob|sub|e|pro|inter)i([aeouy])/ $1j$2/g;
	s/ (Ab|Ad|In|De|Con|Ob|Sub|E|Pro|Inter)i([aeouy])/ $1j$2/g;
	s/ (AB|AD|IN|DE|CON|OB|SUB|E|PRO|INTER)I([AEOUVY])/ $1J$2/g;
	
	s/ ieiun/ jejun/g;
	s/ Ieiun/ Jejun/g;
	s/ IEIUN/ JEJUN/g;
	s/ IEIVN/ JEJUN/g;
	
	s/ ju(s|ris|ri|re)iu/ ju$1ju/g;
	s/ ju(s|ris|ri|re)iu/ Ju$1ju/g;
	s/ JU(S|RIS|RI|RE)IU/ JU$1JU/g;
	s/ JV(S|RIS|RI|RE)IV/ JU$1JU/g;
	
	s/eius /ejus /g;
	s/EIUS /EJUS /g;
	s/EIVS /EJUS /g;
	s/ eius/ ejus/g;
	s/ Eius/ Ejus/g;
	s/ EIUS/ EJUS/g;
	s/ EIVS/ EJUS/g;
	
	s/cuius /cujus /g;
	s/CUIUS /CUJUS /g;
	s/CVIVS /CUJUS /g;
	s/ cuius/ cujus/g;
	s/ Cuius/ Cujus/g;
	s/ CUIUS/ CUJUS/g;
	s/ CVIVS/ CUJUS/g;
	
	s/huius /hujus /g;
	s/HUIUS /HUJUS /g;
	s/HVIVS /HUJUS /g;
	s/ huius/ hujus/g;
	s/ Huius/ Hujus/g;
	s/ HUIUS/ HUJUS/g;
	s/ HVIVS/ HUJUS/g;
	
	s/maius/majus/g;
	s/ Maius/ Majus/g;
	s/MAIUS/MAJUS/g;
	s/MAIVS/MAJUS/g;
	
	s/maior/major/g;
	s/ Maior/ Major/g;
	s/MAIOR/MAJOR/g;
	
	# Troy and Trajan
	s/ Tr([ao])i([$lcv])/ Tr$1j$2/g;
	s/ TR([AO])I([$ucv])/ TR$1J$2/g;
	
	# Get some of the more obvious Vs
	s/V([BCDFGHKLMNPQRSTXZ])/U$1/gi;
	s/([CBDPGFHJKLMQRSTZ])V/$1U/g; # prefixes will be changed back below
	
	# Change u's to v's
	# This is much harder, since distinguishing a case like "servum" from "actuum"
	# or uvae from vulnus is hard to generalise.  
	s/ u([$lcv])/ v$1/g;
	s/ U([$lcv$ucv])/ V$1/g;
	s/([$ucv$lcv])u([$lcv])/$1v$2/g;
	s/([$ucv])U([$ucv])/$1V$2/g;	
	# This list will have to grow as more mistakes are found
	s/ ([Ss])eru([ou])/ $1erv$2/;
	s/ ([Cc])alu([oiu])/ $1alv$2/;
	s/ vu([$lcv])/ uv$1/;
	s/diviu([$lcv])/diviv$1/;
	s/ (ab|ad|in|con|ob|ser|sub|cor|par|inter)u([$lcv])/ $1v$2/g;
	s/ (Ab|Ad|In|Con|Ob|Ser|Sub|Cor|Par|Inter)u([$lcv])/ $1v$2/g;
	s/ (AB|AD|IN|CON|OB|SER|SUB|COR|PAR|INTER)U([$ucv])/ $1V$2/g;
	
	# Join ae
	s/AE/&AElig;/g;
	s/Ae/&AElig;/g;
	s/ae/&aelig;/g;
	
	########################################
	# Undo any overenthusiastic replacements
	########################################
	
	# Get most Hebrew exceptions (Israel, Joel, etc.) that should not be joined.
	# This list should surely be augmented.
	s/&AElig;L /AEL /g; 
	s/&aelig;l /ael /g;
	
	# Roman numerals should not have J or U in them.
	# For now, we'll assume we don't have to bother with lowercase numerals.
	s/XCU/XCV/;
	s/CMU/CMV/;
	s/([ >])JU([ .:,<])/$1IV$2/g;
	s/([ >])([CM])U([ .:,<])/$1$2V$3/g;
	s/([ >])([M])UII([ .:,<])/$1$2VII$3/g;
	s/([ >])([CM])UII([ .:,<])/$1$2VII$3/g;
	s/([ >])([CM])UIII([ .:,<])/$1$2VIII$3/g;
	
	# eo
	s/ju([ie])/iv$1/g;
	s/ Ju([ie])/ Iv$1/g;
	s/JU([IE])/IV$1/g;
	s/jen(s|t)/ien$1/g;
	s/ Jen(s|t)/ Ien$1/g;
	s/JEN(S|T)/IEN$1/g;
	
	s/objer/obier/g;
	s/ Objer/ Obier/g;
	s/OBJER/OBIER/g;

	# Odds and ends
	s/ Nammej([$lcv])/ Nammei$1/g;
	
	# We can't be sure about CUI, so we'll just warn the user to check up on it.
	if (/[ >]CUI[ \.:,<^]/) {
	    print("Warning: found CUI in $outfile, check to make sure it's not a numeral:\n$_");
	}
	print OUTFILE;
    }    
    close(INFILE);
    close(OUTFILE);

}
0;

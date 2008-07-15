#!/usr/bin/perl
# Created:20080708
# By Jeff Connelly
#
# Parse a .pads file and make a wiki table of the pins
while(<>)
{
    chomp;
    last if $_ eq "*NET*";
}
while(<>)
{
    if (m/^[*]SIGNAL[*] (.*)/)
    {
        $signals{$signal} = [ @pins ];
        $signal = $1;
        @pins = ();
    } else {
        push @pins, split /\s+/;
    }
}

print <<EOF;
{| class="wikitable"
! Net !! Connections
|-|
EOF
for my $signal (sort keys %signals)
{
    #print "$signal: @{$signals{$signal}}\n";
    print "| $signal || @{$signals{$signal}}\n";
    print "|-|\n";
}

print "|}\n";

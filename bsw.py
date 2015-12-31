#!/usr/bin/python

import urllib
import json

URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"

raw = urllib.urlopen(URL)

jresponse = json.load(raw)


# current activity
G = jresponse['0']['G']['Scale']
R = jresponse['0']['R']['Scale']
S = jresponse['0']['S']['Scale']

predictDate = jresponse['0']['DateStamp']
predictTime = jresponse['0']['TimeStamp']

print "current Geomagnetic Storm status:     %s" % G
print "current Solar Radiation Storm status: %s" % S
print "current Radio Blackout status:        %s" % R

print "prediction date/time: %s %s UTC" % (predictDate, predictTime)

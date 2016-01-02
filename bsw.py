#!/usr/bin/python

import urllib
import json
from subprocess import check_output
from argparse import ArgumentParser
from collections import namedtuple

# the terms 'current' and 'next' are used through out in comments and variable and function names
# for purposes of this script, 'current' means the scale/color that is CURRENTLY displayed on the blink1
# 'next' refers to what will be displayed (ie- what was just retrieved from NOAA and will be used to update the blink1)


# setup some command line arguments

parser = ArgumentParser(description="display space weather on a blink(1) mk2",
                        epilog="See http://www.swpc.noaa.gov/noaa-scales-explanation for description of the scales")

# TODO - figure out how to set default forecast type to be G
# TODO (??) - write to log file (time, G/R/S scales)

parser.add_argument("forecast", type=str, choices=['G','R', 'S'], default = 'G',
                    help="Which type of forecast to display. G = Geomagentic Storm, "
                         "R = Radio Blackout, S = Solar Radiation Storm. "
                         "Default is Geomagnetic")

args = parser.parse_args()
forecasttype = args.forecast


try:
    a = check_output(['blink1-tool', '--list'])
except:
    print "error: no blink1 device found"

# create some dictionaries to map scale (0 - 5) to colors (both as name and rgb values)
scaleToColor = {'0': 'green', '1': 'cyan', '2': 'blue', '3': 'yellow', '4': 'magenta', '5': 'red'}
colorToScale = {'green': '0', 'cyan': '1', 'blue': '2', 'yellow': '3', 'magenta': '4', 'red': '5'}
#colorToRGB = {'green': [0x00,0xff,0x00], 'cyan': [0x00,0xff,0xff], 'blue': [0x00,0x00,0xff],
#              'yellow': [0xff,0xff,0x00], 'magenta': [0xff,0x00,0xff], 'red': [0xff,0x00,0x00]}
# dict of tuple of strings might be more useful
# a class for scale might be better yet.  also check out named tuples in 'collections'
colorToRGB = {'green': ('0x00','0xff','0x00'), 'cyan': ('0x00','0xff','0xff'), 'blue': ('0x00','0x00','0xff'),
              'yellow': ('0xff','0xff','0x00'), 'magenta': ('0xff','0x00','0xff'), 'red': ('0xff','0x00','0x00')}


# establish some named tuples for each position in the scale (this may be better than the above vars)
Severity = namedtuple('Severity', 'scale red green blue')   #scale = 0-5, red/green/blue - hex values
zero = Severity(scale = '0', red = '0x00', green = '0xff', blue = '0x00')   # green
one =  Severity(scale = '1', red = '0x00', green = '0xff', blue = '0xff')      # cyan
two =  Severity(scale = '2', red = '0x00', green = '0x00', blue = '0xff')      # blue
three= Severity(scale = '3', red = '0xff', green = '0xff', blue = '0x00')    # yellow
four = Severity(scale = '4', red = '0xff', green = '0x00', blue = '0xff')     # magenta
five = Severity(scale = '5', red = '0xff', green = '0x00', blue = '0x00')     # red
#create a list of named tuples that will make iterating over them and matching
allscales = [zero, one, two, three, four, five]

def getSpaceWeather(forecasttype):
    '''
    get space weather prediction from NOAA for what will be displayed next
    :param forecasttype: which of the three forecasts to display
    :return:GRS
    '''
    GRS = {}
#    URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"
#    raw = urllib.urlopen(URL)
#    jresponse = json.load(raw)

    with open('test-data/G3.json') as data_file:
        jresponse = json.load(data_file)

    # current activity
    GRS['G'] = jresponse['0']['G']['Scale']
    GRS['R'] = jresponse['0']['R']['Scale']
    GRS['S'] = jresponse['0']['S']['Scale']
    predictDate = jresponse['0']['DateStamp']
    predictTime = jresponse['0']['TimeStamp']

    print "current Geomagnetic Storm status:     %s" % GRS['G']
    print "current Solar Radiation Storm status: %s" % GRS['R']
    print "current Radio Blackout status:        %s" % GRS['S']

    print "prediction date/time: %s %s UTC" % (predictDate, predictTime)
    return GRS[forecasttype]



def getCurrentBlink1Status():
    '''
    read the current scale (as determined by the color) from the blink1 device to determine
    what the previous forecast was
    :return: currentSeverity (item.scale)
    '''
    currentColor = check_output(['blink1-tool', '--rgbread'])
    currColorString = '%s,%s,%s' %(currentColor[19:23], currentColor[24:28],currentColor[29:33] )
    print "current color to pass to command: " + currColorString
    # determine scale number from color by searching through the list of named tuples
    for item in allscales:
        if currColorString == '%s,%s,%s' % (item.red, item.green, item.blue):
            return item.scale



def updateBlink1(current, next):
    '''
    send update to the blink1; worsening prediction will have different pattern than improving
    :param current: the current state of the blink1
    :param next: the next scale to be displayed
    '''
    print "current scale: " + str(current)
    print "next scale: " + str(next)
    nextColorString = allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue
    print "next color string: " + str(nextColorString)
    check_output(['blink1-tool', '--rgb', '%s, %s, %s' %(allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue)])
# TODO - blinking logic to indicate improving or worsening weather.


if __name__ == '__main__':
    next = getSpaceWeather(forecasttype)
    current = getCurrentBlink1Status()
    updateBlink1(current, next)

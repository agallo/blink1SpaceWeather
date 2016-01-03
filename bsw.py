#!/usr/bin/python

import urllib
from subprocess import check_output
from collections import namedtuple
import os

import json
from argparse import ArgumentParser

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# the terms 'current' and 'next' are used through out in comments and variable and function names
# for purposes of this script, 'current' means the scale/color that is CURRENTLY displayed on the blink1
# 'next' refers to what will be displayed (ie- what was just retrieved from NOAA and will be used to update the blink1)

# setup some command line arguments

parser = ArgumentParser(description="display space weather on a blink(1) mk2",
                        epilog="See http://www.swpc.noaa.gov/noaa-scales-explanation for description of the scales")

# TODO - figure out how to set default forecast type to be G

parser.add_argument("forecast", type=str, choices=['G', 'R', 'S'], default='G',
                    help="Which type of forecast to display. G = Geomagentic Storm, "
                         "R = Radio Blackout, S = Solar Radiation Storm. "
                         "Default is Geomagnetic")

args = parser.parse_args()
forecasttype = args.forecast

# check to make sure there is a working blink1 attached
try:
    a = check_output(['/usr/local/bin/blink1-tool', '--list'])
except:
    print "error: no blink1 device found"


# establish some named tuples for each position in the scale (this may be better than the above vars)
Severity = namedtuple('Severity', 'scale red green blue')  # scale = 0-5, red/green/blue - hex values
zero = Severity(scale='0', red='0x00', green='0xff', blue='0x00')  # green
one  = Severity(scale='1', red='0x00', green='0xff', blue='0xff')  # cyan
two  = Severity(scale='2', red='0x00', green='0x00', blue='0xff')  # blue
three= Severity(scale='3', red='0xff', green='0xff', blue='0x00')  # yellow
four = Severity(scale='4', red='0xff', green='0x00', blue='0xff')  # magenta
five = Severity(scale='5', red='0xff', green='0x00', blue='0x00')  # red
# create a list of named tuples that will make iterating over them and matching easier
allscales = [zero, one, two, three, four, five]


def getSpaceWeather(forecasttype):
    '''
    get space weather prediction from NOAA for what will be displayed next
    :param forecasttype: which of the three forecasts to display
    :return:GRS
    '''
    GRS = {}
    URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"
    raw = urllib.urlopen(URL)
    jresponse = json.load(raw)

#    testdata = open('test-data/G2.json')
#    jresponse = json.load(testdata)

    # current activity
    GRS['G'] = jresponse['0']['G']['Scale']
    GRS['R'] = jresponse['0']['R']['Scale']
    GRS['S'] = jresponse['0']['S']['Scale']
    predictDate = jresponse['0']['DateStamp']
    predictTime = jresponse['0']['TimeStamp']

    logfile.write('getSpaceWeather: ' + predictDate + ' ' + predictTime + ' UTC ' +
                  'G: ' + GRS['G'] + ' R: ' + GRS['R'] + ' S: ' + GRS['S'] +
                  ' Selected forecast type: ' + forecasttype + '\n')
    return GRS[forecasttype]


def getCurrentBlink1Status():
    '''
    read the current scale (as determined by the color) from the blink1 device to determine
    what the previous forecast was
    :return: currentSeverity (item.scale)
    '''
    currentColor = check_output(['/usr/local/bin/blink1-tool', '--rgbread'])
    currColorString = '%s,%s,%s' % (currentColor[19:23], currentColor[24:28], currentColor[29:33])
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
    nextColorString = allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue
    # !!!!!!!!!
    # TODO - blinking option isn't working.  it's either ignored (when included with the delay section) or
    # TODO ----    throws an error when included in its own section
    # !!!!!!!!!
    if current == next:
        logfile.write(
            'updateBlink1: NO CHANGE in prediction.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        return
    elif current > next:
        logfile.write(
            'updateBlink1: PREDICTION IMPROVING.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        check_output(['/usr/local/bin/blink1-tool', '-t 750 -m 500 --blink 5', '--rgb',
                      '%s, %s, %s ' % (
                      allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue)])
    elif next > current:
        logfile.write(
            'updateBlink1: PREDICTION WORSENING.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        check_output(['/usr/local/bin/blink1-tool', '-t 350', '-m 150', '--blink 10', '--rgb',
                      '%s, %s, %s ' % (
                      allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue)])


if __name__ == '__main__':
    logfile = open('log/activity', 'a')
    next = getSpaceWeather(forecasttype)
    current = getCurrentBlink1Status()
    updateBlink1(current, next)
    logfile.close()

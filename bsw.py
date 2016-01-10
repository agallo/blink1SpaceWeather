#!/usr/bin/python

import urllib
from subprocess import check_output
from collections import namedtuple
import os
import json
from argparse import ArgumentParser
from time import sleep
import operator


abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)


# the terms 'current' and 'next' are used through out in comments and variable and function names
# for purposes of this script, 'current' means the scale/color that is CURRENTLY displayed on the blink1
# 'next' refers to what will be displayed (ie- what was just retrieved from NOAA and will be used to update the blink1)

# setup some command line arguments

parser = ArgumentParser(description="display space weather on a blink(1) mk2",
                        epilog="See http://www.swpc.noaa.gov/noaa-scales-explanation for description of the scales")

parser.add_argument("forecast", type=str, choices=['G', 'R', 'S', 'w'], nargs='?', default='G',
                    help="Which type of forecast to display. G = Geomagentic Storm, "
                         "R = Radio Blackout, S = Solar Radiation Storm. w = worst scale"
                         " (Default is Geomagnetic)")

args = parser.parse_args()
reqforecasttype = args.forecast

blinkcmd = "/usr/local/bin/blink1-tool"


# establish some named tuples for each position in the scale (this may be better than the above vars)
Severity = namedtuple('Severity', 'scale red green blue')  # scale = 0-5, red/green/blue - hex values
zero = Severity(scale='0', red='0x00', green='0xff', blue='0x00')  # green
one = Severity(scale='1', red='0x00', green='0xff', blue='0xff')  # cyan
two = Severity(scale='2', red='0x00', green='0x00', blue='0xff')  # blue
three = Severity(scale='3', red='0xff', green='0xff', blue='0x00')  # yellow
four = Severity(scale='4', red='0xff', green='0x00', blue='0xff')  # magenta
five = Severity(scale='5', red='0xff', green='0x00', blue='0x00')  # red
# create a list of named tuples that will make iterating over them and matching easier
allscales = [zero, one, two, three, four, five]


def validateBlink():
    '''
    check to make sure there is a working blink1 attached
    :return: boolean
    '''
    try:
        a = check_output([blinkcmd, '--list'])
        return True
    except:
        print "error: no blink1 device found"
        logfile.write('validateBlink: !!!No valid blink(1) mk2 device - exiting\n')
        return False


def getSpaceWeather(forecasttype):
    '''
    get space weather prediction from NOAA for what will be displayed next
    :param forecasttype: which of the three forecasts to display
    :return:GRS, selectforecasttype
    '''
    GRS = {}

    URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"
    raw = urllib.urlopen(URL)
    jresponse = json.load(raw)

#    testdata = open('test-data/G0.json')
#    jresponse = json.load(testdata)

    # current activity
    GRS['G'] = int(jresponse['0']['G']['Scale'])
    GRS['R'] = int(jresponse['0']['R']['Scale'])
    GRS['S'] = int(jresponse['0']['S']['Scale'])
    predictDate = jresponse['0']['DateStamp']
    predictTime = jresponse['0']['TimeStamp']

    logfile.write('getSpaceWeather: ' + predictDate + ' ' + predictTime + ' UTC. ' +
                  'G: ' + str(GRS['G']) + ' R: ' + str(GRS['R']) + ' S: ' + str(GRS['S']) +
                  ' Selected forecast type: ' + forecasttype + '\n')
    if forecasttype == 'w':
        maxkey = max(GRS.iteritems(), key=operator.itemgetter(1))[0]
        return GRS[maxkey], maxkey
    else:
        return GRS[forecasttype], forecasttype


def getCurrentBlink1Status():
    '''
    read the current scale (as determined by the color) from the blink1 device to determine
    what the previous forecast was
    :return: currentSeverity (item.scale)
    '''
    currentColor = check_output([blinkcmd, '--rgbread'])
    currColorString = '%s,%s,%s' % (currentColor[19:23], currentColor[24:28], currentColor[29:33])
    # determine scale number from color by searching through the list of named tuples
    for item in allscales:
        if currColorString == '%s,%s,%s' % (item.red, item.green, item.blue):
            return int(item.scale)


def updateBlink1(current, next, selforecasttype):
    '''
    send update to the blink1; worsening prediction will have different pattern than improving
    blink1-tool '--blink' (or equiv --flash) not working; work around via for loop and sleep. not ideal
    :param current: the current state of the blink1
    :param next: the next scale to be displayed
    '''
    if current == next:
        logfile.write(
            'updateBlink1: using scale "' + selforecasttype + '"  NO CHANGE in prediction.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        return
    elif current > next:
        logfile.write(
            'updateBlink1: using scale "' + selforecasttype + '"  PREDICTION IMPROVING.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        for blink in range(0, (int(current) - int(next))):
            check_output([blinkcmd, '--off'])
            sleep(1)
            check_output([blinkcmd,  '-t 750', '--rgb', '%s, %s, %s ' % (
                allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue)])
        return
    elif next > current:
        logfile.write(
            'updateBlink1: using scale "' + selforecasttype + '" PREDICTION WORSENING.  Old scale: ' + str(current) + ' New scale: ' + str(next) + '\n')
        for blink in range(0, 3 * int(next)):
            check_output([blinkcmd, '--off'])
            sleep(.5)
            check_output([blinkcmd, '-t 250', '-m 150', '--rgb', '%s, %s, %s ' % (
                allscales[int(next)].red, allscales[int(next)].green, allscales[int(next)].blue)])


if __name__ == '__main__':
    logfile = open('log/activity', 'a')
    if validateBlink():
        next, selforecasttype = getSpaceWeather(reqforecasttype)
        current = getCurrentBlink1Status()
        updateBlink1(current, next, selforecasttype)
    logfile.close()

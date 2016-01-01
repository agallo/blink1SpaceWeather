#!/usr/bin/python

import urllib
import json
from subprocess import check_output
from argparse import ArgumentParser

# TODO - figure out how to set default forecast type to be G

# setup some command line arguments

parser = ArgumentParser(description="display space weather on a blink(1) mk2")

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
colorToRGB = {'green': [0x00,0xff,0x00], 'cyan': [0x00,0xff,0xff], 'blue': [0x00,0x00,0xff],
              'yellow': [0xff,0xff,0x00], 'magenta': [0xff,0x00,0xff], 'red': [0xff,0x00,0x00]}


def getSpaceWeather(forecasttype):
    '''
    get current space weather prediction from NOAA
    :param forecasttype: which of the three forecasts to display
    :return:GRS
    '''
    GRS = {}
#    URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"
#    raw = urllib.urlopen(URL)
#    jresponse = json.load(raw)

    with open('test-data/G1.json') as data_file:
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
    read the current color from the blink1 device to determine
    what the previous forecast was
    :return: currColorString
    '''
    currentColor = check_output(['blink1-tool', '--rgbread'])
    currColorString = '%s,%s,%s' %(currentColor[19:23], currentColor[24:28],currentColor[29:33] )
    print "current color to pass to command: " + currColorString
    return currColorString
# TODO - figure out best way to map current color to scale (maybe search colorToRGB dict and return key from value)


def updateBlink1(current, next):
    '''
    send update to the blink1; worsening prediction will have different pattern than improving
    :param current: the current state of the blink1
    :param next: the next scale to be displayed
    '''
    print current
    print next



if __name__ == '__main__':
    next = getSpaceWeather(forecasttype)
    current = getCurrentBlink1Status()
    updateBlink1(current, next)

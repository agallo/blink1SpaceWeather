#!/usr/bin/python

import urllib
import json
from subprocess import check_output


try:
    a = check_output(['blink1-tool', '--list'])
except:
    print "error: no blink1 device found"

# create some dictionaries to map scale (0 - 5) to colors (both as name and rgb values)
scaleToColor = {'0': 'green', '1': 'cyan', '2': 'blue', '3': 'yellow', '4': 'magenta', '5': 'red'}
colorToScale = {'green': '0', 'cyan': '1', 'blue': '2', 'yellow': '3', 'magenta': '4', 'red': '5'}
colorToRGB = {'green': [0x00,0xff,0x00], 'cyan': [0x00,0xff,0xff], 'blue': [0x00,0x00,0xff],
              'yellow': [0xff,0xff,0x00], 'magenta': [0xff,0x00,0xff], 'red': [0xff,0x00,0x00]}


def getSpaceWeather():
#    URL = "http://services.swpc.noaa.gov/products/noaa-scales.json"
#    raw = urllib.urlopen(URL)
#    jresponse = json.load(raw)

    with open('test-data/G1.json') as data_file:
        jresponse = json.load(data_file)

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

def getCurrentBlink1Status():
    '''
    read the current color from the blink1 device to determine
    what the previous forecast was
    :return: scale
    '''
    currentColor = check_output(['blink1-tool', '--rgbread'])
    red = currentColor[19:23]
    green = currentColor[24:28]
    blue = currentColor[29:33]
    print "current color, red value: %s" % red
    print "current color, green value: %s" % green
    print "current color, blue value: %s" % blue





if __name__ == '__main__':
    getSpaceWeather()
    getCurrentBlink1Status()


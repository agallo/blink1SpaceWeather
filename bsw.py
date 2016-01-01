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
    '''
    get current space weather prediction from NOAA
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
    return GRS

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





if __name__ == '__main__':
    getSpaceWeather()
    getCurrentBlink1Status()
#    updateBlink1()

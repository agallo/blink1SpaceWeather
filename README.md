# blink1SpaceWeather

Get and display space weather on a [blink(1) mk2](https://blink1.thingm.com/)


[NOAA Space Weather Scales](http://www.swpc.noaa.gov/noaa-scales-explanation "NOAA Space Weather Scales") 


## Usage
```
usage: bsw.py [-h] [{G,R,S}]

display space weather on a blink(1) mk2

positional arguments:
  {G,R,S}     Which type of forecast to display. G = Geomagentic Storm, R =
              Radio Blackout, S = Solar Radiation Storm. Default is
              Geomagnetic

optional arguments:
  -h, --help  show this help message and exit

See http://www.swpc.noaa.gov/noaa-scales-explanation for description of the
scales
```

This script uses subprocess to call the blink1-tool command line tool.

For some reason, the '--blink' (or equivalent '--flash') isn't working.  A workaround is in place by creating a for loop, with sleep statements.  This isn't ideal since the blink1-tool includes options for fading

color scale:
```
scale   color       rgb hex
 - 5    red         0xff,0x00,0x00
 - 4    magenta     0xff,0x00,0xff
 - 3    yellow      0xff,0xff,0x00
 - 2    blue        0x00,0x00,0xff
 - 1    cyan        0x00,0xff,0xff
 - 0    green       0x00,0xff,0x00
```
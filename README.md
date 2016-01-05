# blink1SpaceWeather

Get and display space weather on a [blink(1) mk2](https://blink1.thingm.com/)


[NOAA Space Weather Scales](http://www.swpc.noaa.gov/noaa-scales-explanation "NOAA Space Weather Scales") 


color scale:
```
 - 5	red         rgb:0xff,0x00,0x00
 - 4	magenta     rgb:0xff,0x00,0xff
 - 3	yellow      rgb:0xff,0xff,0x00
 - 2	blue        rgb:0x00,0x00,0xff
 - 1	cyan        rgb:0x00,0xff,0xff
 - 0	green       rgb:0x00,0xff,0x00
```

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

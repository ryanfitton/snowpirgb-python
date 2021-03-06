#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
# Modified for SnowPi RGB by @Ryanteck
# Modified for CheerLights API by @ryanfitton - Using code used from: https://github.com/feiticeir0/cheerlights
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.
#
#
# Usage for SnowPi:
# Requires:
#  - PIP (sudo apt install python3-pip)
#  - rpi_ws281x (sudo pip3 install rpi_ws281x)
#
# Once installed, you can run the Demo with these options:
# - All demos: sudo python3 demo.py -a
# - Wipe demo: sudo python3 demo.py -w
# - Theatre Chase demo: sudo python3 demo.py -t
# - Rainbow demo: sudo python3 demo.py -r
# - Cheerlights demo: sudo python3 demo.py -cheer
#
# More configurable options:
# - Clear the current display: sudo python3 demo.py -c
# - Set the brightness, pass an integer for the brighness: sudo python3 demo.py -b 85
#
# Start on Pi start-up - Add to root user crontab:
# sudo crontab -e
# @reboot /usr/bin/python /home/pi/snowpirgb-python/demo.py -cheer &


import time
from rpi_ws281x import PixelStrip, Color
import requests
import argparse

# LED strip configuration:
LED_COUNT = 12        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 100  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53

# If you need proxy configurations:
PROXIES = {
	'http': '<proxy_address>:<port>',
	'https': '<proxy_address>:<port>'
}


#borrowed from Pimoroni's Cheerlights from blink examples
def hex_to_rgb(col_hex):
	"""Convert hex color to rgb"""
	col_hex = col_hex.lstrip("#")
	return bytearray.fromhex(col_hex)


# Define functions which animate LEDs in various ways.
def colorWipe(strip, color, wait_ms=50):
    """Wipe color across display a pixel at a time."""
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, color)
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=50, iterations=10):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=20, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=10, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=50):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def cheerLights(strip):
    """Connect to the CheerLights API and use latest colour value."""
    # With proxy
    #req = requests.get("http://api.thingspeak.com/channels/1417/field/2/last.json", timeout=2,proxies=PROXIES)
    # Without proxy
    req = requests.get("http://api.thingspeak.com/channels/1417/field/2/last.json", timeout=2)
    # Convert HEX code to RGB values
    r, g, b = hex_to_rgb(req.json()["field2"])
    # Loop through LEDs and change values
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(r, g, b))
        strip.show()
        # Wipe effect
        #ime.sleep(wait_ms / 1000.0)
    # Wait 10s before another request to the API - be friendly
    time.sleep(10)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    parser.add_argument('-b', '--brightness', action='store', dest='b', type=int, help='Set the brightness')
    parser.add_argument('-a', '--all', action='store_true', dest='a', help='Run All Demos')
    parser.add_argument('-w', '--whipe', action='store_true', dest='w', help='Only Run Whipe Demos')
    parser.add_argument('-t', '--theater', action='store_true', dest='t', help='Only Run Theater Chase Demos')
    parser.add_argument('-r', '--rainbow', action='store_true', dest='r', help='Only Run Rainbow Demos')
    parser.add_argument('-cheer', '--cheerlights', action='store_true', dest='cheer', help='Only Run CheerLights Demo')
    args = parser.parse_args()

    if args.b:
        LED_BRIGHTNESS = args.b

    # Create NeoPixel object with appropriate configuration.
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    # Intialize the library (must be called once before other functions).
    strip.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            if args.a:
                print('Color wipe animations.')
                colorWipe(strip, Color(255, 0, 0))  # Red wipe
                colorWipe(strip, Color(0, 255, 0))  # Blue wipe
                colorWipe(strip, Color(0, 0, 255))  # Green wipe
                print('Theater chase animations.')
                theaterChase(strip, Color(127, 127, 127))  # White theater chase
                theaterChase(strip, Color(127, 0, 0))  # Red theater chase
                theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
                theaterChaseRainbow(strip)
                print('Rainbow animations.')
                rainbow(strip)
                rainbowCycle(strip)
                theaterChaseRainbow(strip)
            if args.t:
                theaterChase(strip, Color(127, 127, 127))  # White theater chase
                theaterChase(strip, Color(127, 0, 0))  # Red theater chase
                theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            if args.w:
                colorWipe(strip, Color(255, 0, 0))  # Red wipe
                colorWipe(strip, Color(0, 255, 0))  # Blue wipe
                colorWipe(strip, Color(0, 0, 255))  # Green wipe
            if args.r:
                rainbow(strip)
                rainbowCycle(strip)
            if args.cheer:
                cheerLights(strip)


    except KeyboardInterrupt:
        if args.clear:
            colorWipe(strip, Color(0, 0, 0), 10)

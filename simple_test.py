#!/usr/bin/python
# coding: utf8

# Copyright (c) 2014 Adafruit Industries
# Author: Tony DiCola
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

# Can enable debug output by uncommenting:
#import logging
#logging.basicConfig(level=logging.DEBUG)

import time

import Adafruit_GPIO.SPI as SPI
from MAX6675 import MAX6675


# Define a function to convert celsius to fahrenheit.
def c_to_f(c):
        return c * 9.0 / 5.0 + 32.0


# Uncomment one of the blocks of code below to configure your Pi or BBB to use
# software or hardware SPI.

# Raspberry Pi software SPI configuration.
# CLK = 25
# CS  = 24
# DO  = 18
# sensor = MAX6675.MAX6675(CLK, CS, DO)

# Raspberry Pi hardware SPI configuration.
#SPI_PORT   = 0
#SPI_DEVICE = 0
#sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# BeagleBone Black software SPI configuration.
CLK = 24
CS  = 4
DO  = 25
sensor = MAX6675.MAX6675(CLK, CS, DO)

# BeagleBone Black hardware SPI configuration.
# SPI_PORT   = 1
# SPI_DEVICE = 0
# sensor = MAX6675.MAX6675(spi=SPI.SpiDev(SPI_PORT, SPI_DEVICE))

# Loop printing measurements every second.

while True:
    temp = sensor.readTempC()
    print( 'Temp: {0:0.0F}°C / {1:0.0F}°F'.format(temp, c_to_f(temp)))
    time.sleep(1.0)

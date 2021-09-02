#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import MAX6675 as MAX6675
import time

#CLK OR SCK 
CLK = 24

#CS
CS  = 4

#SO OR DO
#sensor1 
DO1  = 25
#sensor2
#DO2 = 12

#c = celsius
#f = Fahrenheit
#k = kelvin
units = "c"

thermocouple1 = MAX6675.MAX6675(CLK, CS, DO1, units)
#thermocouple2 = MAX6675.MAX6675(CLK, CS, DO2, units)
time.sleep(1)
running = True
while(running):
    try:
        thermocouple1 = MAX6675.MAX6675(CLK, CS, DO1, units)
        temp1 = thermocouple1.get_temp()
        print('sensor1 ' ,temp1)
        #temp2 = thermocouple2.get_temp()
        #print('sensor2 ' ,temp2)
        time.sleep(1)

    except KeyboardInterrupt:
        running = False

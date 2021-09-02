#!/usr/bin/python
#--------------------------------------
#    ___  ___  _ ____
#   / _ \/ _ \(_) __/__  __ __
#  / , _/ ___/ /\ \/ _ \/ // /
# /_/|_/_/  /_/___/ .__/\_, /
#                /_/   /___/
#
#           bme280.py
#  Read data from a digital pressure sensor.
#
#  Official datasheet available from :
#  https://www.bosch-sensortec.com/bst/products/all_products/bme280
#
# Author : Matt Hawkins
# Date   : 21/01/2018
#
# https://www.raspberrypi-spy.co.uk/
#
#--------------------------------------
import tkinter
import tk_tools
import MAX6675 as MAX6675
import math 
import smbus
import time
from ctypes import c_short
from ctypes import c_byte
from ctypes import c_ubyte
# tempreture sensor GPIO pin configration 
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

DEVICE = 0x77 # Default device I2C address
sea_level_pressure=1013.4
bus = smbus.SMBus(1) # Rev 2 Pi, Pi 2 & Pi 3 uses bus 1
                     # Rev 1 Pi uses bus 0

def getShort(data, index):
  # return two bytes from data as a signed 16-bit value
    return c_short((data[index+1] << 8) + data[index]).value

def getUShort(data, index):
  # return two bytes from data as an unsigned 16-bit value
    return (data[index+1] << 8) + data[index]

def getChar(data,index):
  # return one byte from data as a signed char
    result = data[index]
    if result > 127:
        result -= 256
    return result

def getUChar(data,index):
  # return one byte from data as an unsigned char
    result =  data[index] & 0xFF
    return result

def readBME280ID(addr=DEVICE):
  # Chip ID Register Address
    REG_ID     = 0xD0
    (chip_id, chip_version) = bus.read_i2c_block_data(addr, REG_ID, 2)
    return (chip_id, chip_version)

def readBME280All(addr=DEVICE):
  # Register Addresses
    REG_DATA = 0xF7
    REG_CONTROL = 0xF4
    REG_CONFIG  = 0xF5

    REG_CONTROL_HUM = 0xF2
    REG_HUM_MSB = 0xFD
    REG_HUM_LSB = 0xFE

  # Oversample setting - page 27
    OVERSAMPLE_TEMP = 2
    OVERSAMPLE_PRES = 2
    MODE = 1

  # Oversample setting for humidity register - page 26
    OVERSAMPLE_HUM = 2
    bus.write_byte_data(addr, REG_CONTROL_HUM, OVERSAMPLE_HUM)

    control = OVERSAMPLE_TEMP<<5 | OVERSAMPLE_PRES<<2 | MODE
    bus.write_byte_data(addr, REG_CONTROL, control)

  # Read blocks of calibration data from EEPROM
  # See Page 22 data sheet
    cal1 = bus.read_i2c_block_data(addr, 0x88, 24)
    cal2 = bus.read_i2c_block_data(addr, 0xA1, 1)
    cal3 = bus.read_i2c_block_data(addr, 0xE1, 7)

  # Convert byte data to word values
    dig_T1 = getUShort(cal1, 0)
    dig_T2 = getShort(cal1, 2)
    dig_T3 = getShort(cal1, 4)

    dig_P1 = getUShort(cal1, 6)
    dig_P2 = getShort(cal1, 8)
    dig_P3 = getShort(cal1, 10)
    dig_P4 = getShort(cal1, 12)
    dig_P5 = getShort(cal1, 14)
    dig_P6 = getShort(cal1, 16)
    dig_P7 = getShort(cal1, 18)
    dig_P8 = getShort(cal1, 20)
    dig_P9 = getShort(cal1, 22)

    dig_H1 = getUChar(cal2, 0)
    dig_H2 = getShort(cal3, 0)
    dig_H3 = getUChar(cal3, 2)

    dig_H4 = getChar(cal3, 3)
    dig_H4 = (dig_H4 << 24) >> 20
    dig_H4 = dig_H4 | (getChar(cal3, 4) & 0x0F)

    dig_H5 = getChar(cal3, 5)
    dig_H5 = (dig_H5 << 24) >> 20
    dig_H5 = dig_H5 | (getUChar(cal3, 4) >> 4 & 0x0F)

    dig_H6 = getChar(cal3, 6)

  # Wait in ms (Datasheet Appendix B: Measurement time and current calculation)
    wait_time = 1.25 + (2.3 * OVERSAMPLE_TEMP) + ((2.3 * OVERSAMPLE_PRES) + 0.575) + ((2.3 * OVERSAMPLE_HUM)+0.575)
    time.sleep(wait_time/1000)  # Wait the required time  

  # Read temperature/pressure/humidity
    data = bus.read_i2c_block_data(addr, REG_DATA, 8)
    pres_raw = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
    temp_raw = (data[3] << 12) | (data[4] << 4) | (data[5] >> 4)
    hum_raw = (data[6] << 8) | data[7]

  #Refine temperature
    var1 = ((((temp_raw>>3)-(dig_T1<<1)))*(dig_T2)) >> 11
    var2 = (((((temp_raw>>4) - (dig_T1)) * ((temp_raw>>4) - (dig_T1))) >> 12) * (dig_T3)) >> 14
    t_fine = var1+var2
    temperature = float(((t_fine * 5) + 128) >> 8);

  # Refine pressure and adjust for temperature
    var1 = t_fine / 2.0 - 64000.0
    var2 = var1 * var1 * dig_P6 / 32768.0
    var2 = var2 + var1 * dig_P5 * 2.0
    var2 = var2 / 4.0 + dig_P4 * 65536.0
    var1 = (dig_P3 * var1 * var1 / 524288.0 + dig_P2 * var1) / 524288.0
    var1 = (1.0 + var1 / 32768.0) * dig_P1
    if var1 == 0:
        pressure=0
    else:
        pressure = 1048576.0 - pres_raw
        pressure = ((pressure - var2 / 4096.0) * 6250.0) / var1
        var1 = dig_P9 * pressure * pressure / 2147483648.0
        var2 = pressure * dig_P8 / 32768.0
        pressure = pressure + (var1 + var2 + dig_P7) / 16.0
       
  # Refine humidity
    humidity = t_fine - 76800.0
    humidity = (hum_raw - (dig_H4 * 64.0 + dig_H5 / 16384.0 * humidity)) * (dig_H2 / 65536.0 * (1.0 + dig_H6 / 67108864.0 * humidity * (1.0 + dig_H3 / 67108864.0 * humidity)))
    humidity = humidity * (1.0 - dig_H1 * humidity / 524288.0)
    if humidity > 100:
        humidity = 100
    elif humidity < 0:
        humidity = 0

    return temperature/100.0,pressure/100.0,humidity
'''
def altitude(self):
        """The altitude based on current ``pressure`` versus the sea level pressure
        (``sea_level_pressure``) - which you must enter ahead of time)"""
        pressure = self.pressure  # in Si units for hPascal
        return 44330 * (1.0 - math.pow(pressure/sea_level_pressure, 0.1903))   '''

#******GUI********
def main():
    x = int(in1.get()) #get value from entry box
    y = int(in2.get()) #get value from entry box
    
    if int(in1.get()) <= 121: 
        constant = 1000
    elif 121 < int(in1.get()) < 134:
        constant = 1500
    elif int(in1.get()) >= 134:
        constant = 2000
    temperature,pressure,humidity = readBME280All()
    Pres = (1000-pressure) + constant
    
    label.configure(text =format(Pres, '.0f'), font= ('Verdana', 26))
   
    temp1 = thermocouple1.get_temp()
    label_pvtemp.configure(text =format(temp1, '.1f'), font= ('Verdana', 26))

    (chip_id, chip_version) = readBME280ID()
    print ("Chip ID     :", chip_id)
    print ("Version     :", chip_version)  
    temperature,pressure,humidity = readBME280All()
    print("SV.Temperature:%.1f *C" %int(in1.get()))
    print("Temperature:%.2f *C" %temperature)
    print("Pressure:%.1f hPa" %pressure)
    print("Humidity:%.2f %%" %humidity)    
    print('SV.Temp1 ' ,temp1)
                
    Pres = (1000-pressure) + constant
    print("SV. pressure:%.0f mbar"%Pres)
    
    altitude=44330 * (1.0 - math.pow(pressure/sea_level_pressure, 0.1903))
    print("Altitude:%.0f meters" %altitude)
    print("________________________________")
    # Convert the integer value to string to display in Seven segment widget
    #ss_int.set_value(int(Pres))  # Update the value of seven segment display widget


#temp1 = thermocouple1.get_temp()
#label_pvtemp.configure(text =format(temp1, '.1f'), font= ('Verdana', 26))

window = tkinter.Tk()   # create tkinter window
window.title("Smart Steam Sterilizer") #give title
window.configure(background="white") #change background color
window.geometry("480x320")
temp1 = thermocouple1.get_temp()
#labe.configure(text =format(temp1, '.1f'), font= ('Verdana', 26))
label_press = tkinter.Label(window, text="Press.", font= ('ARIAL  14 underline bold'), padx=20, pady =1, bg="green",fg="white")
label_press.place(width=80, x=80, y=0)

label_temp = tkinter.Label(window, text="Temp.°C", font= ('ARIAL  14 underline bold'), padx=20, pady =1, bg="green",fg="white")
label_temp.place(width=80, x=200, y=0)

label_time = tkinter.Label(window, text="Time'", font= ('ARIAL  14 underline bold'), padx=20, pady =1, bg="green",fg="white")
label_time.grid(row=0,column=3, columnspan=2)

label_setpoint = tkinter.Label(window, text="SP:", font= ('Verdana', 16, 'bold'), padx=10, pady =1, bg="white",fg="black")
label_setpoint.place(width=80, x=0, y=40)
label_presntvalue = tkinter.Label(window, text="PV:", font= ('Verdana', 16, 'bold'), padx=10, pady =1, bg="white",fg="black")
label_presntvalue.grid(row=2, column=0, padx=10, pady =10)

button_on = tkinter.Button(window, text="Start", font= ('Verdana',16), padx=20, pady =15, bg="green",fg="white",
command = main)
button_on.grid(row=4,column=1, columnspan=5)

in1 = tkinter.Entry(window, width = 4, borderwidth=4, font= ('Verdana', 26))
in1.grid(row = 1, column =2, padx=20, pady =2)
in2 = tkinter.Entry(window, width = 2, borderwidth=4, font= ('Verdana', 26))
in2.grid(row = 1, column =3, padx=10, pady =2)
label=tkinter.Label(window, text=format('2245'), font= ('Verdana', 26), background="white")
label.grid(row = 1, column =1, padx=10, pady =10)

label_pvpres=tkinter.Label(window, text = temp1, font= ('Verdana', 26), background="white")
label_pvpres.grid(row = 2, column =1, padx=10, pady =10)

label_pvtemp=tkinter.Label(window, text = temp1, font= ('Verdana', 26), background="white")
label_pvtemp.grid(row = 2, column =2, padx=10, pady =10)

#self.label.configure(text=now)

if __name__=="__main__":
    main()
window.mainloop()
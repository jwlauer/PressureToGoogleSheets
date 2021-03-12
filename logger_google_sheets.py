"""Logs pressure/temperature/depth to a Google Sheet.
Wes Lauer
March 12, 2021
Released under MIT license

This program uses an ESP32 (Lolin D32 Pro) to read data from a
water pressure sensor (MS8803-05BA) and an atmospheric pressure
sensor (BMP/BME280). Provisions are also made for reading
timestamps from a DS3231 RTC or an NTP server.  Data is posted
to an online google sheet if the device is online. The device
is then placed in deep sleep. This script is intended to
be called directly from main.py.

Be sure to set the correct SSID, password, and apikey.
"""

import machine, utime, esp, esp32, urequests, usocket, network, uos
import bme280, ms5803, direct_to_google_sheet
from machine import Pin

def log():
    import machine, utime, esp, esp32, urequests, usocket, network, uos
    import bme280, ms5803, direct_to_google_sheet
    from machine import Pin

    led = Pin(5, Pin.OUT)
    led.value(0)

    def flash(n,t):
        for i in range(n):
            led.value(1)
            utime.sleep(t)
            led.value(0)
            utime.sleep(t)

    esp.osdebug(None)
    startticks = utime.ticks_ms()

    #declare global login variables
    ssid = "Sensors"
    password = "ENSC_2400"
    gKey = "AKfycbwAJbCuZfNzar00oHPd3CZ8Hzn9c79LfUU5lg8u0p9kAxiGyetqGqWJ"
    gSheetKey = "1AIWnPTtGNdlZ1TfbzpGTnheCOrPnKUHLUVefa8i2Y8k"

    wake_reason = machine.wake_reason()
    reset_cause = machine.reset_cause()
    print('wake reason = '+ str(wake_reason))
    print('reset cause = '+ str(reset_cause))

    #mount SD card on Lolin D32 Pro.  If it doesn't work, sleep 20 seconds so user can break out.
    try:
        uos.mount(machine.SDCard(slot=2,width=1, sck=18, mosi=23, miso=19, cs=4), "/sd")
    except:
        flash(20,0.25)

    #write header file if did not wake from deep sleep
    if machine.reset_cause != machine.DEEPSLEEP_RESET:
        outputtxt = 'date,time,Patm(mbar),Tatm(C),PH20(mbar),TH20(C),Depth(m),Battery(V)\r\n'
        try:
            uos.chdir('sd')
            f = open('datalog.txt','a')
            f.write(outputtxt)
            f.close()
            uos.chdir('/')
        except:
            #flash LED if fails to write and write to flash memory
            f = open('datalog.txt','a')
            f.write(outputtxt)
            f.close()
            flash(10,0.5)

    #turn on power pins for RTC
    power = Pin(2, Pin.OUT)
    power.value(1)

    #connect to wlan
    try:
        sta_if = network.WLAN(network.STA_IF) #define object to access station mode functions
        sta_if.active(True) #make station mode active
        sta_if.connect(ssid, password)
        print('connected')
    except:
        print('not connected')
        pass
        
    utime.sleep(3)

    #read value of time from DS3231 RTC if it is connected. If not, set time from
    #web (NTP time) and if that doesn't work, just revert to system real time clock.
    try:
        import urtc #needs to be on the board
        from machine import I2C, Pin
        i2c = I2C(scl=Pin(22), sda=Pin(21), freq=400000)
        rtc = urtc.DS3231(i2c)
        datetime = rtc.datetime()
        print('Time set from DS3231')
    except:
        try:
            from ntptime import settime
            print('Time set from NTP time to: ', end = '')
            settime()
            utime.sleep_ms(500)
            rtc = machine.RTC()
            #can also set time manually using rtc.datetime(year, month, day, weekday, hour, minute, second, millisecond)
        except:
            print("could not set time from NTP server, reverting to machine RTC for time")
            rtc = machine.RTC()
        datetime = rtc.datetime()
    print('Datetime in machine.rtc format = ', end = '')
    print(datetime)

    #read value of voltage using built-in 100k 100k voltage divider on pin 35 for Lolin D32 Pro
    from machine import ADC
    adc = ADC(Pin(35))
    adc.atten(ADC.ATTN_11DB)  #Voltage range 0 (0) V to 3.6 V (4095)
    adc_count = adc.read()
    battery = adc_count / 4095 * 3.6 * 2  #factor of two because of voltage divider
    print('battery = ',battery)

    #Read data
    i2c = machine.I2C(1, scl=machine.Pin(22), sda=machine.Pin(21))
    bad = False
    try:
        bme1 = bme280.BME280(i2c=i2c, address = 119) #sdo to 3.3v
        [T1,P1,H1] = bme1.raw_values  #T in degrees C, P in hPa
    except:
        [T1,P1,H1] = [-999,-999,-999]
        bad = True

    try:
        [P2,T2] = ms5803.read(i2c=i2c, address = 118)
    except:
        [P2,T2]=[-999,-999]
        bad = True
        
    if not bad:
        WaterLevelDifference = (P2-P1)*100/9810
    else:
        WaterLevelDifference = -999
        
    data = {}
    data['Patm'] = P1
    data['Tatm'] = T1
    data['PH20'] = P2
    data['TH20'] = T2
    data['Depth'] = WaterLevelDifference
    data['Battery'] = battery

    #Send data to Google Sheet
    result = direct_to_google_sheet.send_to_sheet(ssid, password, gKey, gSheetKey, data)
    print(result)

    #turn off wifi to lower power when in sleep mode
    sta_if.active(0)
     
    #format output string
    outputtxt = ('%s/%s/%s,%s:%s:%s,' % (datetime[0], datetime[1], datetime[2], datetime[4], datetime[5], datetime[6]))
    outputtxt += ('%s,%s,%s,%s,%s,%s\r\n' % (P1,T1,P2,T2,WaterLevelDifference,battery))
    print(outputtxt)

    #then write final data to the SD
    try:
        uos.chdir('sd')
        f = open('datalog.txt', 'w') #this erases the old file
        f.write(outputtxt) #only first line of file is used
        f.close()
        uos.chdir('/')
    except:
        #flash LED if fails to write and write to flash memory
        f = open('datalog.txt','a')
        f.write(outputtxt)
        f.close()
        flash(10,0.5)

    flash(5,1)

    p1 = machine.Pin(15, machine.Pin.IN, machine.Pin.PULL_UP)
    #esp32.wake_on_ext0(p1, level = 0)
    #set machine to wake if p1 (so pin 15) is pulled low
    #the internal pull-up resistor may not work, so may require
    #an external pull-up resistor of perhaps 100K.
    esp32.wake_on_ext1([p1], level = 0)

    timeon = (utime.ticks_ms() - startticks)/1000
    print('Going to sleep after being awake for ' + str(timeon) + ' s')
    machine.deepsleep(1000*1*60) #sleeps 5 minutes






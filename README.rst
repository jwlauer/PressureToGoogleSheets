Overview
============

This repository includes code for developing a wifi-enabled differential pressure logger using an ESP32 microcontroller (`Lolin D32 Pro <https://www.wemos.cc/en/latest/d32/d32_pro.html>`__), a `MS5803-05BA <https://www.amsys-sensor.com/products/pressure-sensor/ms5803-series-digital-absolute-pressure-sensors-up-to-1-2-5-7-14-30-bar/>`__ submersible pressure sensor, a `Bosch BMP/BME 280 <https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf>`__ atmospheric pressure sensor, and an optional DS3231 Real Time Clock. Code was tested using the generic `MicroPython 1.14 build <https://micropython.org/download/esp32/>`__ for ESP IDF v3.x. 

The logging program saves data to an SD card or flash memory on the Lolin D32 Pro and attempts to post the data to a Google Sheet using a separate Google Apps script.  The Google Apps script is coded in javascript and must be deployed using a valid Google account. Appropriate API Keys must updated in the file logger_google_sheets.py.

The easiest way to deploy the code is to copy all *.py files in the repository to the Lolin D32 Pro using an IDE like `Thonny <https://thonny.org/>`__.  Thonny can also be used to install the correct version of MicroPython on the ESP32. 

Wiring
------
The code assumes all sensors are wired to the same I2C bus using:
::
  SDA --> Pin 21
  SCL --> Pin 22

The code uses pin 15 to wake the ESP32 from deep sleep. Proper functionality may require adding a weak external pullup resistor (e.g., 100K) to pin 15.

Breakout modules for the BMP/BME280 and DS3231 RTC are readily available. While breakout modules for the MS5803 are also commercially available, they can be too large for practical incorporation in a submersible pressure sensor. I've laid out a `small custom PCB <https://github.com/jwlauer/CTD/tree/master/hardware/MS5803>`__ that can simplify wiring and allows the sensor to be installed inside standard 1-inch PVC pipe.  The I2C address of the MS5803 must be set to 0x76 using an appropriate solder bridge. Instructions for using the MS5803 with a small generic PCB are available at the `Cave Pearl Project <https://thecavepearlproject.org/2014/03/27/adding-a-ms5803-02-high-resolution-pressure-sensor/>`__.

Acknowledgements
----------------

The code uses the `prerequests <https://gist.github.com/SpotlightKid/8637c685626b334e5c0ec341dd269c44>`__ library, the `BME280 <https://github.com/catdog2/mpy_bme280_esp8266>`__ library, and AdaFruit's `urtc <https://github.com/adafruit/Adafruit-uRTC>`__ library.  This `MS5803-05BA <https://github.com/ControlEverythingCommunity/MS5803-05BA/blob/master/Python/MS5803_05BA.py>`__ library was modified for use with micropython. The javascript code is based on this `Google App Scripts example <https://rntlab.com/question/send-sensor-reading-via-email-in-micropython-directly-to-google-sheet-page-191/>`__.  

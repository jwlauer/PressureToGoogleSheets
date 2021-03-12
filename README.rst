Overview
============

This repository includes code for developing a wifi-enabled differential pressure logger using an ESP32 microcontroller (`Lolin D32 Pro <https://www.wemos.cc/en/latest/d32/d32_pro.html>`__), a `MS5803-05BA <https://www.amsys-sensor.com/products/pressure-sensor/ms5803-series-digital-absolute-pressure-sensors-up-to-1-2-5-7-14-30-bar/>`__ submersible pressure sensor, a `Bosch BMP/BME 280 <https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme280-ds002.pdf>`__ atmospheric pressure sensor, and an optional DS3231 Real Time Clock. Code was tested using the generic `MicroPython 1.14 build <https://micropython.org/download/esp32/>`__ for ESP IDF v3.x. 

The logging program saves data to an SD card or flash memory on the Lolin D32 Pro and attempts to post the data to a Google Sheet using a separate Google Apps script.  The Google Apps script is coded in javascript and must be deployed using a valid Google account. Appropriate API Keys must updated in the file logger_google_sheets.py.

The easiest way to deploy the code is to copy all *.py files in the repository to the Lolin D32 Pro using an IDE like Thonny.  Thonny can also be used to install the correct version of MicroPython on the ESP32. 

Wiring
------
The code assumes all sensors are wired to the same I2C bus using:
::
  SDA --> Pin 21
  SCL --> Pin 22




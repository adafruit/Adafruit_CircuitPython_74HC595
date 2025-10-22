# SPDX-FileCopyrightText: 2025 Melissa LeBlanc-Williams for Adafruit Industries
# SPDX-License-Identifier: MIT

import time

import board
import digitalio

import adafruit_74hc595

latch_pin = digitalio.DigitalInOut(board.D5)
clock_pin = digitalio.DigitalInOut(board.D6)
data_pin = digitalio.DigitalInOut(board.D9)
sr = adafruit_74hc595.ShiftRegister74HC595(latch=latch_pin, clock=clock_pin, data=data_pin)

pin1 = sr.get_pin(1)

while True:
    pin1.value = True
    time.sleep(1)
    pin1.value = False
    time.sleep(1)

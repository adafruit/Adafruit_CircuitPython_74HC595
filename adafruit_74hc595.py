# The MIT License (MIT)
#
# Copyright (c) 2018 Kattni Rembor for Adafruit Industries
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
"""
`adafruit_74hc595`
====================================================

CircuitPython driver for 74HC595 shift register.

* Author(s): Kattni Rembor, Tony DiCola

Implementation Notes
--------------------

**Hardware:**

"* `74HC595 Shift Register - 3 pack <https://www.adafruit.com/product/450>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://github.com/adafruit/circuitpython/releases

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
"""

import digitalio
import adafruit_bus_device.spi_device as spi_device

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_74HC595.git"


class DigitalInOut:
    """Digital input/output of the 74HC595.  The interface is exactly the
    same as the ``digitalio.DigitalInOut`` class, however note that by design
    this device is OUTPUT ONLY!  Attempting to read inputs or set
    direction as input will raise an exception.
    """

    def __init__(self, pin_number, shift_register_74hc595):
        """Specify the pin number of the shift register (0...7) and
        ShiftRegister74HC595 instance.
        """
        self._pin = pin_number
        self._shift_register = shift_register_74hc595

    # kwargs in switch functions below are _necessary_ for compatibility
    # with DigitalInout class (which allows specifying pull, etc. which
    # is unused by this class).  Do not remove them, instead turn off pylint
    # in this case.
    # pylint: disable=unused-argument
    def switch_to_output(self, value=False, **kwargs):
        """``DigitalInOut switch_to_output``"""
        self.direction = digitalio.Direction.OUTPUT
        self.value = value

    def switch_to_input(self, **kwargs):  # pylint: disable=no-self-use
        """``switch_to_input`` is not supported."""
        raise RuntimeError("Digital input not supported.")

    # pylint: enable=unused-argument

    @property
    def value(self):
        """The value of the pin, either True for high or False for low."""
        return self._shift_register.gpio & (1 << self._pin) == (1 << self._pin)

    @value.setter
    def value(self, val):
        gpio = self._shift_register.gpio
        if val:
            gpio |= 1 << self._pin
        else:
            gpio &= ~(1 << self._pin)
        self._shift_register.gpio = gpio

    @property
    def direction(self):
        """``Direction`` can only be set to ``OUTPUT``."""
        return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(self, val):  # pylint: disable=no-self-use
        """``Direction`` can only be set to ``OUTPUT``."""
        if val != digitalio.Direction.OUTPUT:
            raise RuntimeError("Digital input not supported.")

    @property
    def pull(self):
        """Pull-up/down not supported, return None for no pull-up/down."""
        return None

    @pull.setter
    def pull(self, val):  # pylint: disable=no-self-use
        """Only supports null/no pull state."""
        if val is not None:
            raise RuntimeError("Pull-up and pull-down not supported.")


class ShiftRegister74HC595:
    """Initialise the 74HC595 on specified SPI bus."""

    def __init__(self, spi, latch):
        self._device = spi_device.SPIDevice(spi, latch, baudrate=1000000)
        self._gpio = bytearray(1)
        self._gpio[0] = 0x00

    @property
    def gpio(self):
        """The raw GPIO output register.  Each bit represents the
        output value of the associated pin (0 = low, 1 = high).
        """
        return self._gpio[0]

    @gpio.setter
    def gpio(self, val):
        self._gpio[0] = val & 0xFF
        with self._device as spi:
            # pylint: disable=no-member
            spi.write(self._gpio)

    def get_pin(self, pin):
        """Convenience function to create an instance of the DigitalInOut class
        pointing at the specified pin of this 74HC595 device .
        """
        assert 0 <= pin <= 7
        return DigitalInOut(pin, self)

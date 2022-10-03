# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

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
from adafruit_bus_device import spi_device

try:
    import typing  # pylint: disable=unused-import
    from microcontroller import Pin
    import busio
    from circuitpython_typing import ReadableBuffer
except ImportError:
    pass

__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/adafruit/Adafruit_CircuitPython_74HC595.git"


class DigitalInOut:
    """Digital input/output of the 74HC595.  The interface is exactly the
    same as the ``digitalio.DigitalInOut`` class, however note that by design
    this device is OUTPUT ONLY!  Attempting to read inputs or set
    direction as input will raise an exception.
    """

    _pin: Pin
    _byte_pos: int
    _byte_pin: int
    _shift_register: "ShiftRegister74HC595"

    def __init__(
        self,
        pin_number: Pin,
        shift_register_74hc595: "ShiftRegister74HC595",
    ) -> None:
        """Specify the pin number of the shift register (0...7) and
        ShiftRegister74HC595 instance.
        """
        self._pin = pin_number
        self._byte_pos = self._pin // 8
        self._byte_pin = self._pin % 8
        self._shift_register = shift_register_74hc595

    # kwargs in switch functions below are _necessary_ for compatibility
    # with DigitalInout class (which allows specifying pull, etc. which
    # is unused by this class).  Do not remove them, instead turn off pylint
    # in this case.
    # pylint: disable=unused-argument
    def switch_to_output(self, value: bool = False, **kwargs) -> None:
        """``DigitalInOut switch_to_output``"""
        self.direction = digitalio.Direction.OUTPUT
        self.value = value

    def switch_to_input(self, **kwargs) -> None:  # pylint: disable=no-self-use
        """``switch_to_input`` is not supported."""
        raise RuntimeError("Digital input not supported.")

    # pylint: enable=unused-argument

    @property
    def value(self) -> bool:
        """The value of the pin, either True for high or False for low."""
        return self._shift_register.gpio[self._byte_pos] & (1 << self._byte_pin) == (
            1 << self._byte_pin
        )

    @value.setter
    def value(self, val: bool) -> None:
        if (
            self._pin >= 0
            and self._pin < self._shift_register.number_of_shift_registers * 8
        ):
            gpio = self._shift_register.gpio
            if val:
                gpio[self._byte_pos] |= 1 << self._byte_pin
            else:
                gpio[self._byte_pos] &= ~(1 << self._byte_pin)
            self._shift_register.gpio = gpio

    @property
    def direction(self) -> digitalio.Direction.OUTPUT:
        """``Direction`` can only be set to ``OUTPUT``."""
        return digitalio.Direction.OUTPUT

    @direction.setter
    def direction(  # pylint: disable=no-self-use
        self,
        val: digitalio.Direction.OUTPUT,
    ) -> None:
        """``Direction`` can only be set to ``OUTPUT``."""
        if val != digitalio.Direction.OUTPUT:
            raise RuntimeError("Digital input not supported.")

    @property
    def pull(self) -> None:
        """Pull-up/down not supported, return None for no pull-up/down."""
        return None

    @pull.setter
    def pull(self, val: None) -> None:  # pylint: disable=no-self-use
        """Only supports null/no pull state."""
        if val is not None:
            raise RuntimeError("Pull-up and pull-down not supported.")


class ShiftRegister74HC595:
    """Initialise the 74HC595 on specified SPI bus, indicate the
    number of shift registers being used and optional baudrate.
    """

    _device: spi_device.SPIDevice
    _number_of_shift_registers: int
    _gpio: ReadableBuffer

    def __init__(
        self,
        spi: busio.SPI,
        latch: digitalio.DigitalInOut,
        number_of_shift_registers: int = 1,
        baudrate: int = 1000000,
    ) -> None:
        self._device = spi_device.SPIDevice(spi, latch, baudrate=baudrate)
        self._number_of_shift_registers = number_of_shift_registers
        self._gpio = bytearray(self._number_of_shift_registers)

    @property
    def number_of_shift_registers(self) -> int:
        """The number of shift register chips"""
        return self._number_of_shift_registers

    @property
    def gpio(self) -> ReadableBuffer:
        """The raw GPIO output register.  Each bit represents the
        output value of the associated pin (0 = low, 1 = high).
        """
        return self._gpio

    @gpio.setter
    def gpio(self, val: ReadableBuffer) -> None:
        self._gpio = val

        with self._device as spi:
            # pylint: disable=no-member
            spi.write(self._gpio)

    def get_pin(self, pin: int) -> DigitalInOut:
        """Convenience function to create an instance of the DigitalInOut class
        pointing at the specified pin of this 74HC595 device .
        """
        assert 0 <= pin <= (self._number_of_shift_registers * 8) - 1
        return DigitalInOut(pin, self)

"""Serial interface to control stepper motors on the Arduino Mega.

This module provides a MotorController class used by the Neuropuppet
project to send movement commands from a Raspberry Pi to the Arduino.
"""
from __future__ import annotations

import time
from typing import Optional

import serial


class MotorController:
    """Manage serial communication with the Arduino.

    Parameters
    ----------
    port: str
        Serial port (e.g. ``/dev/ttyACM0`` on Linux).
    baudrate: int
        Baud rate for the connection.
    timeout: float
        Read timeout in seconds.
    """

    def __init__(self, port: str = "/dev/ttyACM0", baudrate: int = 115200, timeout: float = 1.0) -> None:
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser: Optional[serial.Serial] = None
        self.connect()

    def connect(self) -> None:
        """Attempt to open the serial connection, retrying on failure."""
        while True:
            try:
                self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
                print(f"Connected to {self.port}")
                break
            except serial.SerialException as exc:
                print(f"Serial connection error: {exc}. Retrying in 2 seconds...")
                time.sleep(2)

    def _send(self, message: str) -> None:
        if not self.ser or not self.ser.is_open:
            self.connect()
        try:
            assert self.ser
            self.ser.write(message.encode("utf-8"))
        except serial.SerialException:
            print("Lost connection. Reconnecting...")
            self.connect()
            assert self.ser
            self.ser.write(message.encode("utf-8"))

    def move_motor(self, motor_id: int, steps: int) -> None:
        """Move a motor by a number of steps.

        Parameters
        ----------
        motor_id: int
            Motor index in the range 1-6.
        steps: int
            Positive or negative step count.
        """
        cmd = f"M{motor_id}:{steps}\n"
        self._send(cmd)

    def home_all(self) -> None:
        """Trigger the homing routine on the Arduino."""
        self._send("HOME\n")

    def close(self) -> None:
        if self.ser and self.ser.is_open:
            self.ser.close()


if __name__ == "__main__":
    controller = MotorController()
    try:
        controller.home_all()
        controller.move_motor(1, 200)
        controller.move_motor(2, -150)
        controller.move_motor(3, 100)
    finally:
        controller.close()

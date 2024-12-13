#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 15:43:33 2024

@author: epoirier1
"""
def calculate_crc_modbus(data: bytes) -> int:
    """
    Calculate the CRC-16-Modbus checksum for a given byte sequence.
    :param data: Input byte sequence
    :return: 16-bit CRC checksum as an integer
    """
    crc = 0xFFFF  # Initial CRC value

    for byte in data:
        crc ^= byte  # XOR with byte
        for _ in range(8):  # Process each bit
            if crc & 0x0001:  # If LSB is 1
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1

    return crc  # Final CRC value

# Modbus command excluding CRC
# modbus_command = b'\x01\x03\x00\x00\x00\x02'
modbus_command = b'\x01\x06\x20\x03\x00\x02'

# Calculate the CRC
crc = calculate_crc_modbus(modbus_command)

# Convert CRC to little-endian format
low_byte = crc & 0xFF
high_byte = (crc >> 8) & 0xFF

# Append CRC to the Modbus command
modbus_command_with_crc = modbus_command + bytes([low_byte, high_byte])

print(f"Command with CRC: {modbus_command_with_crc.hex().upper()}")

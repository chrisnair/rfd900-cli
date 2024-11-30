#!/usr/bin/env python3

import serial
import time
import argparse

def send_command(ser, command, expected_response="OK"):
    """
    Send a command to the RFD900 modem and wait for a response.
    """
    ser.write((command + "\r\n").encode())
    time.sleep(0.5)
    response = ser.readlines()
    response = [line.decode().strip() for line in response]
    
    if any(expected_response in line for line in response):
        return response
    else:
        raise ValueError(f"Command '{command}' failed. Response: {response}")

def set_netid(port, baudrate, netid):
    """
    Set the Net ID of the RFD900 modem.
    """
    try:
        with serial.Serial(port, baudrate, timeout=1) as ser:
            print(f"Connecting to modem on {port} at {baudrate} baud...")
            
            # Enter command mode
            time.sleep(4)
            ser.write(("+++").encode())
            time.sleep(4)
            print("Entered command mode.")
            
            response = send_command(ser,"ATS3?")
            print(response)

            # Set the Net ID
            send_command(ser, f"ATS3={netid}")
            print(f"Net ID set to {netid}.")
            
            # # Save settings
            # send_command(ser, "AT&W")
            # print("Settings saved.")
            
            # Exit command mode
            send_command(ser, "ATO")
            print("Exited command mode.")
    except Exception as e:
        print(f"Error: {e}")

def main():
    parser = argparse.ArgumentParser(description="Edit the Net ID of an RFD900 modem.")
    parser.add_argument("port", help="Serial port to which the RFD900 is connected (e.g., /dev/ttyUSB0).")
    parser.add_argument("netid", type=int, help="Net ID to set (0-65535).")
    parser.add_argument("--baudrate", type=int, default=57600, help="Baud rate for the connection (default: 57600).")
    args = parser.parse_args()

    set_netid(args.port, args.baudrate, args.netid)

if __name__ == "__main__":
    main()

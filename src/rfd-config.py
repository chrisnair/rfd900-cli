import time
import logging
from typing import List, Tuple, Optional
import serial
from serial.tools import list_ports
import cmd
import click

# Logging Configuration
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")


class ModemClient:
    """Handles communication with the RFD900 modem."""

    def __init__(self, port: str, baud_rate: int, timeout: float = 1.0):
        self.port = port
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.serial = None

    def connect(self):
        """Establish a connection with the modem."""
        try:
            logging.info(f"Connecting to modem on {self.port} at {self.baud_rate} baud...")
            self.serial = serial.Serial(self.port, self.baud_rate, timeout=self.timeout)
        except serial.SerialException as e:
            logging.error(f"Failed to connect to {self.port}: {e}")
            raise

    def disconnect(self):
        """Close the serial connection."""
        if self.serial and self.serial.is_open:
            logging.info(f"Closing connection to {self.port}")
            self.serial.close()

    def send_command(self, command: str, expect_response: bool = True) -> str:
        """Send an AT command and return the response."""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Serial connection is not open.")

        logging.debug(f"Sending command: {command}")
        self.serial.write(f"{command}\r\n".encode())
        self.serial.flush()

        if not expect_response:
            return ""

        response = []
        start_time = time.time()

        while (time.time() - start_time) < self.timeout:
            if self.serial.in_waiting:
                line = self.serial.readline().decode().strip()
                logging.debug(f"Received: {line}")
                response.append(line)
                if line in ("OK", "ERROR"):
                    break
            time.sleep(0.1)

        return "\n".join(response)

    def enter_command_mode(self) -> bool:
        """Ensure the modem enters command mode with strict guard timing and buffer handling."""
        if not self.serial or not self.serial.is_open:
            raise ConnectionError("Serial connection is not open.")

        logging.info("Attempting to enter command mode...")

        # Step 1: Ensure guard time silence before sending '+++'
        logging.debug("Waiting for guard time before '+++'.")
        time.sleep(2)

        # Step 2: Clear buffers to prevent concatenated input
        logging.debug("Clearing input/output buffers.")
        self.serial.reset_input_buffer()
        self.serial.reset_output_buffer()

        # Step 3: Send '+++' to trigger command mode
        logging.debug("Sending '+++'.")
        self.serial.write(b"+++")
        self.serial.flush()

        # Step 4: Wait for modem to process '+++'
        logging.debug("Waiting for guard time after '+++'.")
        time.sleep(2)

        # Step 5: Send 'AT' to verify command mode entry
        logging.debug("Sending 'AT' to verify command mode.")
        response = self.send_command("AT", expect_response=True)

        # Step 6: Validate response
        if "OK" in response:
            logging.info("Successfully entered command mode.")
            return True
        else:
            logging.error("Failed to enter command mode. Response: %s", response)
            return False


def detect_modems(baud_rate: int = 57600, timeout: float = 1.0) -> List[Tuple[str, str]]:
    """Detect all RFD900 modems connected to the system."""
    logging.info("Detecting RFD900 modems...")
    modems = []

    for port in list_ports.comports():
        try:
            logging.debug(f"Checking port {port.device}...")
            client = ModemClient(port.device, baud_rate, timeout)
            client.connect()

            # Attempt to enter command mode
            if client.enter_command_mode():
                version_info = client.send_command("ATI")
                modems.append((port.device, version_info))
                logging.info(f"Detected modem on {port.device}: {version_info}")

            client.disconnect()
        except Exception as e:
            logging.error(f"Error checking port {port.device}: {e}")
            continue

    return modems


class RFDShell(cmd.Cmd):
    """Interactive CLI shell for RFD900 configuration."""

    intro = "Welcome to the RFD900 configuration shell. Type help or ? to list commands.\n"
    prompt = "rfd-config> "

    def __init__(self, client: ModemClient):
        super().__init__()
        self.client = client

    def do_info(self, arg):
        """Display modem information."""
        try:
            print("Fetching modem information...")
            version = self.client.send_command("ATI")
            print(f"Version: {version}")
        except Exception as e:
            print(f"Error: {e}")

    def do_get(self, arg):
        """Get current parameter value. Usage: get PARAMETER_NAME"""
        try:
            response = self.client.send_command(f"ATS{arg}?")
            print(f"Parameter {arg}: {response}")
        except Exception as e:
            print(f"Error: {e}")

    def do_set(self, arg):
        """Set a parameter value. Usage: set PARAMETER_NAME VALUE"""
        try:
            param, value = arg.split()
            self.client.send_command(f"ATS{param}={value}")
            self.client.send_command("AT&W")  # Write changes to EEPROM
            print(f"Set {param} to {value}")
        except Exception as e:
            print(f"Error: {e}")

    def do_exit(self, arg):
        """Exit the shell."""
        print("Exiting...")
        return True


@click.command()
@click.option("--port", help="Serial port of the modem")
@click.option("--baud-rate", default=57600, help="Baud rate")
@click.option("--timeout", default=1.0, help="Command timeout in seconds")
@click.option("--verbose", is_flag=True, help="Enable verbose logging")
def main(port, baud_rate, timeout, verbose):
    """RFD900 Configuration Tool."""
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    if not port:
        modems = detect_modems(baud_rate, timeout)
        if not modems:
            logging.error("No RFD900 modems detected.")
            return

        if len(modems) > 1:
            print("Multiple modems detected:")
            for i, (device, version) in enumerate(modems, 1):
                print(f"{i}. {device} - {version}")
            choice = click.prompt("Select a modem (1-N)", type=int) - 1
            port = modems[choice][0]
        else:
            port = modems[0][0]

    client = ModemClient(port, baud_rate, timeout)
    client.connect()

    try:
        if client.enter_command_mode():
            shell = RFDShell(client)
            shell.cmdloop()
    finally:
        client.disconnect()


if __name__ == "__main__":
    main()

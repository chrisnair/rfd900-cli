
## Usage

### Basic Usage

Run the tool with automatic modem detection:
```bash
python rfd_config.py
```

### Command Line Options

```bash
python rfd_config.py [OPTIONS]

Options:
  --port TEXT          Serial port of modem (optional, will auto-detect if not specified)
  --baud-rate INTEGER  Baud rate (default: 57600)
  --timeout FLOAT      Timeout in seconds (default: 1.0)
  --verbose            Enable verbose logging
  --help               Show this message and exit
```

### Interactive Shell Commands

Once connected to a modem, the following commands are available:

- `info` - Display comprehensive modem information
- `params` - Show all current parameter values
- `get PARAMETER` - Get the value of a specific parameter
- `set PARAMETER VALUE` - Set the value of a specific parameter
- `factory_reset` - Reset all parameters to factory defaults
- `reboot` - Reboot the modem
- `exit` or `quit` - Exit the configuration shell

### Parameters

The tool supports configuration of the following parameters:

| Parameter | Range | Default | Description | Matching Required |
|-----------|--------|---------|-------------|------------------|
| FORMAT | 0-0 | 0 | EEPROM version (should not be changed) | No |
| SERIAL_SPEED | 2-115 | 57 | Serial speed (2=2400 ... 115=115200) | No |
| AIR_SPEED | 2-250 | 64 | Air data rate (2-250 kbps) | Yes |
| NETID | 0-499 | 25 | Network ID | Yes |
| TXPOWER | 0-30 | 20 | Transmit power in dBm | No |
| ECC | 0-1 | 1 | Error correcting code (0=disabled, 1=enabled) | Yes |
| MAVLINK | 0-1 | 1 | MAVLink framing (0=disabled, 1=enabled) | No |
| MIN_FREQ | 902000-927000 | 915000 | Min frequency in KHz | Yes |
| MAX_FREQ | 903000-928000 | 928000 | Max frequency in KHz | Yes |
| NUM_CHANNELS | 5-50 | 50 | Number of frequency hopping channels | Yes |
| DUTY_CYCLE | 10-100 | 100 | Transmit duty cycle % | No |
| NODEID | 0-29 | 2 | Node ID (0=base node) | No |
| NODEDESTINATION | 0-65535 | 65535 | Remote node ID (65535=broadcast) | No |

Note: Parameters marked with "Matching Required" must be set to the same value on both modems in a link.

## Example Usage

```bash
# Start the tool
$ python rfd_config.py

# View current modem information
rfd-config> info

# Check current network ID
rfd-config> get NETID

# Set new network ID
rfd-config> set NETID 100

# View all parameters
rfd-config> params

# Exit the tool
rfd-config> exit
```


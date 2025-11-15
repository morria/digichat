"""
Command-line interface entry point for DigiChat.
"""

import argparse
import sys
from pathlib import Path
from typing import Optional


def create_parser() -> argparse.ArgumentParser:
    """Create and configure the argument parser."""
    parser = argparse.ArgumentParser(
        description="DigiChat - Curses-based chat for amateur radio digital modes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              # Run with default settings
  %(prog)s --audio-device 2             # Use specific audio device
  %(prog)s --mode CW                    # Start in CW mode
  %(prog)s --hamlib --rig-model 1234    # Enable Hamlib control
        """,
    )

    # Audio settings
    audio_group = parser.add_argument_group("audio settings")
    audio_group.add_argument(
        "--audio-device",
        type=int,
        help="Audio device index (use --list-devices to see options)",
    )
    audio_group.add_argument(
        "--sample-rate", type=int, default=48000, help="Audio sample rate (default: 48000)"
    )
    audio_group.add_argument(
        "--list-devices", action="store_true", help="List available audio devices and exit"
    )

    # Digital mode settings
    mode_group = parser.add_argument_group("digital mode settings")
    mode_group.add_argument(
        "--mode",
        choices=["CW", "PSK31", "RTTY"],
        default="CW",
        help="Initial digital mode (default: CW)",
    )

    # Hamlib settings
    hamlib_group = parser.add_argument_group("hamlib settings")
    hamlib_group.add_argument("--hamlib", action="store_true", help="Enable Hamlib support")
    hamlib_group.add_argument("--rig-model", type=int, help="Hamlib rig model number")
    hamlib_group.add_argument(
        "--rig-port", type=str, default="/dev/ttyUSB0", help="Rig serial port"
    )

    # Configuration
    config_group = parser.add_argument_group("configuration")
    config_group.add_argument(
        "--config", type=Path, help="Path to configuration file (default: ~/.digichat/config.yaml)"
    )

    # Debug options
    debug_group = parser.add_argument_group("debug options")
    debug_group.add_argument("--debug", action="store_true", help="Enable debug logging")
    debug_group.add_argument(
        "--log-file", type=Path, help="Path to log file (default: ~/.digichat/digichat.log)"
    )

    return parser


def list_audio_devices() -> None:
    """List available audio devices."""
    try:
        import sounddevice as sd

        print("Available audio devices:")
        print(sd.query_devices())
    except ImportError:
        print("Error: sounddevice module not installed", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error listing devices: {e}", file=sys.stderr)
        sys.exit(1)


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point for the CLI."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.list_devices:
        list_audio_devices()
        return 0

    # TODO: Import and start the main application
    print("DigiChat is not yet implemented.")
    print("This is a placeholder for the curses-based application.")
    print(f"Mode: {args.mode}")
    print(f"Sample rate: {args.sample_rate}")
    if args.hamlib:
        print(f"Hamlib enabled: Model {args.rig_model}, Port {args.rig_port}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

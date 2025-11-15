"""
Configuration management for DigiChat.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class AudioConfig:
    """Audio input/output configuration."""

    device_index: Optional[int] = None
    sample_rate: int = 48000
    channels: int = 1
    chunk_size: int = 1024


@dataclass
class HamlibConfig:
    """Hamlib radio control configuration."""

    enabled: bool = False
    rig_model: Optional[int] = None
    rig_port: str = "/dev/ttyUSB0"
    poll_interval: float = 1.0  # seconds


@dataclass
class ModeConfig:
    """Digital mode specific configuration."""

    initial_mode: str = "CW"
    cw_wpm: int = 20  # Words per minute for CW
    psk31_squelch: float = 0.5  # PSK31 squelch level
    rtty_baud: int = 45  # RTTY baud rate (45.45 or 50)
    rtty_shift: int = 170  # RTTY shift in Hz


@dataclass
class UIConfig:
    """User interface configuration."""

    left_rail_width: int = 30  # Width of left configuration rail
    history_lines: int = 100  # Number of lines to keep in history
    color_scheme: str = "default"


@dataclass
class Config:
    """Main configuration container."""

    audio: AudioConfig = field(default_factory=AudioConfig)
    hamlib: HamlibConfig = field(default_factory=HamlibConfig)
    mode: ModeConfig = field(default_factory=ModeConfig)
    ui: UIConfig = field(default_factory=UIConfig)

    config_dir: Path = field(default_factory=lambda: Path.home() / ".digichat")
    log_file: Optional[Path] = None
    debug: bool = False

    @classmethod
    def load(cls, config_path: Optional[Path] = None) -> "Config":
        """
        Load configuration from file.

        Args:
            config_path: Path to configuration file. If None, uses default location.

        Returns:
            Config instance with loaded settings.
        """
        # TODO: Implement YAML loading
        config = cls()
        config.config_dir.mkdir(parents=True, exist_ok=True)
        return config

    def save(self, config_path: Optional[Path] = None) -> None:
        """
        Save configuration to file.

        Args:
            config_path: Path to save configuration. If None, uses default location.
        """
        # TODO: Implement YAML saving
        pass

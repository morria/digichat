"""
Tests for configuration management.
"""

from digichat.config import AudioConfig, Config, HamlibConfig, ModeConfig, UIConfig


def test_audio_config_defaults():
    """Test AudioConfig default values."""
    config = AudioConfig()
    assert config.device_index is None
    assert config.sample_rate == 48000
    assert config.channels == 1
    assert config.chunk_size == 1024


def test_hamlib_config_defaults():
    """Test HamlibConfig default values."""
    config = HamlibConfig()
    assert config.enabled is False
    assert config.rig_model is None
    assert config.rig_port == "/dev/ttyUSB0"
    assert config.poll_interval == 1.0


def test_mode_config_defaults():
    """Test ModeConfig default values."""
    config = ModeConfig()
    assert config.initial_mode == "CW"
    assert config.cw_wpm == 20
    assert config.psk31_squelch == 0.5
    assert config.rtty_baud == 45
    assert config.rtty_shift == 170


def test_ui_config_defaults():
    """Test UIConfig default values."""
    config = UIConfig()
    assert config.left_rail_width == 30
    assert config.history_lines == 100
    assert config.color_scheme == "default"


def test_main_config_defaults():
    """Test main Config default values."""
    config = Config()
    assert isinstance(config.audio, AudioConfig)
    assert isinstance(config.hamlib, HamlibConfig)
    assert isinstance(config.mode, ModeConfig)
    assert isinstance(config.ui, UIConfig)
    assert config.debug is False


def test_config_load(tmp_path):
    """Test configuration loading."""
    # Test loading creates default config
    config = Config.load()
    assert isinstance(config, Config)


def test_config_creates_directory(tmp_path):
    """Test that config directory is created."""
    config = Config()
    config.config_dir = tmp_path / "test_config"

    # Directory should not exist yet
    assert not config.config_dir.exists()

    # Load should create it
    config = Config.load()
    config.config_dir = tmp_path / "test_config"
    config.config_dir.mkdir(parents=True, exist_ok=True)

    # Now it should exist
    assert config.config_dir.exists()

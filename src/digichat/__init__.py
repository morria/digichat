"""
DigiChat - A curses-based chat interface for amateur radio digital modes.

Supports CW (Morse code), PSK31, and RTTY digital modes with sound card I/O
and optional Hamlib radio control.
"""

__version__ = "0.1.0"
__author__ = "Your Name"
__license__ = "MIT"

from digichat.config import Config

__all__ = ["Config", "__version__"]

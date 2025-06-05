import json
import os
from pathlib import Path

class Config:
    def __init__(self):
        self.config_path = Path("config")
        self.config_file = self.config_path / "settings.json"
        self.default_config = {
            "theme": "dark",
            "max_payloads_per_hour": 10,
            "default_port": 4444,
            "log_level": "INFO",
            "templates_dir": "templates",
            "output_dir": "output",
            "temp_dir": "temp",
            "encryption_key": "",  # Will be generated on first run
            "rate_limit": {
                "enabled": True,
                "max_requests": 10,
                "time_window": 3600  # 1 hour in seconds
            }
        }
        self._ensure_directories()
        self._load_config()

    def _ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.config_path,
            Path(self.default_config["templates_dir"]),
            Path(self.default_config["output_dir"]),
            Path(self.default_config["temp_dir"])
        ]
        for directory in directories:
            directory.mkdir(exist_ok=True)

    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.settings = json.load(f)
        else:
            self.settings = self.default_config
            self._save_config()

    def _save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key, default=None):
        """Get configuration value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set configuration value"""
        self.settings[key] = value
        self._save_config()
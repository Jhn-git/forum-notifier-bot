import json
import os
from pathlib import Path

SETTINGS_FILE = Path(__file__).parent.parent / "data" / "settings.json"

DEFAULT_SETTINGS = {
    "notification_channel_id": None,
    "error_channel_id": None,
    "monitored_forums": [],
    "embed_color": "#2f3136",
    "preview_length": 100
}


def load_settings():
    """Load settings from JSON file. Creates file with defaults if missing or corrupted."""
    try:
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r') as f:
                settings = json.load(f)
                # Ensure all default keys exist
                for key in DEFAULT_SETTINGS:
                    if key not in settings:
                        settings[key] = DEFAULT_SETTINGS[key]
                return settings
        else:
            # File doesn't exist, create with defaults
            save_settings(DEFAULT_SETTINGS)
            return DEFAULT_SETTINGS.copy()
    except (json.JSONDecodeError, Exception) as e:
        # File corrupted or other error, recreate with defaults
        print(f"Error loading settings: {e}. Recreating with defaults.")
        save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()


def save_settings(settings):
    """Save settings to JSON file."""
    os.makedirs(SETTINGS_FILE.parent, exist_ok=True)
    with open(SETTINGS_FILE, 'w') as f:
        json.dump(settings, f, indent=2)

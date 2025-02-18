#!/usr/bin/env python3
import os
import json

PROJECT_SETTINGS_FILE = "project_settings.json"

def load_project_settings(project_name):
    """Load settings for the given project."""
    settings = {}
    if os.path.exists(PROJECT_SETTINGS_FILE):
        try:
            with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                all_settings = json.load(f)
            settings = all_settings.get(project_name, {})
        except Exception as e:
            print("Error loading project settings:", e)
    return settings

def save_project_settings(project_name, project_settings):
    """Save the given settings for the project."""
    settings = {}
    if os.path.exists(PROJECT_SETTINGS_FILE):
        try:
            with open(PROJECT_SETTINGS_FILE, "r", encoding="utf-8") as f:
                settings = json.load(f)
        except Exception as e:
            print("Error loading project settings:", e)
    settings[project_name] = project_settings
    try:
        with open(PROJECT_SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except Exception as e:
        print("Error saving project settings:", e)

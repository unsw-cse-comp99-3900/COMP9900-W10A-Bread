#!/usr/bin/env python3
import os
import time
import glob
import re

def sanitize(text: str) -> str:
    """Return a sanitized string suitable for file names."""
    return re.sub(r'\W+', '', text)

def build_scene_identifier(project_name: str, hierarchy: list) -> str:
    """
    Create a unique scene identifier by combining the sanitized project name
    with the sanitized hierarchy list (e.g., [Act, Chapter, Scene]).
    """
    sanitized_project = sanitize(project_name)
    sanitized_hierarchy = [sanitize(item) for item in hierarchy]
    return f"{sanitized_project}-" + "-".join(sanitized_hierarchy)

def get_project_folder(project_name: str) -> str:
    """
    Return the full path to the project folder.
    Creates the folder if it doesn't already exist.
    """
    sanitized_project = sanitize(project_name)
    project_folder = os.path.join(os.getcwd(), "Projects", sanitized_project)
    if not os.path.exists(project_folder):
        os.makedirs(project_folder)
    return project_folder

def load_latest_autosave(project_name: str, hierarchy: list) -> str:
    """
    Load the content of the most recent autosave file for a given scene.
    Returns the content if found, or None otherwise.
    """
    scene_identifier = build_scene_identifier(project_name, hierarchy)
    project_folder = get_project_folder(project_name)
    pattern = os.path.join(project_folder, f"{scene_identifier}_*.txt")
    autosave_files = glob.glob(pattern)
    if not autosave_files:
        return None
    latest_file = max(autosave_files, key=os.path.getmtime)
    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading autosave file {latest_file}: {e}")
        return None

def cleanup_old_autosaves(project_folder: str, scene_identifier: str, max_files: int = 6) -> None:
    """
    Remove the oldest autosave files if the number of autosaves exceeds max_files.
    """
    pattern = os.path.join(project_folder, f"{scene_identifier}_*.txt")
    autosave_files = sorted(glob.glob(pattern))
    while len(autosave_files) > max_files:
        oldest = autosave_files.pop(0)
        try:
            os.remove(oldest)
            print("Removed old autosave file:", oldest)
        except Exception as e:
            print("Error removing old autosave file:", e)

def save_scene(project_name: str, hierarchy: list, content: str) -> str:
    """
    Save the scene content if it has changed since the last autosave.
    
    Parameters:
        project_name (str): The name of the project.
        hierarchy (list): List of strings representing the scene hierarchy (e.g., [Act, Chapter, Scene]).
        content (str): The scene content to save.
    
    Returns:
        The filepath of the new autosave file if saved, or None if no changes were detected.
    """
    # Check if the scene content has changed.
    last_content = load_latest_autosave(project_name, hierarchy)
    if last_content is not None and last_content.strip() == content.strip():
        print("No changes detected since the last autosave. Skipping autosave.")
        return None

    scene_identifier = build_scene_identifier(project_name, hierarchy)
    project_folder = get_project_folder(project_name)
    timestamp = time.strftime("%Y%m%d%H%M%S")
    filename = f"{scene_identifier}_{timestamp}.txt"
    filepath = os.path.join(project_folder, filename)

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print("Autosaved scene to", filepath)
    except Exception as e:
        print("Error during autosave:", e)
        return None

    cleanup_old_autosaves(project_folder, scene_identifier)
    return filepath

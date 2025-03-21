import os
import json
from PyQt5.QtWidgets import QMessageBox, QInputDialog, QApplication
from PyQt5.QtCore import Qt
from settings import llm_api_aggregator

def get_summary_prompts(project_name):
    """
    Load the 'Summary' prompts for the given project from its prompts JSON file.
    The file is assumed to be named as: prompts_<projectname_no_spaces>.json
    """
    prompts_file = "prompts.json"
    if os.path.exists(prompts_file):
        try:
            with open(prompts_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data.get("Summary", [])
        except Exception as e:
            print("Error loading summary prompts:", e)
    return []

def gather_child_content(item):
    """
    Recursively gather text content from all leaf nodes (assumed to be scenes)
    within the given QTreeWidgetItem.
    """
    content = ""
    if item.childCount() == 0:
        # Assume leaf items contain scene content stored in UserRole.
        data = item.data(0, Qt.UserRole)
        if data:
            if isinstance(data, dict):
                # Extract "content" if available; otherwise, use "summary"
                text = data.get("content", "") or data.get("summary", "")
            else:
                text = data
            content += text + "\n"
    else:
        for i in range(item.childCount()):
            child = item.child(i)
            content += gather_child_content(child)
    return content

def create_summary(project_window):
    """
    Implements the 'Create Summary' function for the project.
    
    Steps:
      1. Ensure an Act or Chapter (but not a Scene) is selected.
      2. Load all summary prompts from the project's prompts file.
      3. Let the user select one summary prompt.
      4. Gather all content from child (scene) nodes under the selected item.
      5. Build a final prompt combining the selected summary prompt and the gathered content.
      6. Send the final prompt to the LLM and display the generated summary.
      7. Save the summary to a file using the project's summary filename function.
    """
    current_item = project_window.tree.currentItem()
    if not current_item:
        QMessageBox.warning(project_window, "Summary", "Please select an Act or Chapter for summary creation.")
        return

    # Determine the tree level (0 for Act, 1 for Chapter; level 2 or deeper = Scene)
    level = 0
    temp = current_item
    while temp.parent():
        level += 1
        temp = temp.parent()
    if level >= 2:
        QMessageBox.warning(project_window, "Summary", "Please select an Act or Chapter (not a Scene) for summary creation.")
        return

    # Load summary prompts.
    summary_prompts = get_summary_prompts(project_window.project_name)
    if not summary_prompts:
        QMessageBox.warning(project_window, "Summary", "No summary prompts found. Please check your prompt options.")
        return
    # Build a list of prompt names to choose from.
    prompt_names = [p.get("name", "Unnamed") for p in summary_prompts]
    selected, ok = QInputDialog.getItem(project_window, "Select Summary Prompt",
                                        "Choose a summary prompt for summarization:",
                                        prompt_names, 0, False)
    if not ok or not selected:
        return
    # Retrieve the selected prompt's text.
    selected_prompt = None
    for p in summary_prompts:
        if p.get("name", "Unnamed") == selected:
            selected_prompt = p.get("text", "")
            break
    if not selected_prompt:
        QMessageBox.warning(project_window, "Summary", "Selected prompt not found.")
        return

    # Gather all child content (from scenes) recursively.
    child_content = gather_child_content(current_item)
    if not child_content.strip():
        QMessageBox.warning(project_window, "Summary", "No child scene content found to summarize.")
        return

    # Build the final prompt for the LLM.
    final_prompt = f"{selected_prompt}\n\nContent:\n{child_content}"
    project_window.statusBar().showMessage("Generating summary, please wait...", 5000)
    QApplication.processEvents()  # Update UI

    # Build the overrides dictionary to force local LLM usage.
    overrides = {
        "provider": p.get("provider", ""),
        "model": p.get("model", ""),
        "max_tokens": p.get("max_tokens", 2000),
        "temperature": p.get("temperature", 1.0)
    }

    generated_summary = WWApiAggregator.send_prompt_to_llm(final_prompt, overrides=overrides)
    if not generated_summary:
        QMessageBox.warning(project_window, "Summary", "LLM returned no output.")
        return

    # Display the generated summary in the editor.
    project_window.editor.setPlainText(generated_summary)
    # Update the tree item data with the generated summary.
    current_item.setData(0, Qt.UserRole, generated_summary)

    # Save the summary to a file using the project's summary filename function.
    # Ensure that the ProjectWindow class has a get_summary_filename method.
    try:
        filename = project_window.get_summary_filename(current_item)
    except AttributeError:
        # If the method does not exist, create a default one.
        import re, os, time
        def sanitize(text):
            return re.sub(r'\W+', '', text)
        hierarchy = []
        temp = current_item
        while temp:
            hierarchy.insert(0, temp.text(0).strip())
            temp = temp.parent()
        sanitized = [sanitize(x) for x in hierarchy]
        filename = f"{sanitize(project_window.project_name)}-Summary-" + "-".join(sanitized) + ".txt"
        project_folder = os.path.join(os.getcwd(), "Projects", sanitize(project_window.project_name))
        if not os.path.exists(project_folder):
            os.makedirs(project_folder)
        filename = os.path.join(project_folder, filename)
    
    try:
        with open(filename, "w", encoding="utf-8") as f:
            f.write(generated_summary)
        QMessageBox.information(project_window, "Summary", f"Summary created and saved to {filename}.")
    except Exception as e:
        QMessageBox.warning(project_window, "Summary", f"Could not save summary: {e}")

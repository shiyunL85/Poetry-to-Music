# src/data_processing.py
import json
import re

def clean_text(text):
    """Clean text by removing extra spaces and special characters."""
    text = re.sub(r'\s+', ' ', text.strip())  # Normalize spaces
    text = re.sub(r'[^\w\s\'.,!?]', '', text)  # Keep alphanumeric, spaces, and basic punctuation
    return text

def process_manual_input():
    """Process manually entered poem by user."""
    print("Enter your poem details:")
    title = input("Title: ").strip()
    author = input("Author: ").strip()
    print("Enter poem lines (press Enter twice to finish):")
    lines = []
    while True:
        line = input()
        if line == "":
            break
        cleaned_line = clean_text(line)
        if cleaned_line:
            lines.append(cleaned_line)
    
    # Validation
    if not title:
        title = "Untitled"
    if not author:
        author = "Unknown"
    if not lines:
        print("[Error] No valid lines entered")
        return None

    return {
        "title": title,
        "author": author,
        "lines": lines,
        "linecount": str(len(lines))
    }

def process_uploaded_file(file_path):
    """Process an uploaded poem file (JSON or text)."""
    try:
        # Check file extension
        if file_path.endswith('.json'):
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Validate JSON format
            if not isinstance(data, dict) or not all(key in data for key in ["title", "author", "lines"]):
                print("[Error] Invalid JSON format")
                return None
            title = clean_text(data.get("title", "Untitled"))
            author = clean_text(data.get("author", "Unknown"))
            lines = [clean_text(line) for line in data.get("lines", []) if clean_text(line)]
        elif file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8') as f:
                lines_raw = f.readlines()
            # Assume first line is title, second is author, rest are poem lines
            if len(lines_raw) < 3:
                print("[Error] Text file too short")
                return None
            title = clean_text(lines_raw[0].strip() or "Untitled")
            author = clean_text(lines_raw[1].strip() or "Unknown")
            lines = [clean_text(line) for line in lines_raw[2:] if clean_text(line)]
        else:
            print("[Error] Unsupported file format")
            return None

        # Validation
        if not lines:
            print("[Error] No valid lines found")
            return None

        return {
            "title": title,
            "author": author,
            "lines": lines,
            "linecount": str(len(lines))
        }
    except Exception as e:
        print(f"[Error] Failed to process file {file_path}: {e}")
        return None

def process_poem(config, poem_source, uploaded_file=None):
    """
    Process poem input and return standardized format.

    Args:
        config (dict): Configuration dictionary.
        poem_source (str): Source of poem ('search', 'manual', 'upload').
        uploaded_file (str, optional): Path to uploaded file if source is 'upload'.

    Returns:
        dict: Standardized poem dictionary or None if failed.
    """
    if poem_source == "manual":
        return process_manual_input()
    elif poem_source == "upload":
        if not uploaded_file:
            print("[Error] No file path provided for upload")
            return None
        return process_uploaded_file(uploaded_file)
    elif poem_source == "search":
        # This will be handled in main.py with search logic
        return None
    else:
        print("[Error] Invalid poem source")
        return None
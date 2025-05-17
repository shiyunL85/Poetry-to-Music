# main.py
import json
from src.data_processing import process_poem as process_data
from src.nlp_analysis import process_poem as process_nlp
from src.music_mapping import process_poem as process_music_mapping
from src.recitation_generation import process_poem as process_recitation
from src.melody_generation import process_poem as process_melody
from src.music_synthesis import process_poem as process_synthesis

def load_config():
    """Load configuration from config.json."""
    with open("config/config.json", "r") as f:
        return json.load(f)

def load_poetry_data(file_path):
    """Load poetry data from a JSON file."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[Error] Failed to load {file_path}: {e}")
        return []

def search_poem(poetry_data):
    """Search for a poem in the dataset."""
    if not poetry_data:
        print("[Error] No poems available")
        return None

    query = input("Enter search term (title, author, or keyword): ").strip().lower()
    matches = []
    for i, poem in enumerate(poetry_data):
        title = poem.get("title", "").lower()
        author = poem.get("author", "").lower()
        keywords = [kw.lower() for kw in poem.get("keywords", [])] if "keywords" in poem else []
        if query in title or query in author or any(query in kw for kw in keywords):
            matches.append((i, poem))

    if not matches:
        print(f"[Error] No poems found matching '{query}'")
        return None
    elif len(matches) == 1:
        return matches[0][1]
    else:
        print("Multiple matches found:")
        for i, (index, poem) in enumerate(matches):
            print(f"{i+1}. [{index}] {poem['title']} by {poem['author']}")
        try:
            match_choice = int(input(f"Select match (1 to {len(matches)}): ")) - 1
            if 0 <= match_choice < len(matches):
                return matches[match_choice][1]
            print("[Error] Invalid selection")
            return None
        except ValueError:
            print("[Error] Selection must be a number")
            return None

def main():
    config = load_config()

    # Display system intro
    print("=== Poetry to Music System ===")
    print("Welcome! This system transforms poems into musical recitations.")
    print("You can select a poem from our database, input your own, or upload a file.")
    print("The system will analyze the poem, generate music, create a recitation, and mix them together.")
    print("=================================")

    first_iteration = True  

    while True:
        if not first_iteration:
            confirm = input("Do you want to continue? (yes/no): ").strip().lower()
            if confirm not in ["yes", "y"]:
                if confirm in ["no", "n"]:
                    print("Exiting the system.")
                else:
                    print("[Error] Invalid input. Please enter 'yes' or 'no'.")
                return

        first_iteration = False  

        # User selection
        print("Select an option:")
        print("1. Search for a poem in the database")
        print("2. Manually enter a poem")
        print("3. Upload a poem file")
        choice = input("Enter 1, 2, or 3: ").strip()

        # Get poem
        poem = None
        if choice == "1":
            poetry_data = load_poetry_data(config["nlp_analysis"]["input_file"])
            poem = search_poem(poetry_data)
        elif choice == "2":
            poem = process_data(config, "manual")
        elif choice == "3":
            file_path = input("Enter the path to your poem file: ").strip()
            poem = process_data(config, "upload", file_path)
        else:
            print("[Error] Invalid choice")
            return

        if not poem:
            print("[Error] Failed to obtain a poem")
            return

        # Print the poem
        print("\n[Poem Selected]")
        if isinstance(poem, dict):  # If poem is a dictionary, print its details
            print(f"Title: {poem.get('title', 'Unknown')}")
            print(f"Author: {poem.get('author', 'Unknown')}")
            print(f"Content:\n{poem.get('lines', 'No content available')}")
        else:  # If poem is a string or other format
            print(poem)

        # Step 1: NLP Analysis
        analyzed_poem = process_nlp(config["nlp_analysis"], poem)
        if not analyzed_poem:
            print("[Error] NLP analysis failed")
            return

        # Step 2: Music Mapping
        mapped_poem = process_music_mapping(config.get("music_mapping", {}), analyzed_poem)
        if not mapped_poem:
            print("[Error] Music mapping failed")
            return

        # Step 3: Recitation Generation
        recitation_config = config.get("recitation_generation", {})
        updated_poem, recitation_audio = process_recitation(recitation_config, mapped_poem)
        if not updated_poem or not recitation_audio:
            print("[Error] Recitation generation failed")
            return

        # Step 4: Melody Generation
        melody_config = config.get("melody_generation", {})
        final_poem, pm_a, pm_b = process_melody(melody_config, updated_poem, recitation_audio)
        if not final_poem or not pm_a or not pm_b:
            print("[Error] Melody generation failed")
            return

        # Step 5: Music Synthesis
        synthesis_config = config.get("music_synthesis", {})
        final_audio_a, final_audio_b = process_synthesis(synthesis_config, final_poem, recitation_audio, pm_a, pm_b)
        if not final_audio_a or not final_audio_b:
            print("[Error] Music synthesis failed")
            return

        print("[Success] Pipeline completed successfully!")
        break

if __name__ == "__main__":
    main()
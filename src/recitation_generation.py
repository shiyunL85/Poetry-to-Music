# src/recitation_generation.py
import os
import io
from datetime import datetime
from gtts import gTTS
from pydub import AudioSegment
from openai import OpenAI
import re

def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters for Windows.

    Args:
        filename (str): The original filename.

    Returns:
        str: A sanitized filename safe for Windows.
    """
    # Replace spaces with underscores
    filename = filename.replace(" ", "_")
    # Remove or replace invalid characters (<, >, :, ", /, \, |, ?, *)
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, "", filename)
    # Remove any control characters (ASCII 0-31)
    filename = re.sub(r'[\x00-\x1F]', "", filename)
    # Ensure the filename is not empty after sanitization
    if not filename:
        filename = "untitled"
    # Truncate to a reasonable length to avoid path length issues (e.g., 100 characters)
    filename = filename[:100]
    return filename

def adjust_lyrics(lines, api_key, model="gpt-3.5-turbo"):
    """
    Adjust lyrics using OpenAI API to have approximately 8 syllables per line.

    Args:
        lines (list): List of poem lines.
        api_key (str): OpenAI API key.
        model (str): OpenAI model to use.

    Returns:
        list: Adjusted lines.
    """
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)

        # Construct prompt
        prompt = (
            "Adjust the following poem lines to have approximately 8 syllables each "
            "while preserving the meaning and tone:\n\n"
            + "\n".join(lines)
        )

        # Call OpenAI API
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant skilled in poetry."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7
        )

        # Extract adjusted lines
        adjusted_text = response.choices[0].message.content.strip()
        adjusted_lines = adjusted_text.split("\n")
        
        # Ensure the number of lines matches
        if len(adjusted_lines) != len(lines):
            print("[Warning] Number of adjusted lines does not match original. Using original lines.")
            return lines
        
        return adjusted_lines
    except Exception as e:
        print(f"[Error] Failed to adjust lyrics with OpenAI: {e}")
        return lines

def generate_recitation(lines):
    """
    Generate recitation audio for each line using gTTS.

    Args:
        lines (list): List of lines to synthesize.

    Returns:
        AudioSegment: Combined recitation audio with pauses.
    """
    output_segments = []
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            tts = gTTS(text=line, lang="en")
            mp3_fp = io.BytesIO()
            tts.write_to_fp(mp3_fp)
            mp3_fp.seek(0)
            segment = AudioSegment.from_file(mp3_fp, format="mp3")
            output_segments.append(segment)
            output_segments.append(AudioSegment.silent(duration=500))  # 0.5s pause
        except Exception as e:
            print(f"[Warning] Failed to synthesize line {i+1}: {e}")
            output_segments.append(AudioSegment.silent(duration=500))

    if not output_segments:
        print("[Error] No audio segments generated")
        return None

    return sum(output_segments)

def process_poem(config, poem):
    """
    Generate recitation audio for the poem and calculate its length.

    Args:
        config (dict): Configuration dictionary with parameters.
        poem (dict): Poem dictionary with lines and music params.

    Returns:
        tuple: (Updated poem dictionary, AudioSegment object) or (None, None) if failed.
    """
    try:
        # Configure ffmpeg
        ffmpeg_bin_path = config.get("ffmpeg_bin_path", "E:/Program Files/ffmpeg/bin")
        os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
        AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
        AudioSegment.ffprobe = os.path.join(ffmpeg_bin_path, "ffprobe.exe")

        # Ask user if they want to adjust lyrics
        print("\nDo you want to adjust the poem's lyrics for recitation? (e.g., normalize to 8 syllables per line)")
        adjust_choice = input("Enter 'yes' or 'no': ").strip().lower()
        if adjust_choice == "yes":
            # Use OpenAI to adjust lyrics
            api_key = config.get("openai_api_key")
            model = config.get("openai_model", "gpt-3.5-turbo")
            if not api_key:
                print("[Error] OpenAI API key not provided in config")
                return None, None
            adjusted_lyrics = adjust_lyrics(poem["lines"], api_key, model)
            poem["adjusted_lyrics"] = adjusted_lyrics
            lines_to_use = adjusted_lyrics
            # Print adjusted lyrics
            print("\n=== Adjusted Lyrics ===")
            for i, line in enumerate(adjusted_lyrics, 1):
                print(f"Line {i}: {line}")
            print("=======================\n")
        else:
            lines_to_use = poem["lines"]

        # Generate recitation audio
        recitation_audio = generate_recitation(lines_to_use)
        if not recitation_audio:
            return None, None

        # Calculate recitation length (in seconds)
        recitation_length = len(recitation_audio) / 1000.0  # Convert ms to seconds
        poem["recitation_length"] = recitation_length

        # # Sanitize the title for the filename
        # title = sanitize_filename(poem.get("title", "untitled"))
        # timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        # output_filename = f"{title}_recitation_{timestamp}.wav"
        # output_path = os.path.join("output", output_filename)
        # recitation_audio.export(output_path, format="wav")

        # # Print results
        # print("\n=== Recitation Generation Results ===")
        # print(f"Recitation Length: {recitation_length:.2f} seconds")
        # print(f"Recitation Audio Saved To: {output_path}")
        # print("=====================================\n")

        print("\n=== Recitation Generation Results ===")
        print(f"Recitation Length: {recitation_length:.2f} seconds")
        print("=====================================\n")


        return poem, recitation_audio
    except Exception as e:
        print(f"[Error] Failed to generate recitation: {e}")
        return None, None
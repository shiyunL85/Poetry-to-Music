# src/music_synthesis.py
import os
import re
from datetime import datetime
from pydub import AudioSegment
import pretty_midi
from midi2audio import FluidSynth

def sanitize_filename(filename):
    """
    Sanitize a filename by removing or replacing invalid characters for Windows.

    Args:
        filename (str): The original filename.

    Returns:
        str: A sanitized filename safe for Windows.
    """
    filename = filename.replace(" ", "_")
    invalid_chars = r'[<>:"/\\|?*]'
    filename = re.sub(invalid_chars, "", filename)
    filename = re.sub(r'[\x00-\x1F]', "", filename)
    if not filename:
        filename = "untitled"
    filename = filename[:100]
    return filename

def midi_to_wav(pm, output_midi_file, output_wav_file, soundfont_path, ffmpeg_bin_path):
    """
    Convert a PrettyMIDI object to a WAV file using FluidSynth.

    Args:
        pm (PrettyMIDI): The PrettyMIDI object to convert.
        output_midi_file (str): Path to save the temporary MIDI file.
        output_wav_file (str): Path to save the WAV file.
        soundfont_path (str): Path to the SoundFont file.
        ffmpeg_bin_path (str): Path to the ffmpeg binary directory.

    Returns:
        AudioSegment: The generated audio segment, or a silent segment if conversion fails.
    """
    try:
        # Ensure paths are absolute
        output_midi_file = os.path.abspath(output_midi_file)
        output_wav_file = os.path.abspath(output_wav_file)
        soundfont_path = os.path.abspath(soundfont_path)

        # Save the PrettyMIDI object to a MIDI file
        pm.write(output_midi_file)
        print(f"Temporary MIDI file saved: {output_midi_file}")

        # Set up pydub with ffmpeg
        if ffmpeg_bin_path:
            os.environ["PATH"] += os.pathsep + ffmpeg_bin_path
            AudioSegment.converter = os.path.join(ffmpeg_bin_path, "ffmpeg.exe")
            AudioSegment.ffprobe = os.path.join(ffmpeg_bin_path, "ffprobe.exe")

        # Convert MIDI to WAV using FluidSynth
        fs = FluidSynth(soundfont_path)
        fs.midi_to_audio(output_midi_file, output_wav_file)
        print(f"Melody converted to WAV: {output_wav_file}")

        # Load the WAV file
        audio = AudioSegment.from_wav(output_wav_file)
        return audio

    except Exception as e:
        print(f"[Error] Failed to convert MIDI to WAV: {e}")
        duration_ms = int(pm.get_end_time() * 1000)
        audio = AudioSegment.silent(duration=duration_ms)
        audio.export(output_wav_file, format="wav")
        print(f"Fallback WAV file created: {output_wav_file}")
        return audio

def mix_audio(recitation_audio, melody_audio, recitation_volume, melody_volume):
    """
    Mix recitation audio with melody audio, applying volume adjustments from config.

    Args:
        recitation_audio (AudioSegment): The recitation audio.
        melody_audio (AudioSegment): The melody audio.
        recitation_volume (float): Volume adjustment for recitation in dB.
        melody_volume (float): Volume adjustment for melody in dB.

    Returns:
        AudioSegment: The mixed audio.
    """
    try:
        # Ensure both audio segments are the same length
        if len(recitation_audio) < len(melody_audio):
            padding = AudioSegment.silent(duration=len(melody_audio) - len(recitation_audio))
            recitation_audio = recitation_audio + padding
        elif len(recitation_audio) > len(melody_audio):
            padding = AudioSegment.silent(duration=len(recitation_audio) - len(melody_audio))
            melody_audio = melody_audio + padding

        # Apply volume adjustments
        recitation_audio = recitation_audio + recitation_volume
        melody_audio = melody_audio + melody_volume

        # Mix the audio
        mixed_audio = melody_audio.overlay(recitation_audio)
        return mixed_audio

    except Exception as e:
        print(f"[Error] Failed to mix audio: {e}")
        return recitation_audio  # Fallback to recitation audio

def process_poem(config, poem, recitation_audio, pm_a, pm_b):
    """
    Synthesize the final audio by mixing recitation with melodies for Plan A and Plan B.

    Args:
        config (dict): Configuration dictionary.
        poem (dict): Poem dictionary with metadata.
        recitation_audio (AudioSegment): The recitation audio.
        pm_a (PrettyMIDI): PrettyMIDI object for Plan A.
        pm_b (PrettyMIDI): PrettyMIDI object for Plan B.

    Returns:
        tuple: (AudioSegment for Plan A, AudioSegment for Plan B) or (None, None) if failed.
    """
    try:
        # Sanitize the title for filenames
        title = sanitize_filename(poem.get("title", "untitled"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Get paths and volume settings from config
        soundfont_path = config.get("soundfont_path")
        ffmpeg_bin_path = config.get("ffmpeg_bin_path")
        recitation_volume = config.get("recitation_volume", 0)  # Default to 0 dB
        melody_volume = config.get("melody_volume", -3)        # Default to -3 dB
        if not soundfont_path:
            raise ValueError("Soundfont path not provided in config")

        # --- Plan A: Convert MIDI to WAV and Mix ---
        temp_midi_file_a = os.path.join("output", f"{title}_temp_plana_{timestamp}.mid")
        melody_wav_file_a = os.path.join("output", f"{title}_melody_plana_{timestamp}.wav")
        melody_audio_a = midi_to_wav(pm_a, temp_midi_file_a, melody_wav_file_a, soundfont_path, ffmpeg_bin_path)

        mixed_audio_a = mix_audio(recitation_audio, melody_audio_a, recitation_volume, melody_volume)
        final_output_a = os.path.join("output", f"{title}_final_song_plana_{timestamp}.wav")
        final_output_a = os.path.abspath(final_output_a)
        mixed_audio_a.export(final_output_a, format="wav")
        print(f"Final Plan A audio saved: {final_output_a}")

        if os.path.exists(temp_midi_file_a):
            os.remove(temp_midi_file_a)

        # --- Plan B: Convert MIDI to WAV and Mix ---
        temp_midi_file_b = os.path.join("output", f"{title}_temp_planb_{timestamp}.mid")
        melody_wav_file_b = os.path.join("output", f"{title}_melody_planb_{timestamp}.wav")
        melody_audio_b = midi_to_wav(pm_b, temp_midi_file_b, melody_wav_file_b, soundfont_path, ffmpeg_bin_path)

        mixed_audio_b = mix_audio(recitation_audio, melody_audio_b, recitation_volume, melody_volume)
        final_output_b = os.path.join("output", f"{title}_final_song_planb_{timestamp}.wav")
        final_output_b = os.path.abspath(final_output_b)
        mixed_audio_b.export(final_output_b, format="wav")
        print(f"Final Plan B audio saved: {final_output_b}")

        if os.path.exists(temp_midi_file_b):
            os.remove(temp_midi_file_b)

        print("\n=== Music Synthesis Results ===")
        print(f"Plan A Final Audio: {final_output_a}")
        print(f"Plan B Final Audio: {final_output_b}")
        print("=====================================\n")

        return mixed_audio_a, mixed_audio_b

    except Exception as e:
        print(f"[Error] Failed to synthesize music: {e}")
        return None, None
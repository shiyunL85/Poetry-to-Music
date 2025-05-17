# src/melody_generation.py
import os
import random
import pretty_midi
from datetime import datetime
import note_seq
from magenta.models.music_vae import configs
from magenta.models.music_vae.trained_model import TrainedModel
from note_seq.protobuf import music_pb2
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

# --- Plan A: Classmate's melody generation logic ---
def build_scale(base_note, mode='minor', octaves=3):
    """Build a scale based on the mode and base note."""
    if mode == 'minor':
        scale_degrees = [0, 2, 3, 5, 7, 8, 10, 12]
    elif mode == 'major':
        scale_degrees = [0, 2, 4, 5, 7, 9, 11, 12]
    elif mode == 'modal':
        scale_degrees = [0, 2, 3, 5, 7, 9, 10, 12]
    else:
        scale_degrees = [0, 2, 4, 5, 7, 9, 11, 12]
    
    notes = []
    for octave in range(octaves):
        for interval in scale_degrees:
            note = base_note + interval + 12 * octave
            if note <= 127:
                notes.append(note)
    return sorted(list(set(notes)))

def generate_complex_melody(base_note, mode='minor', num_notes=64):
    """Generate a melody based on the scale and number of notes."""
    scale = build_scale(base_note, mode=mode, octaves=3)
    current_index = len(scale) // 2  # Start from the middle of the scale
    melody = []
    for _ in range(num_notes):
        melody.append(scale[current_index])
        step = random.choices([-2, -1, 0, 1, 2], weights=[1, 3, 4, 3, 1])[0]
        current_index += step
        current_index = max(0, min(current_index, len(scale) - 1))
    return melody

# --- Plan B: Your previous logic using MusicVAE ---
def generate_melody_musicvae(config, poem, recitation_length, tempo):
    """Generate melody using MusicVAE for Plan B."""
    music_params = poem["music_params"]
    
    # Initialize MusicVAE model
    checkpoint_path = config.get("musicvae_checkpoint_path")
    if not checkpoint_path:
        raise ValueError("MusicVAE checkpoint path not provided in config")
    
    vae_config = configs.CONFIG_MAP['cat-mel_2bar_big']
    model = TrainedModel(vae_config, batch_size=1, checkpoint_dir_or_path=checkpoint_path)
    print("MusicVAE model loaded successfully!")

    # Calculate number of 2-bar segments based on recitation length
    # Each 2-bar segment at 120 BPM (default for cat-mel_2bar_big) is 4 seconds
    segment_duration = 4.0  # 2 bars at 120 BPM = 4 seconds
    num_segments = max(1, int(recitation_length / segment_duration))
    
    # Generate melody using MusicVAE
    generated_sequences = model.sample(n=num_segments, length=16)  # 16 steps per 2-bar segment
    
    # Convert to PrettyMIDI
    pm = pretty_midi.PrettyMIDI()
    instrument = pretty_midi.Instrument(program=0)  # Default to piano
    
    for sequence in generated_sequences:
        # Adjust pitches based on mode and base_note
        for note in sequence.notes:
            note.pitch += music_params["base_note"] - 60  # Shift to match base_note (C4 = 60)
            pm_note = pretty_midi.Note(
                velocity=int(note.velocity),
                pitch=note.pitch,
                start=note.start_time,
                end=note.end_time
            )
            instrument.notes.append(pm_note)
    
    pm.instruments.append(instrument)
    
    # Adjust total duration to match recitation_length
    current_duration = pm.get_end_time()
    if current_duration > 0:
        scale_factor = recitation_length / current_duration
        for instrument in pm.instruments:
            for note in instrument.notes:
                note.start *= scale_factor
                note.end *= scale_factor
    
    return pm

# --- Shared Functions ---
def add_chords(pm, chord_progression, total_duration):
    """Add chords to the PrettyMIDI object based on the chord progression."""
    chord_instrument = pretty_midi.Instrument(program=0)  # Piano for chords
    chord_idx = 0
    current_time = 0.0
    chord_duration = total_duration / len(chord_progression)  # Distribute chords evenly
    while current_time < total_duration:
        chord = chord_progression[chord_idx % len(chord_progression)]
        for note in chord:
            pm_note = pretty_midi.Note(
                velocity=80,  # Softer for chords
                pitch=note,
                start=current_time,
                end=current_time + chord_duration
            )
            chord_instrument.notes.append(pm_note)
        current_time += chord_duration
        chord_idx += 1
    pm.instruments.append(chord_instrument)

def save_melody(pm, instruments, output_midi_file):
    """Save PrettyMIDI object to MIDI file."""
    # Ensure path is absolute
    output_midi_file = os.path.abspath(output_midi_file)
    
    # Assign instruments to melody tracks
    num_segments = len(instruments)
    if len(pm.instruments) > 1:  # If chords are added, the last instrument is for chords
        melody_instrument = pm.instruments[0]
        total_notes = len(melody_instrument.notes)
        segment_length = total_notes // num_segments
        new_instruments = []
        for i, instrument_name in enumerate(instruments):
            try:
                program = pretty_midi.instrument_name_to_program(instrument_name)
            except ValueError:
                program = 0  # Default to Acoustic Grand Piano
            new_instrument = pretty_midi.Instrument(program=program)
            start_idx = i * segment_length
            end_idx = start_idx + segment_length if i < num_segments - 1 else total_notes
            for note in melody_instrument.notes[start_idx:end_idx]:
                new_instrument.notes.append(note)
            new_instruments.append(new_instrument)
        # Replace melody instrument with segmented instruments
        pm.instruments = new_instruments + pm.instruments[1:]  # Keep chord instrument
    
    # Save MIDI file
    pm.write(output_midi_file)
    print(f"Melody saved as MIDI file: {output_midi_file}")
    
    return pm

def process_poem(config, poem, recitation_audio):
    """
    Generate melodies using both Plan A and Plan B, saving only MIDI files.

    Args:
        config (dict): Configuration dictionary.
        poem (dict): Poem dictionary with music params and recitation length.
        recitation_audio (AudioSegment): Recitation audio object.

    Returns:
        tuple: (Updated poem dictionary, Plan A PrettyMIDI, Plan B PrettyMIDI) or (None, None, None) if failed.
    """
    try:
        music_params = poem["music_params"]
        recitation_length = poem["recitation_length"]
        tempo = music_params["tempo"]
        
        # Sanitize the title for the filename
        title = sanitize_filename(poem.get("title", "untitled"))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # --- Plan A: Classmate's logic ---
        # Calculate number of notes based on recitation length and tempo
        num_notes = int(recitation_length * (tempo / 60))
        num_notes = max(16, num_notes)  # Ensure minimum notes
        note_duration = recitation_length / num_notes  # Duration per note in seconds

        melody_a = generate_complex_melody(
            base_note=music_params["base_note"],
            mode=music_params["mode"],
            num_notes=num_notes
        )
        
        # Create PrettyMIDI object for Plan A
        pm_a = pretty_midi.PrettyMIDI()
        instrument_a = pretty_midi.Instrument(program=0)  # Temporary instrument
        current_time = 0.0
        for note in melody_a:
            pm_note = pretty_midi.Note(
                velocity=100,
                pitch=note,
                start=current_time,
                end=current_time + note_duration
            )
            instrument_a.notes.append(pm_note)
            current_time += note_duration
        pm_a.instruments.append(instrument_a)
        
        # Add chords
        add_chords(pm_a, music_params["chord_progression"], recitation_length)
        
        # # Save Plan A melody (MIDI only)
        # output_midi_file_a = os.path.join("output", f"{title}_melody_plana_{timestamp}.mid")
        # pm_a = save_melody(
        #     pm_a,
        #     music_params["instruments"],
        #     output_midi_file_a
        # )
        
        print("\n=== Plan A Melody Generation Results ===")
        print(f"Number of Notes: {len(melody_a)}")
        print(f"Total Duration: {pm_a.get_end_time():.2f} seconds")
        print("=====================================\n")

        # --- Plan B: Your logic using MusicVAE ---
        pm_b = generate_melody_musicvae(config, poem, recitation_length, tempo)
        
        # Add chords
        add_chords(pm_b, music_params["chord_progression"], recitation_length)
        
        # # Save Plan B melody (MIDI only)
        # output_midi_file_b = os.path.join("output", f"{title}_melody_planb_{timestamp}.mid")
        # pm_b = save_melody(
        #     pm_b,
        #     music_params["instruments"],
        #     output_midi_file_b
        # )
        
        print("\n=== Plan B Melody Generation Results ===")
        print(f"Total Duration: {pm_b.get_end_time():.2f} seconds")
        print("=====================================\n")

        return poem, pm_a, pm_b
    except Exception as e:
        print(f"[Error] Failed to generate melody: {e}")
        return None, None, None
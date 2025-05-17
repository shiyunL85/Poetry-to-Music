# Poetry to Music Pipeline

This project transforms poems into musical recitations by generating spoken audio and melodies, then mixing them into final audio files. It analyzes a poem's sentiment and structure, maps these to musical parameters, generates a recitation, creates a melody, and produces a final audio track.

## Features

- **Poem Input**: Select a poem from a database, enter manually, or upload a JSON file.
- **NLP Analysis**: Analyzes the poem's sentiment and structure.
- **Music Mapping**: Maps poem characteristics to musical parameters (e.g., tempo, mode, chords).
- **Recitation Generation**: Uses OpenAI's TTS to create spoken audio of the poem.
- **Melody Generation**: Generates a melody to match the poem's mood and duration.
- **Music Synthesis**: Mixes the recitation with the melody to produce a final audio file.

## System Requirements

- **Operating System**: Windows, Linux, or macOS.
- **Python**: Version 3.8 or higher.
- **Hardware**:
  - At least 4GB of RAM (8GB recommended for MusicVAE).
  - Optional: NVIDIA GPU for faster processing (CPU works but is slower).
- **Disk Space**: Approximately 2GB for dependencies and checkpoints.
- **Internet Connection**: Required for OpenAI TTS API calls and downloading dependencies.

## Project Structure

```
poetry-to-music/
├── config/
│   └── config.json         # Configuration file
├── data/
│   └── poems.json          # Poem database
├── output/                 # Stores all audio outputs
├── src/
│   ├── data_processing.py  # Handles poem input
│   ├── nlp_analysis.py     # Analyzes poem sentiment and structure
│   ├── music_mapping.py    # Maps poem to musical parameters
│   ├── recitation_generation.py  # Generates recitation audio
│   ├── melody_generation.py      # Generates melodies
│   ├── music_synthesis.py        # Mixes audio and saves final output
├── main.py                 # Main script to run the pipeline
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation
```

- All audio files (e.g., recitation, melody, final output) are saved in the `output` directory.

## Prerequisites

Before running the project, install the required software and set up your environment.

### 1. Install Python

- **Version**: Python 3.8 or higher.

- **Download**: Install from python.org.

- **Verify**:

  ```
  python --version
  ```

### 2. Install Conda (Optional but Recommended)

- **Why**: Conda simplifies environment management.

- **Download**: Install Miniconda from conda.io.

- **Verify**:

  ```
  conda --version
  ```

### 3. Install FluidSynth

- **Why**: Converts MIDI files to WAV audio (used by `midi2audio`).

- **Windows**:

  1. Download FluidSynth from GitHub.

  2. Extract to a directory (e.g., `C:\FluidSynth`).

  3. Add the `bin` directory to your system PATH:

     - Right-click "This PC" > "Properties" > "Advanced system settings" > "Environment Variables".
     - Under "System variables", edit "Path", and add `C:\FluidSynth\bin`.

  4. Verify:

     ```
     fluidsynth --version
     ```

- **Linux**:

  ```
  sudo apt-get install fluidsynth
  ```

- **macOS (Homebrew)**:

  ```
  brew install fluidsynth
  ```

- **Verify**:

  ```
  fluidsynth --version
  ```

### 4. Install FFmpeg

- **Why**: Converts MP3 audio (from OpenAI TTS) to WAV (used by `pydub`).

- **Windows**:

  1. Download FFmpeg from gyan.dev.

  2. Extract to a directory (e.g., `C:\ffmpeg`).

  3. Add the `bin` directory to your system PATH (e.g., `C:\ffmpeg\bin`).

  4. Verify:

     ```
     ffmpeg -version
     ```

- **Linux**:

  ```
  sudo apt-get install ffmpeg
  ```

- **macOS (Homebrew)**:

  ```
  brew install ffmpeg
  ```

- **Verify**:

  ```
  ffmpeg -version
  ```

### 5. Download a SoundFont File

- **Why**: FluidSynth needs a SoundFont to synthesize audio.
- **Download**: Use `FluidR3_GM.sf2` from here or another source.
- **Save**: Place it in a directory (e.g., `E:/soundfonts/FluidR3_GM.sf2`).
- **Note**: Update `soundfont_path` in `config.json` to point to this file.

### 6. Obtain an OpenAI API Key

- **Why**: For TTS in `recitation_generation.py`.
- **Steps**:
  1. Sign up at openai.com.
  2. Go to the API section, generate an API key, and copy it.
  3. Update `openai_api_key` in `config.json`.

## Setup

### 1. Clone or Download the Project

- Clone the repository (if hosted on GitHub):

  ```
  git clone <repository-url>
  cd <repository-directory>
  ```

- Or download and extract the project files.

### 2. Create a Conda Environment (Recommended)

- Create and activate a new environment:

  ```
  conda create -n poem python=3.8
  conda activate poem
  ```

- If not using Conda, use your global Python environment (not recommended).

### 3. Install Python Dependencies

- Install the required packages:

  ```
  pip install -r requirements.txt
  ```

- The `requirements.txt` includes:

  ```
  openai==1.66.3
  pydub==0.25.1
  pretty_midi==0.2.9
  midi2audio==0.1.1
  nltk==3.9.1
  textblob==0.18.0.post0
  pronouncing==0.2.0
  magenta==2.1.4
  note-seq==0.0.3
  tensorflow==2.9.1
  numpy==1.21.6
  ```

### 4. Download NLTK Data

- Run the following to download NLTK data for text processing:

  ```
  python -c "import nltk; nltk.download('punkt'); nltk.download('averaged_perceptron_tagger'); nltk.download('vader_lexicon')"
  ```

### 5. Configure the Project

- Open `config/config.json` and update the following:

  - `openai_api_key`: Your OpenAI API key (e.g., `"sk-..."`).
  - `soundfont_path`: Path to the SoundFont file (e.g., `"E:/soundfonts/FluidR3_GM.sf2"`).
  - `ffmpeg_bin_path`: Path to the FFmpeg `bin` directory (e.g., `"C:/ffmpeg/bin"`).
  - `recitation_volume`: Volume adjustment for recitation in dB (e.g., `1`).
  - `melody_volume`: Volume adjustment for melody in dB (e.g., `-3`).

- Example `config.json`:

  ```json
  {
    "nlp_analysis": {
      "input_file": "data/poems.json"
    },
    "recitation_generation": {
      "openai_api_key": "your-openai-api-key",
      "ffmpeg_bin_path": "C:/ffmpeg/bin"
    },
    "music_synthesis": {
      "soundfont_path": "E:/soundfonts/FluidR3_GM.sf2",
      "ffmpeg_bin_path": "C:/ffmpeg/bin",
      "recitation_volume": 1,
      "melody_volume": -3
    }
  }
  ```

## Usage

### 1. Run the Pipeline

- Activate your environment:

  ```
  conda activate poem
  ```

- Run the main script:

  ```
  python main.py
  ```

### 2. Follow the Prompts

- **Select Poem Input**:

  ```
  Select an option:
  1. Search for a poem in the database
  2. Manually enter a poem
  3. Upload a poem file
  Enter 1, 2, or 3:
  ```

  - **Option 1**: Search by title, author, or keyword.
  - **Option 2**: Enter the poem’s title, author, and lines manually.
  - **Option 3**: Provide the path to a JSON file (e.g., `data/poems.json`).

- **Lyrics Adjustment**:

  ```
  Do you want to adjust the poem's lyrics for recitation? (e.g., normalize to 8 syllables per line)
  Enter 'yes' or 'no':
  ```

  - Enter `yes` to adjust or `no` to skip.

### 3. Pipeline Steps

The pipeline processes the poem in the following steps:

1. **NLP Analysis**: Analyzes sentiment and structure.
2. **Music Mapping**: Maps to musical parameters.
3. **Recitation Generation**: Creates spoken audio.
4. **Melody Generation**: Generates a melody.
5. **Music Synthesis**: Mixes recitation with melody.

### 4. Output Files

- **Intermediate Files**:

  - Recitation: `output/<poem_title>_recitation_<timestamp>.wav`
  - Melody (MIDI): `output/<poem_title>_melody_<timestamp>.mid`

- **Final Output**:

  - Final audio: `output/<poem_title>_final_song_<timestamp>.wav`

- **Example Output**:

  ```
  === Recitation Generation Results ===
  Recitation Length: 156.87 seconds
  Recitation Audio Saved To: output/In_Memory_recitation_20250415_001813.wav
  =====================================
  
  === Melody Generation Results ===
  Number of Notes: 183
  Total Duration: 156.87 seconds
  Melody saved as MIDI file: output/In_Memory_melody_20250415_001813.mid
  =====================================
  
  Temporary MIDI file saved: output/In_Memory_temp_20250415_001813.mid
  Melody converted to WAV: output/In_Memory_melody_20250415_001813.wav
  Final audio saved: output/In_Memory_final_song_20250415_001813.wav
  
  === Music Synthesis Results ===
  Final Audio: output/In_Memory_final_song_20250415_001813.wav
  =====================================
  
  [Success] Pipeline completed successfully!
  ```

## Troubleshooting

- **FluidSynth Not Found**:

  - Ensure FluidSynth is installed and in your PATH.
  - Verify `soundfont_path` in `config.json`.

- **FFmpeg Not Found**:

  - Ensure FFmpeg is installed and in your PATH.
  - Check `ffmpeg_bin_path` in `config.json`.

- **OpenAI API Errors**:

  - Verify `openai_api_key` in `config.json`.
  - Check OpenAI API access and rate limits.

- **File Path Errors**:

  - Use forward slashes (`/`) or double backslashes (`\\`) in `config.json`.
  - Avoid special characters in poem titles.

## Future Improvements

- Organize output files into subdirectories (e.g., `output/<poem_title>_<timestamp>/`).
- Add a user-friendly CLI (e.g., poem preview).
- Optimize melody generation for faster processing.

## License

This project is licensed under the MIT License.

## Contact

For issues or questions, open an issue on GitHub or contact the project maintainer.
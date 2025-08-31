# Gemini Video Behavior Analyzer

This project is a research-grade command-line tool for analyzing human behavior in videos using Google's Gemini multimodal AI models. It extracts frames from a video, sends them to the Gemini API for analysis, and generates detailed reports in Markdown, HTML, and structured JSON formats.

The tool is designed with reproducibility and traceability in mind, incorporating version control, robust logging, and data integrity checks via file hashing.

## Features

- **Flexible Model Selection:** Choose between Gemini 1.5 Flash, 1.5 Pro, 2.5 Flash, and 2.5 Pro models.
- **Customizable Analysis:** Use command-line arguments to specify the analysis focus and output language.
- **Structured Output:** Generates human-readable Markdown/HTML reports and a machine-readable JSON file for programmatic analysis.
- **Robust Logging:** All actions, parameters, and errors are logged to `analysis.log` for a complete audit trail.
- **Data Integrity:** Calculates and logs the SHA256 hash of each video to ensure the input data is traceable.
- **Organized Output:** Creates a structured, timestamped directory for each analysis run to prevent overwriting results.

## Setup

### 1. Clone the Repository
```bash
git clone <repository_url>
cd gemini_video_analyzer
```

### 2. Set up the Environment

This project uses `micromamba` for environment management.

```bash
# Create the conda environment and install dependencies
micromamba create -p ./venv python=3.12 -y
micromamba run -p ./venv pip install -r requirements.txt
```

### 3. Configure API Key

The script requires a Google Gemini API key.

1.  Create a file named `.env` in the root of the project directory.
2.  Add your API key to the file as follows:

```
GEMINI_API_KEY=AIzaSy...your...api...key...
```

## Usage

All commands should be run from the root of the `gemini_video_analyzer` directory. The main script is `analyzer.py`.

### Basic Analysis

This command analyzes a video using the default model (`gemini-1.5-flash`).

```bash
micromamba run -p ./venv python analyzer.py /path/to/your/video.mp4
```

### Analyzing Multiple Videos

You can pass multiple video files at once.

```bash
micromamba run -p ./venv python analyzer.py video1.mp4 "path/to/video 2.mov"
```

### Advanced Options

You can control the analysis with several command-line arguments:

-   `--model` or `-m`: Choose the Gemini model.
-   `--focus` or `-f`: Specify the analysis focus.
-   `--language` or `-l`: Set the output language.
-   `--interval` or `-i`: Set the frame capture interval in seconds.

**Example (High-quality analysis):**
```bash
micromamba run -p ./venv python analyzer.py /path/to/video.mp4 \
    --model gemini-2.5-pro \
    --focus "the woman in the blue jacket" \
    --language "French" \
    --interval 2
```

### Checking Help

To see all available options and their descriptions:
```bash
micromamba run -p ./venv python analyzer.py --help
```

## Output Structure

The generated reports are saved in the `reports/` directory with the following structure:

```
reports/
└── [video_filename_without_extension]/
    └── [model_name]/
        └── [YYYYMMDD]-[run_number]/
            ├── analysis.md      (Markdown Report)
            ├── analysis.html    (HTML Report)
            └── analysis.json    (JSON Data)
```

# Gemini Video Behavior Analyzer

## 1. Overview

This project is a research-grade command-line tool for analyzing human behavior in videos using Google's Gemini multimodal AI models. It can process local video files (`.mp4`, `.webm`, etc.) or directly download and analyze videos from YouTube URLs.

The tool is designed with academic and research rigor in mind, emphasizing reproducibility, traceability, and detailed data output. It generates human-readable reports (Markdown, HTML) and machine-readable structured data (JSON), making it suitable for both qualitative review and quantitative analysis.

---

## 2. Features

-   **Versatile Input:** Accepts local video file paths and YouTube URLs (including full videos and clips) as input.
-   **Multi-Modal AI Analysis:** Utilizes the latest Gemini models to analyze video content.
    -   **Frames Mode:** A traditional approach analyzing visual frames.
    -   **Direct Video Mode:** A powerful mode that analyzes the video file directly, incorporating both **visuals (movement, gestures)** and **audio (tone of voice, speech patterns)**.
-   **Flexible Model Selection:** Allows choice of different Gemini models to balance speed, cost, and analytical depth (`1.5 Flash`, `1.5 Pro`, `2.5 Flash`, `2.5 Pro`).
-   **Customizable Analysis:** Command-line flags allow users to direct the AI's focus and specify the output language of the report.
-   **Rich, Structured Output:** For each analysis, the tool generates:
    -   A detailed Markdown report.
    -   A self-contained, styled HTML report.
    -   A structured JSON file for easy data mining and programmatic analysis.
-   **Research-Grade Integrity:**
    -   **Robust Logging:** A persistent `analysis.log` file records all actions, parameters, timestamps, and errors for a complete audit trail.
    -   **Data Provenance:** Calculates and logs the SHA256 hash of every processed video, ensuring that results can be traced to the exact version of the source data.
    -   **Version Control:** Managed with Git to link results to specific versions of the codebase.

---

## 3. Project Structure

The project is organized into a modular structure to separate concerns and improve maintainability.

```
gemini_video_analyzer/
│
├── .env                # Stores the Gemini API key (must be created manually)
├── .gitignore          # Specifies files and directories to be ignored by Git
├── README.md           # This documentation file
├── analysis.log        # Log file for all analysis runs
├── analyzer.py         # The main entry point and orchestrator script
├── requirements.txt    # Lists Python dependencies for the environment
│
├── reports/            # Root directory for all generated analysis reports
│   └── ...             # (Output is generated here, see section 7)
│
├── src/                # Contains the core application logic
│   ├── gemini_analysis.py    # Handles all interactions with the Gemini API
│   ├── report_generation.py  # Manages the creation of output files and directories
│   └── video_processing.py   # Handles video downloading, conversion, and frame extraction
│
└── temp/               # Temporary storage for downloaded videos (auto-cleaned)
```

---

## 4. File Manifest

| File/Directory | Purpose |
| :--- | :--- |
| **`analyzer.py`** | The main script to execute. It parses command-line arguments and orchestrates the analysis workflow by calling the various modules. |
| **`src/gemini_analysis.py`** | Contains the functions that construct the prompts and make calls to the Gemini API. Includes logic for both `frames` and `video` analysis modes. |
| **`src/video_processing.py`** | Handles all video acquisition and preparation. Downloads from YouTube, converts formats using `ffmpeg`, calculates the SHA256 hash, and extracts frames with `OpenCV`. |
| **`src/report_generation.py`** | Manages the output. Creates the structured directory path for each run and saves the Markdown, HTML, and JSON report files. |
| **`requirements.txt`** | A list of all Python packages required for the project. Used to create the isolated `micromamba` environment. |
| **`.env`** | A user-created file (not in Git) to securely store the `GEMINI_API_KEY`. |
| **`analysis.log`** | A persistent log file. All script operations, from starting a run to errors and completion, are recorded here with timestamps. |
| **`README.md`** | This file. |
| **`reports/`** | The default output directory for all generated analysis. |
| **`temp/`** | A temporary directory for storing downloaded and converted videos before they are processed. It is automatically deleted at the end of a successful run. |

---

## 5. Prerequisites

Before setting up the project, you must have the following software installed on your system (these instructions are for Debian/Ubuntu-based Linux):

1.  **Micromamba:** A fast and lightweight conda package manager.
    ```bash
    # Download and install micromamba
    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)
    # Follow the on-screen instructions to initialize your shell
    ```

2.  **FFmpeg:** A powerful multimedia framework used for video conversion.
    ```bash
    sudo apt update && sudo apt install ffmpeg -y
    ```

---

## 6. Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd gemini_video_analyzer
    ```

2.  **Create the Environment:**
    Use `micromamba` to create an isolated Python environment and install all necessary dependencies from the `requirements.txt` file.
    ```bash
    # Create the environment in a 'venv' subdirectory
    micromamba create -p ./venv python=3.12 -y

    # Install packages using pip within the new environment
    micromamba run -p ./venv pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    The script requires a Google Gemini API key.
    1.  Create a file named `.env` in the root of the project directory: `touch .env`
    2.  Open the file and add your API key in the following format:
        ```
        GEMINI_API_KEY=AIzaSy...your...api...key...
        ```

---

## 7. Usage

All commands must be run from the root of the `gemini_video_analyzer` directory.

### 7.1. Basic Commands

**Analyze a local video file:**
```bash
micromamba run -p ./venv python analyzer.py /path/to/my_video.mp4
```

**Analyze a video from a YouTube URL:**
```bash
micromamba run -p ./venv python analyzer.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 7.2. Command-Line Arguments

You can control the analysis with the following flags:

| Argument | Short | Description |
| :--- | :--- | :--- |
| `video_inputs` | (Positional) | One or more local file paths or YouTube URLs. |
| `--model` | `-m` | **(Default: `gemini-1.5-flash`)** Sets the AI model. Choices: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.5-flash`, `gemini-2.5-pro`. |
| `--analysis-mode`| | **(Default: `frames`)** Sets the analysis method. `frames` for visual-only, `video` for combined visual and audio. |
| `--interval` | `-i` | **(Default: `1`)** Seconds between frame captures. Only used in `frames` mode. |
| `--focus` | `-f` | **(Default: None)** Specifies a subject for the AI to focus on (e.g., "the person in the red shirt"). |
| `--language` | `-l` | **(Default: None)** The output language for the report (e.g., "Spanish", "Japanese"). |

### 7.3. Advanced Examples

**High-quality video/audio analysis on a specific person:**
```bash
micromamba run -p ./venv python analyzer.py "https://youtube.com/clip/..." \
    --model gemini-2.5-pro \
    --analysis-mode video \
    --focus "the detective asking questions"
```

**Frame-based analysis in another language:**
```bash
micromamba run -p ./venv python analyzer.py /path/to/local_video.mp4 \
    --analysis-mode frames \
    --language "German"
```

---

## 8. Output

The script generates a structured, timestamped directory for each analysis run to ensure results are never overwritten.

**Output Directory Structure:**
```
reports/
└── [video_filename_without_extension]/
    └── [model_name]/
        └── [YYYYMMDD]-[run_number]/
            ├── analysis.md      (Markdown Report)
            ├── analysis.html    (HTML Report)
            └── analysis.json    (JSON Data)
```

-   **`analysis.md`**: A human-readable report in Markdown format.
-   **`analysis.html`**: A styled, self-contained HTML version of the report for easy viewing in a browser.
-   **`analysis.json`**: A machine-readable file containing the key analytical findings. This is ideal for downstream data processing, statistical analysis, or integration with other tools.
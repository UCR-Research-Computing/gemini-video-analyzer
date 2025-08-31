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
└── venv/               # Directory for the isolated micromamba environment
```

---

## 4. Prerequisites

Before setting up the project, you must have the following software installed on your system.

1.  **Micromamba:** A fast, native, and lightweight conda package manager. This is required to create a consistent and isolated environment for the project's Python dependencies.
    ```bash
    # Download and install micromamba on Linux or macOS
    "${SHELL}" <(curl -L micro.mamba.pm/install.sh)

    # Follow the on-screen instructions to initialize your shell.
    # You will likely need to restart your terminal or source your shell's config file (e.g., source ~/.bashrc).
    ```

2.  **FFmpeg:** A powerful multimedia framework used by the tool for video conversion.
    ```bash
    # On Debian/Ubuntu-based Linux
    sudo apt update && sudo apt install ffmpeg -y

    # On macOS using Homebrew
    brew install ffmpeg
    ```

---

## 5. Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url>
    cd gemini_video_analyzer
    ```

2.  **Create the Micromamba Environment:**
    Use `micromamba` to create an isolated Python environment in a local `venv` directory and install all necessary dependencies from the `requirements.txt` file.
    ```bash
    # Create the environment using Python 3.12
    micromamba create -p ./venv python=3.12 -y

    # Install all required packages using pip within the new environment
    micromamba run -p ./venv pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    The script requires a Google Gemini API key.
    1.  Create a file named `.env` in the root of the project directory: `touch .env`
    2.  Open the file and add your API key in the following format:
        ```
        GEMINI_API_KEY="AIzaSy...your...api...key..."
        ```

---

## 6. Usage

All commands must be run from the root of the `gemini_video_analyzer` directory. The `micromamba run -p ./venv` prefix is essential as it executes the command within the project's isolated environment.

### 6.1. Basic Commands

**Analyze a local video file:**
```bash
micromamba run -p ./venv python3 analyzer.py /path/to/my_video.mp4
```

**Analyze a video from a YouTube URL:**
```bash
micromamba run -p ./venv python3 analyzer.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 6.2. Command-Line Arguments

You can control the analysis with the following flags:

| Argument | Short | Description |
| :--- | :--- | :--- |
| `video_inputs` | (Positional) | One or more local file paths or YouTube URLs. |
| `--model` | `-m` | **(Default: `gemini-1.5-flash`)** Sets the AI model. Choices: `gemini-1.5-flash`, `gemini-1.5-pro`, `gemini-2.5-flash`, `gemini-2.5-pro`. |
| `--analysis-mode`| | **(Default: `frames`)** Sets the analysis method. `frames` for visual-only, `video` for combined visual and audio. |
| `--interval` | `-i` | **(Default: `1`)** Seconds between frame captures. Only used in `frames` mode. |
| `--focus` | `-f` | **(Default: None)** Specifies a subject for the AI to focus on (e.g., "the person in the red shirt"). |
| `--language` | `-l` | **(Default: None)** The output language for the report (e.g., "Spanish", "Japanese"). |

### 6.3. Advanced Examples

**High-quality video/audio analysis on a specific person:**
```bash
micromamba run -p ./venv python3 analyzer.py "https://youtube.com/clip/..." \
    --model gemini-2.5-pro \
    --analysis-mode video \
    --focus "the detective asking questions"
```

**Frame-based analysis in another language:**
```bash
micromamba run -p ./venv python3 analyzer.py /path/to/local_video.mp4 \
    --analysis-mode frames \
    --language "German"
```

---

## 7. Output

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

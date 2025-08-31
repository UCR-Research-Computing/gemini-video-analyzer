# Gemini Video Analyzer

## Project Overview

This project is a command-line tool for analyzing human behavior in videos using Google's Gemini multimodal AI models. It can process local video files or videos from YouTube URLs. The tool is designed for research purposes, with a focus on reproducibility and detailed data output. It generates reports in Markdown, HTML, and JSON formats.

The main technologies used are Python, the Google Gemini API, `opencv-python` for frame extraction, `yt-dlp` and `pytubefix` for downloading YouTube videos, and `ffmpeg` for video conversion.

The project is structured into a main script `analyzer.py` that orchestrates the analysis, and a `src` directory containing modules for video processing, Gemini analysis, and report generation.

## Building and Running

### Prerequisites

- Micromamba
- FFmpeg

### Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd gemini_video_analyzer
    ```

2.  **Create the environment:**
    ```bash
    micromamba create -p ./venv python=3.12 -y
    micromamba run -p ./venv pip install -r requirements.txt
    ```

3.  **Configure API Key:**
    Create a `.env` file in the project root and add your Gemini API key:
    ```
    GEMINI_API_KEY=your_api_key
    ```

### Running the analyzer

**Analyze a local video file:**
```bash
micromamba run -p ./venv python analyzer.py /path/to/my_video.mp4
```

**Analyze a video from a YouTube URL:**
```bash
micromamba run -p ./venv python analyzer.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### Command-Line Arguments

-   `video_inputs`: (Positional) One or more local file paths or YouTube URLs.
-   `--model` or `-m`: Sets the AI model (default: `gemini-1.5-flash`).
-   `--analysis-mode`: Sets the analysis method (`frames` or `video`, default: `frames`).
-   `--interval` or `-i`: Seconds between frame captures (default: `1`).
-   `--focus` or `-f`: Specifies a subject for the AI to focus on.
-   `--language` or `-l`: The output language for the report.

## Development Conventions

-   **Logging:** The project uses the `logging` module to log all actions, parameters, timestamps, and errors to `analysis.log` and the console.
-   **Modularity:** The code is organized into modules with specific responsibilities (video processing, AI analysis, report generation).
-   **Error Handling:** The code includes error handling for file operations, API calls, and external processes.
-   **Data Integrity:** The SHA256 hash of every processed video is calculated and logged to ensure traceability.
-   **Dependency Management:** Project dependencies are managed with `pip` and a `requirements.txt` file.
-   **Environment Management:** The project uses `micromamba` to create an isolated Python environment.

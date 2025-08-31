import os
import sys
import argparse
import logging
import shutil
from src.video_processing import (
    extract_frames, 
    get_video_hash, 
    is_youtube_url,
    download_youtube_video,
    convert_to_mp4
)
from src.gemini_analysis import analyze_frames_with_gemini, analyze_video_with_gemini
from src.report_generation import create_output_directory, save_reports

def setup_logging():
    """Configures logging to file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("analysis.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )

def main():
    """Main function to orchestrate the video analysis process."""
    setup_logging()
    
    parser = argparse.ArgumentParser(
        description="A research-grade tool to analyze human behavior in videos using Gemini AI.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("video_inputs", nargs='+', help="Local paths or YouTube URLs of the videos to analyze.")
    
    parser.add_argument(
        "-m", "--model", 
        choices=['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-2.5-flash', 'gemini-2.5-pro'],
        default='gemini-1.5-flash',
        help='''The Gemini model to use for analysis.
- gemini-1.5-flash: (Default) Fast and cost-effective.
- gemini-1.5-pro:   Higher quality, more detailed analysis.
- gemini-2.5-flash: The next-generation fast and efficient model.
- gemini-2.5-pro:   The state-of-the-art model for highest quality analysis.'''
    )
    
    parser.add_argument(
        "--analysis-mode",
        choices=['frames', 'video'],
        default='frames',
        help='''The method for analysis.
- frames: (Default) Extracts frames as images and analyzes them visually.
- video:  Uploads the full video for combined visual and audio analysis.'''
    )
    
    parser.add_argument("-i", "--interval", type=int, default=1, help="Interval in seconds between frame captures (only used in 'frames' mode).")
    parser.add_argument("-f", "--focus", type=str, default=None, help="Specify the focus of the analysis (e.g., 'the person on the left').")
    parser.add_argument("-l", "--language", type=str, default=None, help="The output language for the analysis report (e.g., 'Spanish').")

    args = parser.parse_args()

    logging.info("--- Starting new analysis run ---")
    logging.info(f"Command line arguments: {vars(args)}")

    for video_input in args.video_inputs:
        logging.info(f"--- Processing input: {video_input} ---")
        
        processed_video_path = None
        original_filename = ""

        if os.path.exists(video_input):
            logging.info("Input is a local file.")
            processed_video_path = video_input
            original_filename = os.path.basename(video_input)
        elif is_youtube_url(video_input):
            logging.info("Input is a YouTube URL. Starting download...")
            downloaded_path = download_youtube_video(video_input)
            if downloaded_path:
                original_filename = os.path.basename(downloaded_path)
                processed_video_path = convert_to_mp4(downloaded_path)
        else:
            logging.error(f"Input '{video_input}' is not a valid file path or YouTube URL. Skipping.")
            continue

        if not processed_video_path:
            logging.error(f"Failed to acquire or process video from '{video_input}'. Skipping.")
            continue

        video_hash = get_video_hash(processed_video_path)
        if not video_hash:
            logging.warning(f"Could not hash video {original_filename}. Skipping.")
            continue
        logging.info(f"SHA256 Hash for {original_filename}: {video_hash}")

        analysis_md, analysis_json = None, None
        if args.analysis_mode == 'frames':
            frames = extract_frames(processed_video_path, args.interval)
            if frames:
                analysis_md, analysis_json = analyze_frames_with_gemini(frames, args.model, args.focus, args.language)
            else:
                logging.warning(f"Frame extraction failed for {original_filename}. Skipping.")
                continue
        elif args.analysis_mode == 'video':
            analysis_md, analysis_json = analyze_video_with_gemini(processed_video_path, args.model, args.focus, args.language)

        if not analysis_md:
            logging.warning(f"Gemini analysis failed for {original_filename}. Skipping report generation.")
            continue

        output_dir = create_output_directory("reports", original_filename, args.model)
        if not output_dir:
            logging.error(f"Could not create output directory for {original_filename}. Skipping report generation.")
            continue
        
        logging.info(f"Saving reports to: {output_dir}")
        save_reports(output_dir, analysis_md, analysis_json, original_filename)

    if os.path.exists("temp"):
        shutil.rmtree("temp")
        logging.info("Cleaned up temporary directory.")

    logging.info("--- Analysis run finished ---")

if __name__ == "__main__":
    main()
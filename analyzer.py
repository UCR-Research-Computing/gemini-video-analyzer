import os
import sys
import argparse
import logging
from src.video_processing import extract_frames, get_video_hash
from src.gemini_analysis import analyze_frames_with_gemini
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
    parser.add_argument("video_files", nargs='+', help="Paths to the video files to analyze.")
    
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
    
    parser.add_argument("-i", "--interval", type=int, default=1, help="Interval in seconds between frame captures. Default is 1 second.")
    parser.add_argument("-f", "--focus", type=str, default=None, help="Specify the focus of the analysis (e.g., 'the person on the left').")
    parser.add_argument("-l", "--language", type=str, default=None, help="The output language for the analysis report (e.g., 'Spanish').")

    args = parser.parse_args()

    logging.info("--- Starting new analysis run ---")
    logging.info(f"Command line arguments: {vars(args)}")

    for video_file in args.video_files:
        logging.info(f"--- Processing video: {video_file} ---")
        
        # 1. Get video hash for data integrity
        video_hash = get_video_hash(video_file)
        if not video_hash:
            logging.warning(f"Could not hash video {video_file}. Skipping.")
            continue
        logging.info(f"SHA256 Hash for {os.path.basename(video_file)}: {video_hash}")

        # 2. Extract frames
        frames = extract_frames(video_file, args.interval)
        if not frames:
            logging.warning(f"Frame extraction failed for {video_file}. Skipping.")
            continue

        # 3. Analyze with Gemini
        analysis_md, analysis_json = analyze_frames_with_gemini(frames, args.model, args.focus, args.language)
        if not analysis_md:
            logging.warning(f"Gemini analysis failed for {video_file}. Skipping report generation.")
            continue

        # 4. Create output directory
        output_dir = create_output_directory("reports", os.path.basename(video_file), args.model)
        if not output_dir:
            logging.error(f"Could not create output directory for {video_file}. Skipping report generation.")
            continue
        
        logging.info(f"Saving reports to: {output_dir}")

        # 5. Save all reports
        save_reports(output_dir, analysis_md, analysis_json, os.path.basename(video_file))

    logging.info("--- Analysis run finished ---")

if __name__ == "__main__":
    main()
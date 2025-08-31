import os
import cv2
from tqdm import tqdm
import hashlib
import logging
import re
import subprocess

TEMP_DIR = "temp"

def is_youtube_url(url):
    """Checks if the given string is a valid YouTube URL."""
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    return re.match(youtube_regex, url)

def download_youtube_video(url):
    """
    Downloads a video from a YouTube URL using yt-dlp, falling back to pytubefix.
    Returns the path to the downloaded file.
    """
    if not os.path.exists(TEMP_DIR):
        os.makedirs(TEMP_DIR)

    logging.info(f"Attempting to download video from URL: {url}")
    
    # Define output template for yt-dlp to control filename
    output_template = os.path.join(TEMP_DIR, '%(title)s.%(ext)s')

    # Try with yt-dlp first
    try:
        logging.info("Using yt-dlp for download...")
        # We need to capture the output to find the filename
        result = subprocess.run(
            ['/home/chuck/bin/yt-dlp', '--print', 'filename', '-o', output_template, url],
            check=True,
            capture_output=True,
            text=True
        )
        downloaded_file_path = result.stdout.strip()
        
        # Now run the actual download
        subprocess.run(
            ['/home/chuck/bin/yt-dlp', '-o', output_template, url],
            check=True,
            capture_output=True # Suppress verbose output in main log
        )

        if os.path.exists(downloaded_file_path):
            logging.info(f"Successfully downloaded with yt-dlp: {downloaded_file_path}")
            return downloaded_file_path
        else:
            raise FileNotFoundError("yt-dlp reported success but file not found.")

    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.warning(f"yt-dlp failed: {e}. Falling back to pytubefix.")
        
        # Fallback to pytubefix
        try:
            logging.info("Using pytubefix for download...")
            # pytubefix downloads to the current directory, so we run it from inside temp
            subprocess.run(
                ['/home/chuck/bin/pytubefix', url],
                check=True,
                cwd=TEMP_DIR,
                capture_output=True # Suppress verbose output
            )
            # This is a bit of a guess, as pytubefix doesn't tell us the filename.
            # We'll have to find the newest file in the temp dir.
            files = [os.path.join(TEMP_DIR, f) for f in os.listdir(TEMP_DIR)]
            if not files:
                logging.error("pytubefix ran but no file was created.")
                return None
            latest_file = max(files, key=os.path.getctime)
            logging.info(f"Successfully downloaded with pytubefix: {latest_file}")
            return latest_file

        except (subprocess.CalledProcessError, FileNotFoundError) as e_pytube:
            logging.error(f"pytubefix also failed: {e_pytube}")
            return None

def convert_to_mp4(video_path):
    """
    Converts a video file to a compatible MP4 format using ffmpeg.
    Deletes the original file upon successful conversion.
    """
    if not video_path or not os.path.exists(video_path):
        logging.error(f"Cannot convert video: file not found at {video_path}")
        return None

    if video_path.endswith('.mp4'):
        logging.info("Video is already in MP4 format. No conversion needed.")
        return video_path

    output_path = os.path.splitext(video_path)[0] + ".mp4"
    logging.info(f"Converting {os.path.basename(video_path)} to MP4 format...")

    try:
        subprocess.run(
            ['ffmpeg', '-i', video_path, '-c:v', 'libx264', '-c:a', 'aac', '-y', output_path],
            check=True,
            capture_output=True # Suppress verbose ffmpeg output
        )
        logging.info(f"Successfully converted video to {output_path}")
        
        # Clean up the original file
        try:
            os.remove(video_path)
            logging.info(f"Removed original file: {video_path}")
        except OSError as e:
            logging.warning(f"Failed to remove original file {video_path}: {e}")
            
        return output_path
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        logging.error(f"ffmpeg conversion failed: {e}")
        if isinstance(e, subprocess.CalledProcessError):
            logging.error(f"ffmpeg stderr: {e.stderr.decode()}")
        return None

def get_video_hash(video_path):
    """Calculates the SHA256 hash of a video file for data integrity."""
    sha256_hash = hashlib.sha256()
    try:
        with open(video_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except FileNotFoundError:
        logging.error(f"Could not find file {video_path} to calculate hash.")
        return None
    except Exception as e:
        logging.error(f"Error calculating hash for {video_path}: {e}")
        return None

def extract_frames(video_path, interval_sec=1):
    """Extracts frames from a video file at a given interval."""
    if not os.path.exists(video_path):
        logging.error(f"Video file not found at {video_path}")
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        logging.error(f"Could not open video file {video_path}")
        return None

    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        logging.warning(f"Could not determine FPS for {video_path}. Using a default of 30.")
        fps = 30
        
    frame_interval = int(fps * interval_sec)
    frames = []
    frame_count = 0
    
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    logging.info(f"Extracting frames from {os.path.basename(video_path)}...")
    with tqdm(total=total_frames, unit='frames', leave=False) as pbar:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            if frame_count % frame_interval == 0:
                _, buffer = cv2.imencode('.jpg', frame)
                frames.append(buffer.tobytes())
            
            frame_count += 1
            pbar.update(1)

    cap.release()
    logging.info(f"Extracted {len(frames)} frames from {os.path.basename(video_path)}.")
    return frames
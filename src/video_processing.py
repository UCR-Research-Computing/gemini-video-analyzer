import os
import cv2
from tqdm import tqdm
import hashlib
import logging

def get_video_hash(video_path):
    """Calculates the SHA256 hash of a video file for data integrity."""
    sha256_hash = hashlib.sha256()
    try:
        with open(video_path, "rb") as f:
            # Read and update hash in chunks of 4K
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

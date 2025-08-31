import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging
import re
import json
from tqdm import tqdm

def parse_json_from_markdown(markdown_text):
    """Extracts and parses a JSON object from a Markdown code block."""
    try:
        match = re.search(r"```json\n(.*?)\n```", markdown_text, re.DOTALL)
        if match:
            json_string = match.group(1)
            return json.loads(json_string)
        else:
            logging.warning("No JSON block found in the model's response.")
            return None
    except json.JSONDecodeError as e:
        logging.error(f"Error decoding JSON from response: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during JSON parsing: {e}")
    return None

def analyze_frames_with_gemini(frames, model_name, focus, language):
    """
    Analyzes frames using a Gemini model and returns the full markdown
    and a parsed JSON object.
    """
    # (The existing frame analysis code remains unchanged)
    if not frames:
        logging.warning("No frames were provided for analysis.")
        return None, None

    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY not found. Please set it in a .env file.")
        return None, None
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(f'models/{model_name}')
    logging.info(f"Analyzing frames with {model_name}...")

    image_parts = [{"mime_type": "image/jpeg", "data": frame} for frame in frames]

    prompt_parts = [
        "You are an expert in behavioral analysis and non-verbal communication.",
        "Analyze the provided sequence of images, which are frames from a video."
    ]
    if focus:
        prompt_parts.append(f"Your analysis should focus on: {focus}.")
    else:
        prompt_parts.append("Focus on the primary individual visible in the frames.")

    prompt_parts.append("Based on their facial expressions, body language, posture, and any discernible gestures, please provide a comprehensive report in Markdown format.")
    
    if language:
        prompt_parts.append(f"The report must be written in {language}.")

    prompt_parts.append("""
The report should include the following sections:

## Overall Emotional State
- A summary of the person's dominant emotional state throughout the clip.

## Sentiment Analysis
- Classify the overall sentiment as Positive, Negative, or Neutral, and provide a brief justification.

## Detailed Observations
- **Facial Expressions:** Describe specific expressions observed (e.g., furrowed brow, smile, tightened lips, eye contact/avoidance).
- **Body Language:** Describe posture (e.g., open, closed, slumped, upright), hand gestures, and any other significant body movements.
- **Potential Inferred Feelings:** Based on your observations, infer potential feelings such as nervousness, confidence, happiness, fear, sadness, or contemplation. Provide specific visual evidence for each inference.

## Confidence Level
- Assess the person's apparent confidence level on a scale of Low, Medium, or High, explaining your reasoning.

## Summary
- Conclude with a brief summary of your findings.

Finally, after the summary, provide a JSON object containing the key findings. The JSON object should be enclosed in a Markdown code block like this:
```json
{
  "emotional_state": "...",
  "sentiment": {
    "classification": "...",
    "justification": "..."
  },
  "confidence_level": "...",
  "key_observations": [
    {"type": "facial_expression", "detail": "..."},
    {"type": "body_language", "detail": "..."}
  ]
}
```
""")
    
    prompt = "\n".join(prompt_parts)

    try:
        response = model.generate_content([prompt] + image_parts)
        full_markdown = response.text
        json_data = parse_json_from_markdown(full_markdown)
        logging.info("Successfully received and parsed response from Gemini.")
        return full_markdown, json_data
    except Exception as e:
        logging.error(f"An error occurred during the Gemini API call: {e}")
        return None, None

def analyze_video_with_gemini(video_path, model_name, focus, language):
    """
    Analyzes a video file directly using a Gemini model, including audio.
    Returns the full markdown and a parsed JSON object.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        logging.critical("GEMINI_API_KEY not found. Please set it in a .env file.")
        return None, None
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel(f'models/{model_name}')
    logging.info(f"Uploading video file: {video_path}...")
    
    # Upload the video file
    video_file = genai.upload_file(path=video_path)
    logging.info(f"Successfully uploaded {video_file.display_name}.")

    # Wait for the file to be processed
    while video_file.state.name == "PROCESSING":
        print('.', end='', flush=True)
        video_file = genai.get_file(video_file.name)
    print() # Newline after processing dots

    if video_file.state.name == "FAILED":
        logging.error(f"Video processing failed for {video_path}.")
        return None, None

    logging.info(f"Analyzing video and audio with {model_name}...")

    # Dynamically build the prompt for video and audio analysis
    prompt_parts = [
        "You are an expert in behavioral analysis, skilled in interpreting both visual and auditory cues.",
        "Analyze the provided video file, paying attention to both the visual elements and the audio track."
    ]
    if focus:
        prompt_parts.append(f"Your analysis should focus on: {focus}.")
    else:
        prompt_parts.append("Focus on the primary individual visible and audible in the video.")

    prompt_parts.append("Based on their facial expressions, body language, gestures, tone of voice, and speech patterns, please provide a comprehensive report in Markdown format.")
    
    if language:
        prompt_parts.append(f"The report must be written in {language}.")

    prompt_parts.append("""
The report should include the following sections:

## Overall Emotional State
- A summary of the person's dominant emotional state, considering both visual and auditory cues.

## Sentiment Analysis
- Classify the overall sentiment as Positive, Negative, or Neutral, justifying your answer with evidence from both video and audio.

## Detailed Observations
- **Visual Cues:** Describe specific facial expressions, posture, and body movements (e.g., fidgeting, leaning forward, breaking eye contact).
- **Auditory Cues:** Describe the tone of voice (e.g., wavering, confident, monotone), pace of speech, use of filler words, and any notable pauses or hesitations.
- **Potential Inferred Feelings:** Infer potential feelings (e.g., nervousness, confidence, deception, honesty) and support your inferences with specific, timestamped examples from the video if possible.

## Confidence Level
- Assess the person's apparent confidence level on a scale of Low, Medium, or High, explaining your reasoning based on both visual and auditory evidence.

## Summary
- Conclude with a brief, holistic summary of your findings.

Finally, after the summary, provide a JSON object containing the key findings. The JSON object should be enclosed in a Markdown code block like this:
```json
{
  "emotional_state": "...",
  "sentiment": {
    "classification": "...",
    "justification": "..."
  },
  "confidence_level": "...",
  "key_observations": [
    {"type": "visual_cue", "detail": "..."},
    {"type": "auditory_cue", "detail": "..."}
  ]
}
```
""")
    
    prompt = "\n".join(prompt_parts)

    try:
        response = model.generate_content([prompt, video_file])
        full_markdown = response.text
        json_data = parse_json_from_markdown(full_markdown)
        
        # Clean up the uploaded file
        genai.delete_file(video_file.name)
        logging.info(f"Cleaned up uploaded file: {video_file.name}")
        
        logging.info("Successfully received and parsed response from Gemini.")
        return full_markdown, json_data
    except Exception as e:
        logging.error(f"An error occurred during the Gemini API call: {e}")
        return None, None
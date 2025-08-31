import os
import datetime
import json
import markdown2
import logging

def create_output_directory(base_reports_dir, video_filename, model_name):
    """Creates a unique, structured directory for the analysis run."""
    base_video_name = os.path.splitext(video_filename)[0]
    today_str = datetime.date.today().strftime("%Y%m%d")
    run_number = 1
    
    video_model_dir = os.path.join(base_reports_dir, base_video_name, model_name)
    
    while True:
        output_dir = os.path.join(video_model_dir, f"{today_str}-{run_number:03d}")
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                return output_dir
            except OSError as e:
                logging.error(f"Failed to create output directory {output_dir}: {e}")
                return None
        run_number += 1

def save_reports(output_dir, markdown_content, json_content, video_filename):
    """Saves the markdown, html, and json reports to the specified directory."""
    if not markdown_content:
        logging.error("No markdown content provided to save.")
        return

    base_video_name = os.path.splitext(video_filename)[0]
    
    # Save Markdown
    md_path = os.path.join(output_dir, "analysis.md")
    try:
        with open(md_path, "w") as f:
            f.write(markdown_content)
        logging.info(f"Markdown report saved to: {md_path}")
    except IOError as e:
        logging.error(f"Failed to save Markdown report to {md_path}: {e}")

    # Save JSON
    if json_content:
        json_path = os.path.join(output_dir, "analysis.json")
        try:
            with open(json_path, "w") as f:
                json.dump(json_content, f, indent=4)
            logging.info(f"JSON report saved to: {json_path}")
        except IOError as e:
            logging.error(f"Failed to save JSON report to {json_path}: {e}")
        except TypeError as e:
            logging.error(f"Failed to serialize JSON data: {e}")

    # Save HTML
    html_path = os.path.join(output_dir, "analysis.html")
    try:
        html_content = markdown2.markdown(markdown_content, extras=["tables", "fenced-code-blocks", "styling"])
        html_template = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Gemini Video Analysis: {base_video_name}</title>
            <style>
                body {{ font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: auto; }}
                h1, h2, h3 {{ color: #333; }}
                code {{ background-color: #f4f4f4; padding: 2px 4px; border-radius: 4px; }}
                pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 4px; }}
            </style>
        </head>
        <body>
            <h1>Analysis for: {video_filename}</h1>
            {html_content}
        </body>
        </html>
        """
        with open(html_path, "w") as f:
            f.write(html_template)
        logging.info(f"HTML report saved to: {html_path}")
    except IOError as e:
        logging.error(f"Failed to save HTML report to {html_path}: {e}")
    except Exception as e:
        logging.error(f"An unexpected error occurred during HTML generation: {e}")

import os
import re
import asyncio
import logging
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

logger = logging.getLogger(__name__)

async def run_adversal_pipeline_async(source: str, output_dir: str, timeout_seconds: int = 360) -> str:
    """
    Submits a video to Adversal MCP over stdio interface and polls check_video_status
    until COMPLETED or timeout.
    Returns the path to the output notes.md file.
    """
    os.makedirs(output_dir, exist_ok=True)
    notes_filepath = os.path.join(output_dir, "notes.md")

    server_params = StdioServerParameters(
        command="uvx",
        args=["adversal-cli"],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            logger.info(f"Initialized Adversal MCP session for source: {source}")

            # Prepare process_video arguments
            args = {
                "output_path": output_dir,
                "file_name": "notes.md",
                "type": "generic",
                "images": "minimal"
            }
            if source.startswith("http://") or source.startswith("https://"):
                logger.info("Pre-downloading YouTube video using VidChat robust handler...")
                from ..utils.audio_processor import download_youtube_video
                local_video = download_youtube_video(source)
                args["video_path"] = os.path.abspath(local_video)
            else:
                args["video_path"] = os.path.abspath(source)

            # Call process_video tool
            process_res = await session.call_tool("process_video", arguments=args)
            res_text = ""
            for content in process_res.content:
                if hasattr(content, "text"):
                    res_text += content.text

            logger.info(f"Adversal process_video response: {res_text}")

            # Extract request_id from response
            match = re.search(r"request_id:\s*([a-f0-9\-]+)", res_text, re.IGNORECASE)
            if not match:
                raise RuntimeError(f"Failed to obtain request_id from Adversal response: {res_text}")
            
            request_id = match.group(1).strip()
            logger.info(f"Adversal job submitted with request_id: {request_id}")

            # Poll check_video_status
            start_time = asyncio.get_event_loop().time()
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                if elapsed > timeout_seconds:
                    raise TimeoutError(f"Adversal AI Cloud pipeline timed out after {timeout_seconds} seconds")

                await asyncio.sleep(15)

                status_res = await session.call_tool("check_video_status", arguments={"request_id": request_id})
                status_text = ""
                for content in status_res.content:
                    if hasattr(content, "text"):
                        status_text += content.text

                logger.info(f"Adversal status check ({int(elapsed)}s): {status_text.splitlines()[0] if status_text else ''}")

                if "COMPLETED" in status_text:
                    logger.info(f"Adversal job {request_id} COMPLETED successfully.")
                    break
                elif "FAILED" in status_text:
                    raise RuntimeError(f"Adversal AI Cloud processing failed: {status_text}")

    if not os.path.exists(notes_filepath):
        raise FileNotFoundError(f"Expected output file not found at {notes_filepath}")

    return notes_filepath

def run_adversal_pipeline(source: str, output_dir: str, timeout_seconds: int = 360) -> str:
    """Synchronous wrapper for run_adversal_pipeline_async"""
    return asyncio.run(run_adversal_pipeline_async(source, output_dir, timeout_seconds))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

def parse_adversal_notes(output_dir: str) -> dict:
    """
    Parses generated notes.md and associated images from output_dir into structured dictionary.
    Rewrites relative image markdown tags to point to static backend server URLs.
    """
    notes_path = os.path.join(output_dir, "notes.md")
    if not os.path.exists(notes_path):
        raise FileNotFoundError(f"Notes file does not exist: {notes_path}")

    with open(notes_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Calculate static URL base relative to BASE_DIR/data
    data_dir = os.path.join(BASE_DIR, "data")
    rel_path = os.path.relpath(output_dir, data_dir).replace("\\", "/")
    static_url_prefix = f"http://localhost:8000/static/{rel_path}"

    # Rewrite ![alt](image_path) tags to http://localhost:8000/static/...
    def replace_img(match):
        alt = match.group(1)
        src = match.group(2).replace("\\", "/")
        if src.startswith("http://") or src.startswith("https://"):
            return f"![{alt}]({src})"
        
        filename = os.path.basename(src)
        if os.path.exists(os.path.join(output_dir, "img", filename)):
            return f"![{alt}]({static_url_prefix}/img/{filename})"
        elif os.path.exists(os.path.join(output_dir, filename)):
            return f"![{alt}]({static_url_prefix}/{filename})"
        else:
            return f"![{alt}]({static_url_prefix}/{src})"

    content = re.sub(r"!\[(.*?)\]\((.*?)\)", replace_img, content)

    # Discover images inside output_dir or output_dir/img
    images = []
    for root, _, files in os.walk(output_dir):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                images.append(os.path.join(root, file))

    # Extract title
    title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Adversal AI Cloud Video Analysis"

    # Separate headers / sections
    sections = re.split(r"^##\s+", content, flags=re.MULTILINE)

    summary = ""
    action_items = ""
    key_decisions = ""
    open_questions = ""

    if len(sections) > 0:
        summary = sections[0].strip()

    for sec in sections[1:]:
        lines = sec.strip().splitlines()
        sec_title = lines[0].lower() if lines else ""
        sec_body = "\n".join(lines[1:]).strip()

        if "action" in sec_title or "takeaway" in sec_title:
            action_items += f"### {lines[0]}\n{sec_body}\n\n"
        elif "decision" in sec_title or "conclusion" in sec_title:
            key_decisions += f"### {lines[0]}\n{sec_body}\n\n"
        elif "question" in sec_title or "context" in sec_title or "theme" in sec_title:
            open_questions += f"### {lines[0]}\n{sec_body}\n\n"
        else:
            summary += f"\n\n### {lines[0]}\n{sec_body}"

    if not action_items.strip():
        takeaway_bullets = [line for line in content.splitlines() if line.strip().startswith(('- ', '* ', '1.', '2.', '3.', '4.', '5.'))]
        if takeaway_bullets:
            action_items = "### Practical Takeaways & Highlights\n" + "\n".join(takeaway_bullets[:8])
        else:
            action_items = "### Key Takeaways\n- Synthesized technical concepts and practical insights from the video analysis.\n- Key core principles established in the media content."

    if not key_decisions.strip():
        key_decisions = "### Core Principles & Conclusions\n- Central principles and technical conclusions established in the video."

    if not open_questions.strip():
        open_questions = "### Analytical Themes & Follow-ups\n- Primary themes and analytical framing for further study."

    return {
        "title": title,
        "transcript": content,
        "summary": summary.strip(),
        "action_items": action_items.strip(),
        "key_decisions": key_decisions.strip(),
        "open_questions": open_questions.strip(),
        "images": images
    }

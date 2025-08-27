import streamlit as st
import os
import tempfile
import subprocess
import re
from apify_client import ApifyClient
from openai import OpenAI

import streamlit.components.v1 as components
import markdown

# Load environment variables from .env file if it exists (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, will use system environment variables

# Page configuration
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for minimalistic design
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 600;
        text-align: center;
        color: #333;
        margin-bottom: 0.5rem;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }
    .sub-header {
        font-size: 1.1rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    .success-message {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        color: #495057;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        line-height: 1.6;
        font-size: 1rem;
        font-family: -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .success-message table {
        border-collapse: collapse;
        width: 100%;
        margin: 1rem 0;
        border: 1px solid #e9ecef;
    }

    .success-message th,
    .success-message td {
        border: 1px solid #e9ecef;
        padding: 0.75rem;
        text-align: left;
        vertical-align: top;
    }

    .success-message th {
        background-color: #f1f3f5;
        font-weight: 600;
    }

    .success-message tr:nth-child(even) {
        background-color: #f8f9fa;
    }

    .success-message code {
        background-color: #e9ecef;
        padding: 0.2rem 0.4rem;
        border-radius: 4px;
        font-family: monospace;
    }

    .success-message pre {
        background-color: #e9ecef;
        padding: 1rem;
        border-radius: 4px;
        overflow-x: auto;
    }

    .error-message {
        background-color: #fff5f5;
        border: 1px solid #fed7d7;
        color: #c53030;
        padding: 1rem;
        border-radius: 6px;
        margin: 1rem 0;
        font-size: 0.95rem;
    }

    /* Clean up Streamlit default styles */
    .stProgress > div > div > div {
        background-color: #e9ecef;
    }
    .stProgress > div > div > div > div {
        background-color: #007bff;
    }

    /* Button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
    }

    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 6px;
    }

    /* Mobile optimizations */
    @media (max-width: 768px) {
        .main-header {
            font-size: 1.8rem;
        }
        .sub-header {
            font-size: 0.9rem;
        }
        .stTextInput > div > div > input {
            font-size: 16px; /* Prevents zoom on iOS */
        }
        .stButton > button {
            font-size: 1rem;
            padding: 0.75rem 2rem;
        }
    }

    /* Form styling for better mobile keyboard handling */
    .stForm {
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

class YouTubeSummarizer:
    def __init__(self):
        pass

    def extract_transcript_apify(self, youtube_url):
        """Extract transcript, video title, and channel name from YouTube video using Apify"""
        try:
            # Initialize the ApifyClient with API token from environment variable
            api_token = os.getenv("APIFY_API_TOKEN")
            client = ApifyClient(api_token)

            # Prepare the Actor input
            run_input = {
                "startUrls": [youtube_url],
                "language": "Default",
                "includeTimestamps": "No",
            }

            # Run the Actor and wait for it to finish
            run = client.actor("dB9f4B02ocpTICIEY").call(run_input=run_input)

            # Check if the run was successful
            if not run or not run.get("defaultDatasetId"):
                st.error("❌ Apify actor failed to process the video.")
                return None, None, None

            # Fetch and process results
            transcript_text = ""
            video_title = None
            channel_name = None

            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                # Extract video title if available
                if 'videoTitle' in item and item['videoTitle']:
                    video_title = item['videoTitle']

                # Extract channel name if available
                if 'channelName' in item and item['channelName']:
                    channel_name = item['channelName']

                # Extract transcript content
                if 'transcript' in item and item['transcript']:
                    transcript_text += item['transcript'] + "\n"
                elif 'text' in item and item['text']:
                    transcript_text += item['text'] + "\n"

            if not transcript_text.strip():
                st.error("❌ No transcript found in the video.")
                return None, video_title or "YouTube Video", channel_name or "Unknown Channel"

            return transcript_text, video_title or "YouTube Video", channel_name or "Unknown Channel"


        except Exception as e:
            st.error(f"❌ Error extracting transcript: {str(e)}")
            return None, "YouTube Video", "Unknown Channel"

    def get_video_title_from_url(self, youtube_url):
        """Extract video title from YouTube URL (simplified approach)"""
        try:
            # For now, return a generic title - could be enhanced later
            return "YouTube Video"
        except:
            return "YouTube Video"

    def summarize_text(self, text, video_title=None, channel_name=None, custom_prompt=None):
        """Summarize text using OpenRouter API"""
        try:
            # Get API key from environment
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                st.error("❌ OpenRouter API key not found. Please set the OPENROUTER_API_KEY environment variable.")
                return None

            # Initialize OpenRouter client
            client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=api_key,
            )

            # Prepare the prompt
            if custom_prompt and custom_prompt.strip():
                # Use custom prompt with transcript context
                if video_title and channel_name:
                    prompt = f"""You are analyzing a YouTube video from the channel "{channel_name}" titled: "{video_title}"

Transcript:
{text}

User Question: {custom_prompt.strip()}"""
                elif video_title:
                    prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Transcript:
{text}

User Question: {custom_prompt.strip()}"""
                else:
                    prompt = f"""Transcript:
{text}

User Question: {custom_prompt.strip()}"""
            else:
                # Use default summarization prompts
                if video_title and channel_name:
                    prompt = f"""You are analyzing a YouTube video from the channel "{channel_name}" titled: "{video_title}"

Please provide a concise summary of the following transcript:

{text}

Create a clear summary that captures the main points and key information."""
                elif video_title:
                    prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Please provide a concise summary of the following transcript:

{text}

Create a clear summary that captures the main points and key information."""
                else:
                    prompt = f"""Please provide a concise summary of the following transcript:

{text}

Create a clear summary that captures the main points and key information."""

            if custom_prompt and custom_prompt.strip():
                spinner_text = "Answering your question..."
            else:
                spinner_text = "Generating summary..."

            with st.spinner(spinner_text):
                completion = client.chat.completions.create(
                    model="deepseek/deepseek-r1-0528:free",
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )

                if not completion or not completion.choices:
                    st.error("❌ The AI model did not return a valid response. This could be due to high demand or an invalid request. Please try again later.")
                    return None

                summary = completion.choices[0].message.content.strip()
                return summary if summary else "Summary could not be generated."

        except Exception as e:
            st.error(f"❌ Error generating summary: {str(e)}")
            return None



    def parse_transcript_file(self, transcript_file_path):
        """Parse transcript file and extract clean text"""
        try:
            with open(transcript_file_path, 'r', encoding='utf-8') as file:
                content = file.read()

            # Clean up the transcript text
            transcript = re.sub(r'\s+', ' ', content).strip()

            return transcript if transcript else None

        except Exception as e:
            st.error(f"❌ Error parsing transcript file: {str(e)}")
            return None

    def extract_transcript_and_title(self, youtube_url):
        """Extract transcript from YouTube video using Apify and get video title and channel"""
        try:
            # Extract transcript, title, and channel using Apify
            result = self.extract_transcript_apify(youtube_url)
            if not result or not result[0]:
                video_title = result[1] if result and len(result) > 1 else "YouTube Video"
                channel_name = result[2] if result and len(result) > 2 else "Unknown Channel"
                return None, video_title, channel_name

            transcript_text, video_title, channel_name = result

            # Clean up the transcript text (remove extra whitespace)
            transcript = re.sub(r'\s+', ' ', transcript_text).strip()

            if not transcript:
                return None, video_title, channel_name

            return transcript, video_title, channel_name

        except Exception as e:
            st.error(f"❌ Error processing video: {str(e)}")
            return None, "YouTube Video", "Unknown Channel"

def main():
    st.markdown('<div class="main-header">YouTube Summarizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-powered video summaries</div>', unsafe_allow_html=True)

    # Initialize the summarizer
    summarizer = YouTubeSummarizer()

    # Input section with form for better UX
    st.markdown("### YouTube URL")

    # Create a form to handle Enter key and button clicks
    with st.form("url_form"):
        url = st.text_input(
            "YouTube URL",
            placeholder="Paste your YouTube video link here...",
            label_visibility="hidden"
        )

        # Optional custom question input (inside form for Enter key support)
        with st.expander("Ask a question (Optional)", expanded=False):
            custom_prompt = st.text_input(
                "",
                placeholder="e.g., What are the main benefits?",
                label_visibility="collapsed"
            )

        # Submit button - always enabled when form is submitted
        submitted = st.form_submit_button("Summarize", type="primary")

    # Process when form is submitted (either by button click or Enter key)
    if submitted and url:
        # Validate URL
        if "youtube.com" not in url and "youtu.be" not in url:
            st.error("⚠️ Please enter a valid YouTube URL")
            return

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Step 1: Download subtitles and extract transcript
            status_text.text("Extracting transcript...")
            progress_bar.progress(25)

            result = summarizer.extract_transcript_and_title(url)

            if not result or not result[0]:
                return

            transcript, video_title, channel_name = result

            progress_bar.progress(60)

            # Display transcript (secondary)
            with st.expander("View full transcript"):
                st.text_area("Full transcript", transcript, height=200, disabled=True, label_visibility="hidden")

            # Step 2: Generate response
            if custom_prompt and custom_prompt.strip():
                status_text.text("Answering your question...")
            else:
                status_text.text("Creating summary...")
            summary = summarizer.summarize_text(transcript, video_title, channel_name, custom_prompt)

            if not summary:
                return

            summary_html = markdown.markdown(summary, extensions=['tables'])

            progress_bar.progress(100)
            status_text.text("Complete!")

            # Display results - focus on summary or answer
            if custom_prompt and custom_prompt.strip():
                st.markdown("### Answer to Your Question")
            else:
                st.markdown("### Summary")

            html_content = f"""
<div style="position: relative;">
<div class="success-message" id="summary-text" style="padding-right: 40px;">
{summary_html}
</div>
<button style="position: absolute; top: 5px; right: 10px; background: none; border: none; cursor: pointer; opacity: 0.7;" onclick="navigator.clipboard.writeText(document.getElementById(\'summary-text\').textContent)">
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"/>
</svg>
</button>
</div>
            """
            # Improved height estimation: base + lines * line height
            num_lines = summary.count('\n') + 1
            estimated_height = 300 + num_lines * 30
            components.html(html_content, height=estimated_height, scrolling=False)

        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

        finally:
            progress_bar.empty()
            status_text.empty()


if __name__ == "__main__":
    main()

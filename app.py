import streamlit as st
import os
import tempfile
import subprocess
import re
from apify_client import ApifyClient

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
</style>
""", unsafe_allow_html=True)

class YouTubeSummarizer:
    def __init__(self):
        pass

    def extract_transcript_apify(self, youtube_url):
        """Extract transcript, video title, and channel name from YouTube video using Apify"""
        try:
            # Initialize the ApifyClient with API token
            client = ApifyClient("apify_api_rJhfZzud6sk38pBwVXndxtKRN1zqLI0eqE9l")

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

    def summarize_text(self, text, video_title=None, channel_name=None):
        """Summarize text using Qwen Coder CLI"""
        try:
            # Create a temporary file with the transcript
            with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
                temp_file.write(text)
                temp_file_path = temp_file.name

            # Prepare the prompt for Qwen Code with video title and channel context
            if video_title and channel_name:
                prompt = f"""You are analyzing a YouTube video from the channel "{channel_name}" titled: "{video_title}"

Please provide a very concise summary of the following transcript from this video. Based on your knowledge of the channel and content, identify the likely speaker(s) and include this information in your summary:

{text}

Create a clear, comprehensive summary that captures the main points, key information, context from the video title, and identifies the speaker(s) where possible."""
            elif video_title:
                prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Please provide a very concise summary of the following transcript from this video. Based on the content and context, try to identify the likely speaker(s):

{text}

Create a clear, comprehensive summary that captures the main points, key information, context from the video title, and identifies the speaker(s) where possible."""
            else:
                prompt = f"""Please provide a very concise summary of the following transcript. Based on the content, try to identify the likely speaker(s):

{text}

Create a clear, very concise, comprehensive summary that captures the main points and key information, including speaker identification where possible."""

            with st.spinner("Generating summary with Qwen Coder..."):
                # Call Qwen Coder CLI with the prompt
                result = subprocess.run([
                    r'node',
                    r'C:\\Users\\tesla\\AppData\\Roaming\\npm\\node_modules\\@qwen-code\\qwen-code\\dist\\index.js',
                    '--prompt', prompt
                ], capture_output=True, text=True, encoding='utf-8', timeout=120)

                if result.returncode != 0:
                    st.error("⚠️ AI processing failed. Please try again.")
                    return None

                # Clean the output to remove system messages and keep only the actual summary
                raw_output = result.stdout.strip()

                # Remove common system messages from Qwen CLI output
                system_messages = [
                    "Loaded cached Qwen credentials.",
                    "Loading Qwen model...",
                    "Processing request...",
                    "Generating response...",
                    "Qwen Coder",
                    "qwen-code",
                    "Node.js",
                    "npm"
                ]

                # Split output into lines and filter out system messages
                lines = raw_output.split('\n')
                cleaned_lines = []

                for line in lines:
                    line = line.strip()
                    # Skip empty lines
                    if not line:
                        continue
                    # Skip system messages (case-insensitive)
                    if any(msg.lower() in line.lower() for msg in system_messages):
                        continue
                    # Skip lines that look like debug output (contain file paths, version info, etc.)
                    if any(char in line for char in ['[', ']', '{', '}', 'C:\\', '/usr/', 'node_modules']):
                        continue
                    # Keep the line if it looks like actual summary content
                    cleaned_lines.append(line)

                # Join the cleaned lines back together
                summary = '\n'.join(cleaned_lines).strip()

                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

                return summary if summary else "Summary could not be generated."

        except subprocess.TimeoutExpired:
            st.error("⚠️ Processing took too long. Please try with a shorter video.")
            return None
        except Exception as e:
            st.error("⚠️ AI processing failed. Please try again.")
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
    st.markdown('<div class="main-header">YouTube Video Summarizer</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Get quick summaries from YouTube videos</div>', unsafe_allow_html=True)

    # Initialize the summarizer
    summarizer = YouTubeSummarizer()

    # Input section with form for better UX
    st.markdown("### Enter YouTube URL")

    # Create a form to handle Enter key and button clicks
    with st.form("url_form"):
        url = st.text_input(
            "YouTube URL",
            placeholder="Paste your YouTube video link here...",
            label_visibility="hidden"
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

            # Step 2: Generate summary
            status_text.text("Creating summary...")
            summary = summarizer.summarize_text(transcript, video_title, channel_name)

            if not summary:
                return

            progress_bar.progress(100)
            status_text.text("Complete!")

            # Display results - focus on summary
            st.markdown("### Summary")
            st.markdown(f'<div class="success-message">{summary}</div>', unsafe_allow_html=True)

        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)

        finally:
            progress_bar.empty()
            status_text.empty()

    # Minimal footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #999; font-size: 0.9rem;'>"
        "Powered by AI"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()

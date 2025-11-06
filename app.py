import streamlit as st
import os
import re
import requests
from typing import List
from apify_client import ApifyClient
from openai import OpenAI
import streamlit.components.v1 as components
import markdown

# Load environment variables from .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Page configuration
st.set_page_config(
    page_title="YouTube Summarizer",
    page_icon="📝",
    layout="centered"
)

# Custom CSS for minimalistic design
st.markdown("""
<style>
    .success-message {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        color: #495057;
        padding: 1rem;
        border-radius: 6px;
        margin: 0.5rem 0;
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
    }

    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
    }

    .stTextInput > div > div > input {
        border-radius: 6px;
    }

    .stForm button[data-testid="stFormSubmitButton"] {
        width: auto !important;
        height: auto !important;
        padding: 0.2rem !important;
        font-size: 20px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        margin: 0 !important;
        min-height: 40px !important;
    }

    .stForm .row-widget {
        align-items: stretch !important;
    }

    .stForm [data-testid="column"] {
        display: flex !important;
        align-items: center !important;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=3600)  # Cache for 1 hour
def fetch_openrouter_models(api_key: str) -> List[str]:
    """Fetch free/low-cost models from OpenRouter API for Google, DeepSeek, and Qwen vendors"""
    url = "https://openrouter.ai/api/v1/models"
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        vendors = ["google", "deepseek", "qwen"]  # Gemini (google), Deepseek, Qwen (includes Qwen3 variants)

        # First try to get completely free models
        free_models = [
            model["id"] for model in data["data"]
            if any(vendor in model["id"].lower() for vendor in vendors)
            and model.get("pricing", {}).get("prompt") == "0"
            and model.get("pricing", {}).get("completion") == "0"
        ]

        # If no free models, include very low-cost models (under $0.001 per token)
        if not free_models:
            low_cost_models = [
                model["id"] for model in data["data"]
                if any(vendor in model["id"].lower() for vendor in vendors)
                and model.get("pricing", {}).get("prompt", "0") != "0"
                and model.get("pricing", {}).get("completion", "0") != "0"
                and float(model.get("pricing", {}).get("prompt", "0") or "0") < 0.001
                and float(model.get("pricing", {}).get("completion", "0") or "0") < 0.001
            ]
            return low_cost_models

        return free_models
    return []

def extract_transcript_apify(youtube_url):
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
            video_date = None

            for item in client.dataset(run["defaultDatasetId"]).iterate_items():
                # Extract video title if available
                if 'videoTitle' in item and item['videoTitle']:
                    video_title = item['videoTitle']

                # Extract channel name if available
                if 'channelName' in item and item['channelName']:
                    channel_name = item['channelName']

                # Extract video date if available
                if 'videoDate' in item and item['videoDate']:
                    video_date = item['videoDate']

                # Extract transcript content
                if 'transcript' in item and item['transcript']:
                    transcript_text += item['transcript'] + "\n"
                elif 'text' in item and item['text']:
                    transcript_text += item['text'] + "\n"

            if not transcript_text.strip():
                st.error("❌ No transcript found in the video.")
                return None, video_title or "YouTube Video", channel_name or "Unknown Channel", video_date

            return transcript_text, video_title or "YouTube Video", channel_name or "Unknown Channel", video_date


        except Exception as e:
            st.error(f"❌ Error extracting transcript: {str(e)}")
            return None, "YouTube Video", "Unknown Channel", None


def summarize_text(text, model="google/gemini-2.0-flash-exp:free", video_title=None, channel_name=None, video_date=None, custom_prompt=None, available_models=None):
        """Summarize text using OpenRouter API with automatic model switching on rate limits"""
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

            # Try models in order if rate limited
            models_to_try = [model]
            if available_models and model in available_models:
                # Add other available models as fallbacks
                for fallback_model in available_models:
                    if fallback_model != model and fallback_model not in models_to_try:
                        models_to_try.append(fallback_model)

            for attempt, current_model in enumerate(models_to_try):
                try:
                    with st.spinner(f"{spinner_text} (trying {current_model})" if attempt > 0 else spinner_text):
                        completion = client.chat.completions.create(
                            model=current_model,
                            messages=[
                                {
                                    "role": "user",
                                    "content": prompt
                                }
                            ]
                        )

                        if not completion or not completion.choices:
                            if attempt < len(models_to_try) - 1:
                                st.warning(f"⚠️ Model {current_model} did not return a valid response. Trying next model...")
                                continue
                            else:
                                st.error("❌ All models failed to return a valid response. Please try again later.")
                                return None

                        summary = completion.choices[0].message.content.strip()
                        if summary:
                            if attempt > 0:
                                st.success(f"✅ Successfully used {current_model} after {current_model} failed!")
                            return summary
                        else:
                            if attempt < len(models_to_try) - 1:
                                st.warning(f"⚠️ Model {current_model} returned empty response. Trying next model...")
                                continue
                            else:
                                return "Summary could not be generated."

                except Exception as e:
                    error_str = str(e)
                    
                    # Handle rate limit errors (429)
                    if "429" in error_str or "rate" in error_str.lower():
                        if attempt < len(models_to_try) - 1:
                            st.warning(f"⚠️ Model {current_model} is rate limited. Trying next model...")
                            continue
                        else:
                            st.error("❌ All models are currently rate limited. Please try again later.")
                            return None
                    
                    # Handle 404 errors
                    elif "404" in error_str and "data policy" in error_str.lower():
                        if attempt < len(models_to_try) - 1:
                            st.warning(f"⚠️ Model {current_model} has data policy restrictions. Trying next model...")
                            continue
                        else:
                            st.error("❌ All models have data policy restrictions. Please try again later.")
                            return None
                    elif "404" in error_str:
                        if attempt < len(models_to_try) - 1:
                            st.warning(f"⚠️ Model {current_model} not found. Trying next model...")
                            continue
                        else:
                            st.error("❌ All models not found or not available.")
                            return None
                    else:
                        if attempt < len(models_to_try) - 1:
                            st.warning(f"⚠️ Model {current_model} failed: {error_str}. Trying next model...")
                            continue
                        else:
                            st.error(f"❌ All models failed. Last error: {error_str}")
                            return None

            return None

        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
            return None





def extract_transcript_and_title(youtube_url):
    """Extract transcript from YouTube video using Apify and get video title and channel"""
    try:
        # Extract transcript, title, channel, and date using Apify
        result = extract_transcript_apify(youtube_url)
        if not result or not result[0]:
            video_title = result[1] if result and len(result) > 1 else "YouTube Video"
            channel_name = result[2] if result and len(result) > 2 else "Unknown Channel"
            video_date = result[3] if result and len(result) > 3 else None
            return None, video_title, channel_name, video_date

        transcript_text, video_title, channel_name, video_date = result

        # Clean up the transcript text (remove extra whitespace)
        transcript = re.sub(r'\s+', ' ', transcript_text).strip()

        if not transcript:
            return None, video_title, channel_name, video_date

        return transcript, video_title, channel_name, video_date

    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        return None, "YouTube Video", "Unknown Channel", None

def get_or_extract_transcript(youtube_url):
    """Get cached transcript if same URL, otherwise extract new one"""
    # Check if we have cached data for this URL
    if (st.session_state.cached_transcript and 
        st.session_state.cached_video_info and 
        st.session_state.cached_video_info.get('url') == youtube_url):
        
        st.info("📋 Using cached transcript from previous analysis")
        return (st.session_state.cached_transcript, 
                st.session_state.cached_video_info['title'],
                st.session_state.cached_video_info['channel'],
                st.session_state.cached_video_info['date'])
    
    # Extract new transcript
    result = extract_transcript_and_title(youtube_url)
    if result and result[0]:
        transcript, title, channel, date = result
        # Cache the results
        st.session_state.cached_transcript = transcript
        st.session_state.cached_video_info = {
            'url': youtube_url,
            'title': title,
            'channel': channel,
            'date': date
        }
        st.info("🔄 New transcript extracted and cached")
    
    return result

def main():
    # Initialize session state
    defaults = {
        'summary_data': None,
        'current_url': "",
        'current_question': "",
        'selected_model': "google/gemini-2.0-flash-exp:free",
        'cached_transcript': None,
        'cached_video_info': None,
        'chat_history': [],
        'last_question': "",
        'last_url': ""
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

    # Create a form to handle Enter key and button clicks
    form_key = f"url_form_{st.session_state.get('form_counter', 0)}"
    with st.form(form_key):
        # Create columns for URL input and button in the same row
        col1, col2 = st.columns([6, 1])

        with col1:
            url = st.text_input(
                "YouTube URL",
                placeholder="insert youtube link for AI analysis...",
                label_visibility="hidden",
                value=st.session_state.current_url
            )

        with col2:
            # Check mark button aligned with URL input
            submitted = st.form_submit_button("✓", type="primary", help="Summarize")

        # Optional custom question input (inside form for Enter key support)
        with st.expander("Ask a question (Optional)", expanded=False):
            custom_prompt = st.text_input(
                "Custom Question",
                placeholder="e.g., What are the customer feedbacks?",
                label_visibility="collapsed",
                key=f"custom_question_input_{st.session_state.get('form_counter', 0)}"
            )

    # Model selection (outside form to prevent reset)
    api_key = os.getenv("OPENROUTER_API_KEY")
    if api_key:
        models = fetch_openrouter_models(api_key)
        if models:
            selected_model = st.selectbox(
                "AI Model",
                models,
                index=models.index(st.session_state.selected_model) if st.session_state.selected_model in models else 0,
                help="Select an AI model for analysis. Some free models may have data policy restrictions - if one fails, the app will automatically try a known working model."
            )
            st.session_state.selected_model = selected_model
        else:
            st.warning("No free or low-cost models available from selected vendors. Using default model.")
    else:
        st.warning("OpenRouter API key not found. Using default model.")



    # Display current video context if available
    if st.session_state.cached_video_info:
        col1, col2 = st.columns([4, 1])
        with col1:
            video_info = st.session_state.cached_video_info
            st.markdown(f"**📺 Current Video:** {video_info['title']} | **📺 Channel:** {video_info['channel']}")
        with col2:
            if st.button("🗑️ Clear Chat", help="Clear chat history and start fresh"):
                st.session_state.chat_history = []
                st.session_state.summary_data = None
                st.rerun()
    
    # Display chat history if available
    if st.session_state.chat_history:
        st.markdown("### 💬 Chat History")
        for i, chat in enumerate(st.session_state.chat_history):
            with st.expander(f"Q{i+1}: {chat['question'][:50]}{'...' if len(chat['question']) > 50 else ''}", expanded=False):
                st.markdown(f"**Question:** {chat['question']}")
                st.markdown(f"**Answer:**")
                st.markdown(chat['answer'], unsafe_allow_html=True)

    # Display summary below the form if available
    if st.session_state.summary_data:

        summary_data = st.session_state.summary_data
        summary_html = summary_data['html']
        summary_text = summary_data['text']
        displayed_question = summary_data.get('question', '')
        num_lines = summary_text.count('\n') + 1

        # Display results header
        if displayed_question and displayed_question.strip():
            st.markdown("### Answer to Your Question")
        else:
            st.markdown("### Summary")

        # Summary output with copy button
        html_content = f"""
<div style="position: relative;">
<div class="success-message" id="summary-text" style="padding-right: 40px;">
{summary_html}
</div>
<button style="position: absolute; top: 5px; right: 10px; background: none; border: none; cursor: pointer; opacity: 0.7;" onclick="copySummary()">
<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" viewBox="0 0 16 16">
<path fill-rule="evenodd" d="M4 2a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2zm2-1a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1zM2 5a1 1 0 0 0-1 1v8a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1v-1h1v1a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h1v1z"/>
</svg>
</button>
</div>
<script>
function copySummary() {{
    var element = document.getElementById('summary-text');
    var text = element.innerText || element.textContent || '';
    var textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.style.position = 'fixed';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
}}
</script>
        """
        estimated_height = 800 + num_lines * 30
        components.html(html_content, height=estimated_height, scrolling=False)

    # Process when form is submitted
    if submitted:
        # Capture form input immediately before any processing
        current_custom_prompt = custom_prompt or ""
        
        # Store current values
        st.session_state.current_url = url or ""

        # Always clear summary data when form is submitted to prevent stale responses
        st.session_state.summary_data = None
        st.session_state.form_counter = st.session_state.get('form_counter', 0) + 1

        # Check if there's a new question or URL change
        has_new_question = current_custom_prompt.strip() and current_custom_prompt != st.session_state.get('last_question', '')
        has_new_url = url and url != st.session_state.get('last_url', '')

        # Use stored URL if no new URL provided
        if not url and st.session_state.current_url:
            url = st.session_state.current_url

        # Validate URL
        if not url or ("youtube.com" not in url and "youtu.be" not in url):
            st.error("⚠️ Please enter a valid YouTube URL")
            return

        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()

        try:
            # Check if URL changed - if so, clear cache and chat history
            if has_new_url:
                st.session_state.cached_transcript = None
                st.session_state.cached_video_info = None
                st.session_state.chat_history = []
                st.session_state.current_url = url
            
            # Update tracking variables immediately to prevent stale responses
            st.session_state.last_question = current_custom_prompt
            st.session_state.last_url = url
            
            # Clear any existing summary to ensure fresh response
            if 'summary_data' in st.session_state:
                del st.session_state.summary_data
            
            status_text.text("Getting transcript...")
            progress_bar.progress(25)

            result = get_or_extract_transcript(url)
            if not result or not result[0]:
                return

            transcript, video_title, channel_name, video_date = result
            progress_bar.progress(60)

            # Display transcript
            with st.expander("View full transcript"):
                st.text_area("Full transcript", transcript, height=200, disabled=True, label_visibility="hidden")

            # Generate response
            status_text.text("Answering your question..." if current_custom_prompt.strip() else "Creating summary...")
            
            # Get available models for fallback
            available_models = []
            if api_key:
                available_models = fetch_openrouter_models(api_key)
            
            summary = summarize_text(transcript, st.session_state.selected_model, video_title, channel_name, video_date, current_custom_prompt, available_models)

            if not summary:
                return

            summary_html = markdown.markdown(summary, extensions=['tables'])
            progress_bar.progress(100)
            status_text.text("Complete!")

            # Store summary data
            st.session_state.summary_data = {
                'html': summary_html,
                'text': summary,
                'question': current_custom_prompt if current_custom_prompt.strip() else ''
            }

            # Add to chat history if there's a question
            if current_custom_prompt.strip():
                st.session_state.chat_history.append({
                    'question': current_custom_prompt,
                    'answer': summary_html,
                    'timestamp': st.session_state.get('chat_count', 0) + 1
                })
                st.session_state.chat_count = st.session_state.get('chat_count', 0) + 1

            st.rerun()

        except Exception as e:
            st.markdown(f'<div class="error-message">❌ Error: {str(e)}</div>', unsafe_allow_html=True)
        finally:
            progress_bar.empty()
            status_text.empty()


    st.markdown("### Share Your Feedback")
    components.html(
        """
<iframe id='idy_frame' height="100%" width="100%" src="https://wj.qq.com/s2/24721803/2c9f/" frameborder="0" style='min-height:650px' allowfullscreen sandbox="allow-same-origin allow-scripts allow-modals allow-downloads allow-forms allow-popups"></iframe>
        """,
        height=650,
        scrolling=False,
    )


if __name__ == "__main__":
    main()

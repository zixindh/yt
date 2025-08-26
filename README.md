# 🎥 YouTube Video AI Summarizer

A streamlined Streamlit application that automatically extracts YouTube video transcripts using Apify and generates intelligent summaries with speaker identification using Qwen Coder.

🎉 **Try it now:** [https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)

## ✨ Features

- **Simple & Fast**: Just paste a YouTube URL and get instant summaries
- **AI-Powered**: Uses Qwen Coder for intelligent summarization with speaker identification
- **Channel Context**: Extracts video title and channel name for better context
- **Speaker Identification**: AI identifies likely speakers based on channel and content
- **Clean UI**: Beautiful, minimal interface focused on automatic processing
- **No Manual Upload**: Fully automated - no file uploads needed

## 🚀 Quick Start

### Option 1: Use the Deployed App (Easiest)

🎉 **No installation required!** Use the live app directly:

👉 **[https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)**

Just paste any YouTube URL and get instant summaries with speaker identification.

### Option 2: Run Locally

#### Prerequisites

- Python 3.8+
- Qwen Code CLI installed and accessible in PATH

#### Installation

1. **Clone the repository** (if applicable) or navigate to the project folder

2. **Install Qwen Coder CLI**:
   - Install Qwen Coder and ensure the `qwen` command is available in your PATH
   - Make sure `qwen` is accessible from your command line

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` includes:
   - `streamlit` - Web interface
   - `apify-client` - YouTube transcript extraction

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 How to Use

### Using the Deployed App
1. **Open the app**: Visit [https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)
2. **Paste YouTube URL**: Copy and paste any YouTube video URL into the input field
3. **Click Summarize**: Press the "Summarize" button
4. **Get Results**: View the AI-generated summary with speaker identification

### Using Locally (Advanced)
1. **Paste YouTube URL**: Copy and paste any YouTube video URL into the input field
2. **Click Summarize**: Press the "Summarize" button
3. **Automatic Processing**: Watch the progress bar as the app:
   - Uses Apify to extract the video transcript, title, and channel name
   - Processes the transcript content for analysis
   - Generates a summary using Qwen Coder with speaker identification
4. **View Results**: Read the AI-generated summary with identified speakers and optionally view the full transcript

## 🛠️ Technical Details

### Architecture

- **Frontend**: Streamlit for responsive web UI
- **Transcript Extraction**: Apify for automatic YouTube transcript and metadata retrieval
- **AI Summarization**: Qwen Coder CLI assistant with speaker identification
- **Data Processing**: Direct text processing with channel and video context

### Tools Used

- **Apify**: Cloud-based web scraping and data extraction service
- **Qwen Coder CLI**: Free coding assistant for intelligent text summarization

### File Structure

```
youtube-summarizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── context.md            # Project description
├── README.md             # This file
└── test_apify_transcript.py # Test script for Apify integration
```

## ⚠️ Important Notes

- **Processing Time**: Fast transcript extraction and AI summarization
- **Internet Required**: For Apify transcript extraction and Qwen Code API calls
- **Qwen Code**: Must be installed and accessible in system PATH
- **Apify API**: Requires Apify account and API token configuration
- **Subtitle Availability**: Only works with videos that have subtitle tracks available

## 🎯 Supported Content

- YouTube videos with subtitle/caption tracks available
- Automatic extraction of video title and channel name
- Speaker identification based on channel and content context
- Multiple languages (depending on subtitle availability)

## 🐛 Troubleshooting

### Common Issues

1. **"Qwen Coder is not installed"**
   - Install Qwen Coder and ensure the `qwen` command is available in your PATH
   - Ensure `qwen` command is accessible from your terminal

2. **"Apify actor failed to process the video"**
   - Check your Apify API token configuration in the code
   - The video might not have subtitle tracks available on YouTube
   - Check your internet connection

3. **"No transcript found in the video"**
   - The video might not have subtitle tracks available
   - Check if the video has captions enabled (CC button)
   - Try a different video with available subtitles

4. **"Qwen Code timeout"**
   - The transcript text might be too long for processing
   - Try with shorter videos or shorter transcripts

5. **"Module 'apify_client' not found"**
   - Install the apify-client package: `pip install apify-client`
   - Make sure you're using the correct Python environment

### Getting Help

If you encounter issues:
1. Check the terminal output for detailed error messages
2. Ensure all dependencies are properly installed
3. Verify Qwen Coder CLI installation and PATH accessibility
4. Verify FFmpeg installation
5. Check available disk space and RAM

## 🔧 Customization

### Changing Whisper Models

To use different Whisper model sizes, modify the model loading in `app.py`:

```python
# For faster processing (less accurate)
self.whisper_model = whisper.load_model("tiny")

# For higher accuracy (slower, more memory)
self.whisper_model = whisper.load_model("large")
```

### Qwen Code Parameters

To customize Qwen Code behavior, modify the summarization function in `app.py`:

```python
# Adjust these parameters in the subprocess.run call
'--max-tokens', '512',     # Maximum length of summary
'--temperature', '0.7'     # Creativity level (0.0-1.0)
```

### Contextual Prompts

The app automatically includes the video title as context when generating summaries, which helps Qwen Code produce more relevant and accurate summaries. The prompt structure is:

```python
prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Please provide a concise summary of the following transcript from this video:

{transcript}

Create a clear, comprehensive summary that captures the main points, key information, and context from the video title."""
```

## 📄 License

This project is open source. Please check individual tool licenses:
- OpenAI Whisper: MIT License
- Qwen Coder: Free to use (check Qwen Coder license)
- yt-dlp: Unlicense
- Streamlit: Apache 2.0 License

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve the application!

---

Built with ❤️ using cutting-edge AI technology

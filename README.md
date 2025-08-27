# 🎥 YouTube Video AI Summarizer

A streamlined Streamlit application that automatically extracts YouTube video transcripts using Apify and generates intelligent summaries or answers specific questions using OpenRouter AI.

🎉 **Try it now:** [https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)

## ✨ Features

- **Simple & Fast**: Just paste a YouTube URL and get instant summaries or answers
- **AI-Powered**: Uses OpenRouter AI for intelligent summarization and Q&A
- **Custom Questions**: Ask specific questions about video content
- **Channel Context**: Extracts video title and channel name for better context
- **Clean UI**: Beautiful, minimal interface focused on automatic processing
- **No Manual Upload**: Fully automated - no file uploads needed

## 🚀 Quick Start

### Option 1: Use the Deployed App (Easiest)

🎉 **No installation required!** Use the live app directly:

👉 **[https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)**

Just paste any YouTube URL and get instant summaries or answers to your specific questions.

### Option 2: Run Locally

#### Prerequisites

- Python 3.8+
- API tokens for Apify and OpenRouter

#### Installation

1. **Clone the repository** (if applicable) or navigate to the project folder

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

   The `requirements.txt` includes:
   - `streamlit` - Web interface
   - `apify-client` - YouTube transcript extraction
   - `openai` - OpenRouter API client
   - `python-dotenv` - Environment variable management

3. **Set up environment variables**:
   - Create a `.env` file in the project root
   - Add your API tokens:
     ```
     APIFY_API_TOKEN=your_apify_token_here
     OPENROUTER_API_KEY=your_openrouter_key_here
     ```
   - Get tokens from:
     - **Apify**: https://console.apify.com/account/integrations
     - **OpenRouter**: https://openrouter.ai/keys

### Running the Application

```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## 📖 How to Use

### Using the Deployed App
1. **Open the app**: Visit [https://youtuberead.streamlit.app/](https://youtuberead.streamlit.app/)
2. **Paste YouTube URL**: Copy and paste any YouTube video URL into the input field
3. **Optional**: Click "🤔 Ask a specific question (Optional)" to expand and add a custom question
4. **Click Summarize**: Press the "Summarize" button
5. **Get Results**: View the AI-generated summary or answer to your question

### Using Locally (Advanced)
1. **Paste YouTube URL**: Copy and paste any YouTube video URL into the input field
2. **Optional**: Click "🤔 Ask a specific question (Optional)" to expand and add a custom question
3. **Click Summarize**: Press the "Summarize" button
4. **Automatic Processing**: Watch the progress bar as the app:
   - Uses Apify to extract the video transcript, title, and channel name
   - Processes the transcript content for analysis
   - Generates a summary or answers your question using OpenRouter AI
5. **View Results**: Read the AI-generated summary/answer and optionally view the full transcript

## 🛠️ Technical Details

### Architecture

- **Frontend**: Streamlit for responsive web UI
- **Transcript Extraction**: Apify for automatic YouTube transcript and metadata retrieval
- **AI Processing**: OpenRouter API with GPT-OSS-20B model (supports both summarization and Q&A)
- **Data Processing**: Conditional prompt handling with channel and video context

### Tools Used

- **Apify**: Cloud-based web scraping and data extraction service
- **OpenRouter**: AI API service providing access to multiple AI models
- **OpenAI Python Client**: For API communication with OpenRouter

### File Structure

```
youtube-summarizer/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── context.md            # Project description
├── README.md             # This file
└── .streamlit/           # Streamlit configuration (optional)
    └── config.toml       # Streamlit settings
```

## ⚠️ Important Notes

- **Processing Time**: Fast transcript extraction and AI summarization
- **Internet Required**: For Apify transcript extraction and OpenRouter API calls
- **API Tokens**: Requires both Apify and OpenRouter API tokens
- **Environment Variables**: Both APIFY_API_TOKEN and OPENROUTER_API_KEY must be configured
- **Subtitle Availability**: Only works with videos that have subtitle tracks available

## 🔐 Environment Variables Setup

### For Local Development

1. **Create a `.env` file** in the project root:
   ```bash
   touch .env
   ```

2. **Edit `.env` file** and add your API tokens:
   ```
   APIFY_API_TOKEN=your_actual_apify_token_here
   OPENROUTER_API_KEY=your_actual_openrouter_key_here
   ```

### For Streamlit Cloud Deployment

1. **Go to your Streamlit app dashboard**
2. **Navigate to Settings → Secrets**
3. **Add the secrets**:
   ```
   APIFY_API_TOKEN = "your_actual_apify_token_here"
   OPENROUTER_API_KEY = "your_actual_openrouter_key_here"
   ```

4. **Deploy automatically** - Streamlit Cloud will:
   - Install Python packages from `requirements.txt`
   - Start your app with the configured secrets

### Getting Your API Tokens

**Apify Token:**
1. **Sign up/Login** to [Apify Console](https://console.apify.com/)
2. **Go to Settings → Integrations**
3. **Copy your API token**

**OpenRouter Token:**
1. **Sign up/Login** to [OpenRouter](https://openrouter.ai/)
2. **Go to Keys section**
3. **Create a new API key**
4. **Copy your API key**

## 🎯 Supported Content

- YouTube videos with subtitle/caption tracks available
- Automatic extraction of video title and channel name
- Multiple languages (depending on subtitle availability)

## 🐛 Troubleshooting

### Common Issues

1. **"Apify actor failed to process the video"**
   - Check your Apify API token configuration
   - The video might not have subtitle tracks available on YouTube
   - Check your internet connection

2. **"No transcript found in the video"**
   - The video might not have subtitle tracks available
   - Check if the video has captions enabled (CC button)
   - Try a different video with available subtitles

3. **"OpenRouter API key not found"**
   - Set the OPENROUTER_API_KEY environment variable
   - For local: Add it to your `.env` file
   - For Streamlit Cloud: Add secret in app settings
   - Get token from: https://openrouter.ai/keys

4. **"Apify API token not found"**
   - Set the APIFY_API_TOKEN environment variable
   - For local: Add it to your `.env` file
   - For Streamlit Cloud: Add secret in app settings
   - Get token from: https://console.apify.com/account/integrations

5. **"Module 'apify_client' not found"**
   - Install the apify-client package: `pip install apify-client`
   - Make sure you're using the correct Python environment

6. **"Module 'openai' not found"**
   - Install the openai package: `pip install openai`
   - Make sure you're using the correct Python environment

### Getting Help

If you encounter issues:
1. Check the terminal output for detailed error messages
2. Ensure all dependencies are properly installed
3. Verify both API tokens are correctly configured
4. Check available disk space and RAM

## 🔧 Customization

### Changing AI Models

To use different AI models, modify the model name in the `summarize_text` function in `app.py`:

```python
# Current model
model="openai/gpt-oss-20b:free"

# Other available models on OpenRouter
model="anthropic/claude-3-haiku:beta"
model="meta-llama/llama-3-8b-instruct"
```

### Custom Questions

Users can ask specific questions about video content through the custom prompt input box, or leave it empty for automatic summarization.

### Adjusting Prompts

The app automatically includes video context when generating responses. You can customize the prompt structure by modifying the prompt templates in `app.py`:

```python
# For custom questions
prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Transcript:
{transcript}

User Question: {custom_prompt}"""

# For automatic summarization
prompt = f"""You are analyzing a YouTube video titled: "{video_title}"

Please provide a concise summary of the following transcript:

{transcript}

Create a clear summary that captures the main points."""
```

### API Configuration

You can adjust the OpenRouter client configuration in `app.py`:

```python
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key,
    # Add additional headers if needed
    default_headers={
        "HTTP-Referer": "https://your-app-url.com",
        "X-Title": "YouTube Summarizer",
    }
)
```

## 📄 License

This project is open source. Please check individual tool licenses:
- Streamlit: Apache 2.0 License
- Apify Client: Apache 2.0 License
- OpenAI Python Client: MIT License
- OpenRouter: Check their terms of service

## 🤝 Contributing

Feel free to open issues or submit pull requests to improve the application!

---

Built with ❤️ using cutting-edge AI technology

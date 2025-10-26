# YouTube AI Summarizer

Streamlit app for YouTube video transcript analysis with AI-powered Q&A.

## Core Functionality

1. **Transcript Extraction** - Apify API fetches YouTube transcripts with video metadata
2. **AI Analysis** - OpenRouter API with multiple free/low-cost models (Gemini, DeepSeek, Qwen)
3. **Multi-Round Chat** - Ask multiple questions on the same video with chat history
4. **Smart Caching** - Transcripts cached per video URL to avoid re-fetching

## Key Features

- **Custom Questions** - Ask specific questions about the video or get default summary
- **Chat History** - View all Q&A for current video, persists across questions
- **Model Fallback** - Auto-switches models on rate limits or errors
- **Transcript Cache** - Reuses transcript when asking multiple questions on same video
- **Video Context** - Displays video title and channel for current session

## Workflow

1. User enters YouTube URL
2. App extracts transcript via Apify (or uses cached if same URL)
3. User optionally asks a custom question
4. OpenRouter API processes with selected model
5. Answer displayed with chat history
6. User can ask follow-up questions on same video

## Technical Implementation

**Transcript Extraction**: Apify Actor `dB9f4B02ocpTICIEY`
**AI Models**: Dynamic fetch from OpenRouter (Google/DeepSeek/Qwen vendors)
**Session State**: Tracks cached transcripts, video info, chat history per URL
**Error Handling**: Automatic model switching on 429 rate limits or 404 errors

## Recent Fixes

- Fixed variable collision causing AI to answer old questions instead of new ones
- Input capture now happens immediately on form submission
- Chat history cleared only when URL changes, preserved for same video

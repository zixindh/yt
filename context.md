# YouTube Video AI Summarization Tool

A Streamlit application that automatically summarizes YouTube videos using AI.

## Features

- **Easy Input**: Users can paste YouTube video links directly into the UI
- **Automated Processing**: Downloads videos using apify package
- **Smart Summarization**: Leverages Qwen Coder CLI assistant to generate concise summaries

## Workflow

1. User inputs YouTube video URL
2. Apify downloads the transcript
3. Qwen Coder generates a summary of the transcript
4. Results are displayed to the user 

## apify setup
from apify_client import ApifyClient

# Initialize the ApifyClient with your API token
client = ApifyClient("api_token")

# Prepare the Actor input
run_input = {
    "startUrls": ["https://www.youtube.com/watch?v=aAkMkVFwAoo"],
    "language": "Default",
    "includeTimestamps": "No",
}

# Run the Actor and wait for it to finish
run = client.actor("dB9f4B02ocpTICIEY").call(run_input=run_input)

# Fetch and print Actor results from the run's dataset (if there are any)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():

    print(item)

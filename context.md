# YouTube Video AI Summarization Tool

A Streamlit application that automatically summarizes YouTube videos using AI.

## Features

- **Easy Input**: Users can paste YouTube video links directly into the UI
- **Automated Processing**: Downloads videos using apify package
- **Smart Summarization**: Leverages openai/gpt-oss-20b:free ai model to generate concise summaries

## Workflow

1. User inputs YouTube video URL
2. Apify downloads the transcript
3. openrouter api calling openai/gpt-oss-20b:free model generates a summary of the transcript
4. Results are displayed to the user 

## apify setup
from apify_client import ApifyClient

# Initialize the ApifyClient with your API token from environment variable
import os
api_token = os.getenv("APIFY_API_TOKEN")
client = ApifyClient(api_token)

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
## openrouter setup
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
  extra_body={},
  model="openai/gpt-oss-20b:free",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)
print(completion.choices[0].message.content)
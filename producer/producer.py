import asyncio
import requests
import time
import os
import json
from dotenv import load_dotenv, find_dotenv
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")
api_url = os.getenv("URL")

async def run(data):
    # Create a producer client to send messages to the event hub.
    # Specify a connection string to your event hubs namespace and
    # the event hub name.
    producer = EventHubProducerClient.from_connection_string(
        conn_str=EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME
    )
    async with producer:
        # Create a batch.
        event_data_batch = await producer.create_batch()

        # Add events to the batch.
        event_data_batch.add(EventData(json.dumps(data)))

        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)



# Reddit API endpoint
reddit_endpoint = "https://www.reddit.com/top.json"

# Reddit API parameters
params = {
    "limit": 10,
    "after": None,
}

# Number of posts to fetch in each batch
batch_size = 10

# Initial setup for pagination
posts_count = 0

while True:
    # Fetch the next batch of top posts
    response = requests.get(reddit_endpoint, params=params, headers={"User-agent": "your_user_agent"})
    data = response.json()
    posts = response.json()["data"]["children"]

    for post in posts:
        asyncio.run(run(post))

    # Update the 'after' parameter for the next batch
    params["after"] = data['data']['after']
    posts_count += batch_size

    # Check if there are more posts
    if posts_count >= 1000:  # Limit to 1000 posts
        break

    time.sleep(10)

while True:
    time.sleep(1)

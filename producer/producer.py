import asyncio
import requests
import time
import os
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
        event_data_batch.add(EventData(data))

        # Send the batch of events to the event hub.
        await producer.send_batch(event_data_batch)



# Dohvaćanje podataka s API-ja
response = requests.get(api_url, headers={'User-agent': 'tpiuo'})
if response.status_code == 200:
    # Uzimanje podataka o objavama
    posts = response.json()["data"]["children"]

    # Slanje podataka na Event Hub
    for post in posts:
        asyncio.run(run(str(post)))

    # Beskonačna petlja
    while True:
        time.sleep(1)  # Pauza od 1 sekunde kako bi se spriječilo zatvaranje programa
else:
    print("Error fetching data from Reddit API. Status code:", response.status_code)


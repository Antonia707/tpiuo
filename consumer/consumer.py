import os
from azure.eventhub import EventHubConsumerClient, TransportType
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from dotenv import load_dotenv, find_dotenv

dotenv_path = find_dotenv()
load_dotenv(dotenv_path)

# Azure Event Hub Configuration
EVENT_HUB_CONNECTION_STR = os.getenv("EVENT_HUB_CONNECTION_STR")
EVENT_HUB_NAME = os.getenv("EVENT_HUB_NAME")

# Azure Data Lake Storage Configuration
ADLS_CONNECTION_STR = os.getenv("ADLS_CONNECTION_STR")
ADLS_CONTAINER_NAME = os.getenv("ADLS_CONTAINER_NAME")


def save_to_datalake(data, timestamp):

    blob_service_client = BlobServiceClient.from_connection_string(ADLS_CONNECTION_STR)
    container_client = blob_service_client.get_container_client(ADLS_CONTAINER_NAME)

    year, month, day, hour, minute = timestamp.strftime('%Y %m %d %H %M').split()

    directory_path = f"{year}/{month}/{day}/{hour}/{minute}/"
    blob_path = directory_path + f"{timestamp}.json"

    blob_client = container_client.get_blob_client(blob_path)
    blob_client.upload_blob(data)


def on_event(partition_context, event):
    timestamp = event.enqueued_time
    data = event.body_as_str()
    
    print(timestamp)
    print(data)
    save_to_datalake(data, timestamp)
    print(f"Data saved to Data Lake at {timestamp}")


def main():
    consumer_group = '$Default'

    consumer_client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR, consumer_group, eventhub_name=EVENT_HUB_NAME, transport_type=TransportType.Amqp
    )

    try:
        with consumer_client:
            consumer_client.receive(
                on_event=on_event,
                starting_position="-1",  # Start from the latest available event
            )
    except KeyboardInterrupt:
        print("Receiving has stopped.")

if __name__ == "__main__":
    main()

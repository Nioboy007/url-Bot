from pyrogram import Client, filters
import requests
import os
import re
from urllib.parse import unquote
import threading

# Set your API credentials
api_id = "10471716"
api_hash = "f8a1b21a13af154596e2ff5bed164860"
bot_token = "6365859811:AAGK5hlLKtLf-RqlaEXngZTWnfSPISerWPI"

# Create the Pyrogram client
app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Function to download a chunk of the file
def download_chunk(url, start_byte, end_byte, filename, semaphore):
    headers = {'Range': f'bytes={start_byte}-{end_byte}'}
    with requests.get(url, headers=headers, stream=True) as response:
        response.raise_for_status()
        with open(filename, 'ab') as file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    file.write(chunk)
    semaphore.release()

# Define a start message handler
@app.on_message(filters.command("start"))
def start_message(client, message):
    start_text = "Hello! I am your download bot. Send me a /download command followed by the link to download a file."
    message.reply_text(start_text)

# Define a command handler for the /download command
@app.on_message(filters.command("download"))
def download_file_handler(client, message):
    try:
        # Get the link from the command
        link = message.text.split(None, 1)[1]

        # Determine the filename using Content-Disposition
        response = requests.head(link, stream=True)
        content_disposition = response.headers.get('Content-Disposition')
        if content_disposition and 'filename' in content_disposition:
            original_filename = content_disposition.split('filename=')[1].strip('\"')
            # Replace invalid characters with underscores
            sanitized_filename = re.sub(r'[\/:*?"<>|]', '_', original_filename)
            filename = os.path.join(os.getcwd(), sanitized_filename)
        else:
            # If Content-Disposition is not present, use unquoted URL filename
            filename = os.path.join(os.getcwd(), unquote(os.path.basename(link)))

        # Number of threads to use
        num_threads = 4

        # Calculate chunk size for each thread
        chunk_size = -1
        content_length = response.headers.get('Content-Length')
        if content_length:
            content_length = int(content_length)
            chunk_size = content_length // num_threads

        # Create a semaphore to control thread synchronization
        semaphore = threading.Semaphore(0)

        # List to store thread objects
        threads = []

        # Download the file using multiple threads
        with open(filename, 'wb') as file:
            for i in range(num_threads):
                start_byte = i * chunk_size
                end_byte = (i + 1) * chunk_size - 1 if i < num_threads - 1 else None
                thread = threading.Thread(target=download_chunk, args=(link, start_byte, end_byte, filename, semaphore))
                threads.append(thread)
                thread.start()

            # Wait for all threads to finish
            for thread in threads:
                thread.join()

        # Send the downloaded file to the user
        message.reply_document(document=filename)

        # Remove the downloaded file
        os.remove(filename)

    except IndexError:
        # Handle the case where the command is missing the link
        message.reply_text("Please provide a valid link after the /download command.")

    except requests.exceptions.RequestException as e:
        # Handle connection issues or other requests-related errors
        message.reply_text(f"An error occurred: {str(e)}")

    except Exception as e:
        # Handle other exceptions
        message.reply_text(f"An error occurred: {str(e)}")

# Start the bot
app.run()

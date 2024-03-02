from pyrogram import Client, filters
import requests
import os
import re
from urllib.parse import unquote

# Set your API credentials
api_id = "10471716"
api_hash = "f8a1b21a13af154596e2ff5bed164860"
bot_token = "6365859811:AAGK5hlLKtLf-RqlaEXngZTWnfSPISerWPI"

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Define a start message handler
@app.on_message(filters.command("start"))
def start_message(client, message):
    start_text = "Hello! I am your download bot. Send me a /download command followed by the link to download a file."
    message.reply_text(start_text)

# Define a command handler for the /download command
@app.on_message(filters.command("download"))
def download_file(client, message):
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
            # If Content-Disposition is not present, inform the user
            message.reply_text("Content-Disposition header not found. Unable to determine filename.")
            return

        # Download the file using requests
        with requests.get(link, stream=True) as response:
            response.raise_for_status()
            with open(filename, 'wb') as file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        file.write(chunk)

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

from pyrogram import Client, filters
import wget
import os

api_id = "10471716"
api_hash = "f8a1b21a13af154596e2ff5bed164860"
bot_token = "6365859811:AAGK5hlLKtLf-RqlaEXngZTWnfSPISerWPI"

# Create the Pyrogram client
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

        # Create a temporary folder to store the downloaded file
        temp_folder = "downloads"
        os.makedirs(temp_folder, exist_ok=True)

        # Determine the filename using Content-Disposition
        output = wget.download(link, out=temp_folder, bar=wget.bar_thermometer)

        # Send the downloaded file to the user
        message.reply_document(document=output)

        # Remove the temporary folder and its contents
        os.remove(output)
        os.rmdir(temp_folder)

    except IndexError:
        # Handle the case where the command is missing the link
        message.reply_text("Please provide a valid link after the /download command.")

    except Exception as e:
        # Handle other exceptions
        message.reply_text(f"An error occurred: {str(e)}")

# Start the bot
app.run()

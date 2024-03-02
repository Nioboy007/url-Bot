from pyrogram import Client, filters
from pyrogram.types import Message
import wget
import os

API_ID = "10471716"
API_HASH = "f8a1b21a13af154596e2ff5bed164860"
BOT_TOKEN = "6365859811:AAGK5hlLKtLf-RqlaEXngZTWnfSPISerWPI"

app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def download_file(url, chat_id, message_id):
    try:
        filename = wget.download(url)
        app.send_document(chat_id, document=filename, caption="File downloaded successfully! 📥")
        os.remove(filename)  # Remove the downloaded file after uploading
    except Exception as e:
        app.send_message(chat_id, f"Error: {str(e)}")
        app.edit_message_text(chat_id, message_id, text="Failed to download the file. 😔")


@app.on_message(filters.command("start"))
def start_command(_, message):
    message.reply_text("Hello! Send me a link, and I'll download and upload the file for you. 📤")


@app.on_message(filters.text & ~filters.command)
def handle_links(_, message):
    chat_id = message.chat.id
    message_id = message.message_id

    try:
        url = message.text
        app.send_message(chat_id, "Downloading file... 🔄")

        # Download the file and upload
        download_file(url, chat_id, message_id)
    except Exception as e:
        app.send_message(chat_id, f"Error: {str(e)}")


if __name__ == "__main__":
    app.run()

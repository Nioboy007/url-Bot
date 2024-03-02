from pyrogram import Client, filters
from pyrogram.types import Message
from aria2p import API
from aria2p import Aria2, Aria2RPC

aria2 = Aria2(Aria2RPC())

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
API_KEY = '6365859811:AAGK5hlLKtLf-RqlaEXngZTWnfSPISerWPI'
API_ID = 10471716 # Replace with your actual API ID
API_HASH = "f8a1b21a13af154596e2ff5bed164860"  # Replace with your actual API HASH
bot = Client("aria2_bot", api_id=API_ID, api_hash=API_HASH, bot_token=API_KEY)


def start_message():
    return "Welcome! Send me a direct download link, and I'll download and upload the file for you."


def help_message():
    return (
        "Send me a direct download link, and I'll download and upload the file for you. "
        "I support HTTP, HTTPS, FTP, and BitTorrent links."
    )


@bot.on_message(filters.command("start"))
def start(_, message: Message):
    message.reply_text(start_message())


@bot.on_message(filters.command("help"))
def help_command(_, message: Message):
    message.reply_text(help_message())


@bot.on_message(filters.regex(r"(https?|ftp|torrent)://[^\s]+"))
def download_link(_, message: Message):
    # Respond that the download has started
    message.reply_text("Downloading...")

    # Extract the link from the message
    download_link = message.text.strip()

    # Use the global aria2 instance to download the file
    download_path = "downloads/"
    download = aria2.add_uris([download_link], {"dir": download_path})

    # Wait for the download to finish
    download.wait()

    if download.error_message:
        # If there's an error during download, handle it
        message.reply_text(f"Error: {download.error_message}")
    else:
        # If successful, reply with the file
        downloaded_file_path = download.followed_by_ids[0]
        with open(downloaded_file_path, "rb") as file:
            message.reply_document(file)


if __name__ == "__main__":
    bot.run()

import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
from dotenv import load_dotenv

load_dotenv()  # Load variables from .env file
print(os.getenv("BOT_TOKEN"))
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hi there! I can download files from Terabox. Send me a Terabox link to download.")

def download_terabox_file(update, context):
    message_text = update.message.text
    if "terabox.com" in message_text or "teraboxapp.com" in message_text:
        file_details = get_terabox_file_details(message_text)
        if file_details and 'direct_link' in file_details:
            download_file(file_details['direct_link'], update, context)
        else:
            context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to get Terabox file details.")
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Please send a valid Terabox link.")

from bs4 import BeautifulSoup
import requests

def get_terabox_file_details(terabox_link):
    try:
        response = requests.get(terabox_link)
        soup = BeautifulSoup(response.content, 'html.parser')
        # Extracting details from the HTML, adjust as per Terabox's HTML structure
        direct_link = soup.find('a', class_='download-btn')['href']
        file_name = soup.find('h1', class_='file-title').text.strip()
        file_size = soup.find('span', class_='file-size').text.strip()
        return {'direct_link': direct_link, 'file_name': file_name, 'file_size': file_size}
    except Exception as e:
        print("Error extracting Terabox file details:", e)
        return None
    # Example: Call an API or parse the HTML to get the details
    return {'direct_link': 'https://example.com/download/file'}

def download_file(file_url, update, context):
    try:
        response = requests.get(file_url)
        file_name = file_url.split("/")[-1]
        with open(file_name, 'wb') as file:
            file.write(response.content)
        context.bot.send_document(chat_id=update.effective_chat.id, document=open(file_name, 'rb'))
        os.remove(file_name)
    except Exception as e:
        print("Error downloading file:", e)
        context.bot.send_message(chat_id=update.effective_chat.id, text="Failed to download the file.")

def main():
    updater = Updater(token=os.getenv("BOT_TOKEN"), use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, download_terabox_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

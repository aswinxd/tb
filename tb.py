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
        direct_link_elem = soup.find('a', class_='download-btn')
        file_title_elem = soup.find('h1', class_='file-title')
        file_size_elem = soup.find('span', class_='file-size')
        if direct_link_elem and file_title_elem and file_size_elem:
            direct_link = direct_link_elem['href']
            file_name = file_title_elem.text.strip()
            file_size = file_size_elem.text.strip()
            return {'direct_link': direct_link, 'file_name': file_name, 'file_size': file_size}
        else:
            print("Unable to find required elements in HTML")
            return None
    except Exception as e:
        print("Error extracting Terabox file details:", e)
        return None

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

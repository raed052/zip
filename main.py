import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import zipfile
import shutil
from config import TELEGRAM_TOKEN  # Import the token from config.py

# Define start command
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Hello! Send me a Python file and I will prepare it for deployment on Heroku.')

# Handle received files
def handle_file(update: Update, context: CallbackContext) -> None:
    file = update.message.document.get_file()
    file.download('received_file.py')
    
    # Process the file to create required Heroku files
    prepare_heroku_files('received_file.py')
    
    # Send back the zip file
    zip_filename = 'heroku_deployment.zip'
    with open(zip_filename, 'rb') as f:
        update.message.reply_document(document=InputFile(f), filename=zip_filename)

# Function to prepare the Heroku files
def prepare_heroku_files(main_script):
    # Create a directory to store the files
    if not os.path.exists('heroku_files'):
        os.makedirs('heroku_files')

    # Copy the main script to the directory
    shutil.copy(main_script, 'heroku_files/main.py')

    # List of required packages (you can modify this list)
    requirements = [
        "APScheduler==3.6.3",
        "cachetools==4.2.2",
        "certifi==2022.6.15",
        "charset-normalizer==2.1.0",
        "click==8.1.3",
        "docopt==0.6.2",
        "fast-proxy-list==0.0.2",
        "idna==3.3",
        "Flask==2.1.2",
        "itsdangerous==2.1.2",
        "Jinja2==3.1.2",
        "MarkupSafe==2.1.1",
        "pipreqs==0.4.11",
        "pyTelegramBotAPI==4.6.0",
        "python-telegram-bot==13.3",
        "Pytz==2022.1",
        "pytz-deprecation-shim==0.1",
        "requests==2.28.1",
        "six==1.16.0",
        "telebot==0.0.4",
        "tzdata==2022.1",
        "tornado==6.1",
        "tzlocal==4.2",
        "Werkzeug==2.1.2",
        "yarg==0.1.9",
        "uuid==1.30",
        "user-agent==0.1.10",
        "urllib3==1.26.9",
        "pyperclip==1.8.2",
        "beautifulsoup4==4.10.0",
        "websocket-client==1.2.1",
        "autopep8==1.5.7",
        "pyrogram==2.0.106",
        "kvsqlite==0.2.1",
        "schedule==1.1.0",
        "psutil==5.8.0",
        "PyGithub"
    ]

    # Write the requirements to requirements.txt
    with open('heroku_files/requirements.txt', 'w') as f:
        for req in requirements:
            f.write(req + "\n")

    # Create Procfile
    with open('heroku_files/Procfile', 'w') as f:
        f.write('bot: python main.py\n')

    # Create a zip file
    with zipfile.ZipFile('heroku_deployment.zip', 'w') as zipf:
        for root, _, files in os.walk('heroku_files'):
            for file in files:
                zipf.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), 'heroku_files'))
    
    # Clean up
    shutil.rmtree('heroku_files')

def main() -> None:
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.document.mime_type("text/x-python") | Filters.document.mime_type("application/octet-stream"), handle_file))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

import os, sys, subprocess
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler
import logging
import json
import httpcore

from vidGen import generate


with open('config.json', 'r') as config_file:
    config = json.load(config_file)
    
BOT_TOKEN = config['telegram']["token"]

setattr(httpcore, 'SyncHTTPTransport', 'AsyncHTTPProxy')


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


async def generate_and_send(update: Update, context: ContextTypes.DEFAULT_TYPE):
    args = context.args
    # Ensure there are enough arguments
    if len(args) != 2 or args[0] not in ['man', 'woman'] or not args[1].startswith('https://www.reddit.com/r/'):
        await context.bot.send_message(chat_id=update.effective_chat.id, text='Usage: /generate [man|woman] [Reddit Post Link]. Make sure the reddit link starts withh /r')
        return

    # Forward the arguments to the vidGen.py script
    try:
        video_paths = generate(args[0], args[1])
        for i, video_path in enumerate(video_paths):
            await context.bot.send_video(write_timeout=1000,
                                             chat_id=update.effective_chat.id, 
                                             video=open(video_path, 'rb'),
                                             caption=f"Here is your generated video number {i+1} out of {len(video_paths)}!")
        else:
            # Handle errors from vidGen.py
            await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error: We had a problem finding the videos generated.')
    except Exception as e:
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f'Error running vidGen.py: {e}')

if __name__ == '__main__':

    telegramApp = ApplicationBuilder().token(BOT_TOKEN).build()
    
    startHandler = CommandHandler('generate', generate_and_send)
    telegramApp.add_handler(startHandler)

    telegramApp.run_polling()



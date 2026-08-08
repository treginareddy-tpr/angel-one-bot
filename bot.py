import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your trading bot is officially up and running perfectly on PythonAnywhere.")

def main():
    token = "8952306451:AAG1UnFFtb8rTnFkcVQEktc-Zn0CtstIxkQ"
    
    # Configure the mandatory PythonAnywhere free tier proxy settings
    proxy_url = "http://proxy.server:3128"
    
    # Build application with the required proxy routing
    app = Application.builder().token(token).proxy(proxy_url).get_updates_proxy(proxy_url).build()
    app.add_handler(CommandHandler('start', start_command))
    
    print("Bot is successfully polling for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()

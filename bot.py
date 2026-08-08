import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Response function for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is officially up and running perfectly on Render.")

def main():
    # Fetch token securely from Render environment variables
    token = os.environ.get('TELEGRAM_TOKEN')
    
    # Initialize the application
    app = Application.builder().token(token).build()
    
    # Register the start command handler
    app.add_handler(CommandHandler('start', start_command))
    
    # Start checking for incoming messages
    print("Bot is successfully polling for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()

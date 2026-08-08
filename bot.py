import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is officially up and running perfectly on Render.")

def main():
    token = os.environ.get('TELEGRAM_TOKEN')
    
    # Initialize the application
    app = Application.builder().token(token).build()
    
    # Register the start command handler
    app.add_handler(CommandHandler('start', start_command))
    
    # Get port assigned by Render dynamically, default to 8000
    port = int(os.environ.get("PORT", 8000))
    
    # Start web server for Telegram Webhooks instead of polling
    print(f"Starting bot webserver on port {port}...")
    app.run_webhook(
        listen="0.0.0.0",
        port=port,
        webhook_url=f"https://onrender.com{token}"
    )

if __name__ == '__main__':
    main()

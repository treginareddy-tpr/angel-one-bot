import os
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Response function for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is officially up and running perfectly on Render.")

async def post_init(application: Application):
    # Wipes out any stuck webhooks on Telegram's servers instantly
    print("Clearing stuck webhooks from Telegram...")
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("Webhooks successfully cleared!")

def main():
    # Fetch token securely from environment variables
    token = os.environ.get('TELEGRAM_TOKEN')
    
    # Initialize application cleanly without any custom threading
    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler('start', start_command))
    
    print("Bot is successfully polling for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()

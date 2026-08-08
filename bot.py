import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Simple Web Server to keep Render happy
def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Health server running on port {port}")
        httpd.serve_forever()

# Response function for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is officially up and running perfectly on Render.")

async def post_init(application: Application):
    # This completely wipes out any stuck webhooks on Telegram's servers instantly
    print("Clearing stuck webhooks from Telegram...")
    await application.bot.delete_webhook(drop_pending_updates=True)
    print("Webhooks successfully cleared!")

def main():
    # Start the web port in the background so Render passes its scan
    threading.Thread(target=run_health_server, daemon=True).start()

    # Fetch token securely from environment variables
    token = os.environ.get('TELEGRAM_TOKEN')
    
    # Initialize application with post_init hook to wipe webhooks
    app = Application.builder().token(token).post_init(post_init).build()
    app.add_handler(CommandHandler('start', start_command))
    
    print("Bot is successfully polling for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()

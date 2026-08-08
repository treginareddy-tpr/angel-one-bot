import os
import http.server
import socketserver
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# 1. Simple Web Server to keep Render happy
def run_health_server():
    port = int(os.environ.get("PORT", 8000))
    handler = http.server.SimpleHTTPRequestHandler
    # Bind to 0.0.0.0 to accept Render's traffic
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"Health server running on port {port}")
        httpd.serve_forever()

# 2. Response function for the /start command
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Your bot is officially up and running perfectly on Render.")

def main():
    # Start the web port in the background so Render passes its scan
    threading.Thread(target=run_health_server, daemon=True).start()

    # Fetch token securely from environment variables
    token = os.environ.get('TELEGRAM_TOKEN')
    
    # Initialize and run the polling bot
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler('start', start_command))
    
    print("Bot is successfully polling for messages...")
    app.run_polling()

if __name__ == '__main__':
    main()

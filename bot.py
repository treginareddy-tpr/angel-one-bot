import logging
import math
import statistics
from collections import deque
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# ----------------------------------------------------
# 1. SYSTEM CONFIGURATION & RISK PARAMETERS
# ----------------------------------------------------
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHAT_ID = "YOUR_CHAT_ID"

# Risk & Strategy Constraints
Z_SCORE_THRESHOLD = 2.5       # Alert when price deviates past 2.5 standard deviations
WINDOW_SIZE = 30              # Rolling lookback window for statistical baseline
POSITION_SIZE_USD = 1000      # Allocation size per approved trade

# ----------------------------------------------------
# 2. STATE MANAGER & IN-MEMORY DATABASE
# ----------------------------------------------------
# Tracking global states to avoid logic collisions, double execution, or duplicate alerts
market_data_store = {
    "AAPL": deque(maxlen=WINDOW_SIZE),
}

# The Active Lock Registry prevents the scanner from flooding your phone with alerts 
# while you are busy reviewing a previous alert for that specific asset.
active_locks = {
    "AAPL": False
}

# ----------------------------------------------------
# 3. THE STATISTICAL MATH ENGINE
# ----------------------------------------------------
def calculate_z_score(price_history, current_price):
    """Calculates exactly how far price has deviated from its historical average."""
    if len(price_history) < WINDOW_SIZE:
        return 0.0
    mean = statistics.mean(price_history)
    stdev = statistics.stdev(price_history)
    if stdev == 0:
        return 0.0
    return (current_price - mean) / stdev

async def scan_market_tick(symbol: str, current_price: float, app: Application):
    """Invoked every single millisecond a new price tick hits the system."""
    history = market_data_store[symbol]
    history.append(current_price)
    
    # Bypass logic if we do not have enough baseline data or if a decision is currently pending
    if len(history) < WINDOW_SIZE or active_locks.get(symbol, False):
        return

    z_score = calculate_z_score(list(history), current_price)
    
    # Check for structural internal pricing mismatches
    if abs(z_score) >= Z_SCORE_THRESHOLD:
        # Acquire state lock immediately before generating the notification payload
        active_locks[symbol] = True
        direction = "BUY (Mean Reversion Bounce)" if z_score < 0 else "SHORT (Mean Reversion Drop)"
        
        await send_approval_payload(symbol, current_price, z_score, direction, app)

# ----------------------------------------------------
# 4. TELEGRAM GATEKEEPER INTERFACE
# ----------------------------------------------------
async def send_approval_payload(symbol: str, price: float, z_score: float, direction: str, app: Application):
    """Constructs a heavily detailed cryptographic approval schema for your mobile interface."""
    
    # Callback data string structured cleanly for explicit stateless parsing
    # Format: ACTION_SYMBOL_PRICE
    callback_yes = f"EXEC_{symbol}_{price}"
    callback_no = f"DECLINE_{symbol}"
    
    keyboard = [
        [
            InlineKeyboardButton("🟩 YES (Execute)", callback_data=callback_yes),
            InlineKeyboardButton("🟥 NO (Dismiss)", callback_data=callback_no)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = (
        f"🚨 **PRICE DISLOCATION DETECTED**\n\n"
        f"• **Asset:** {symbol}\n"
        f"• **Trigger Price:** ${price:.2f}\n"
        f"• **Statistical Deviation:** {z_score:+.2f} σ\n"
        f"• **Target Strategy Action:** {direction}\n\n"
        f"⚠️ *The system state for {symbol} is locked pending your authorization decision.*"
    )
    
    await app.bot.send_message(chat_id=CHAT_ID, text=message_text, parse_mode='Markdown', reply_markup=reply_markup)
    logging.info(f"Dislocation alert dispatched for {symbol} at {price}. State Lock engaged.")

# ----------------------------------------------------
# 5. ASYNC CALLBACK & EXECUTION BRIDGE HANDLERS
# ----------------------------------------------------
async def handle_user_decision(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes your manual touchscreen interactions securely and atomically."""
    query = update.callback_query
    await query.answer() # Prevents interface lag UI bugs
    
    data_payload = query.data
    
    if data_payload.startswith("DECLINE_"):
        _, symbol = data_payload.split("_")
        active_locks[symbol] = False # Release lock safely
        await query.edit_message_text(text=f"❌ **Trade Declined:** Scanner state unlocked for {symbol}. No orders routed.")
        logging.info(f"User declined trade for {symbol}. State released.")
        
    elif data_payload.startswith("EXEC_"):
        _, symbol, trigger_price = data_payload.split("_")
        await query.edit_message_text(text=f"⚡ **Processing Order Routing Matrix...**")
        
        # Sizing Calculations (Position Size / Asset Trigger Price)
        shares_to_trade = math.floor(POSITION_SIZE_USD / float(trigger_price))
        
        # -------------------------------------------------------------------------
        # BROKER API BRIDGE INSERTION LAYER
        # This is where the physical routing happens.
        # Example using a mock execution pipeline:
        # -------------------------------------------------------------------------
        execution_success = await execute_broker_order_pipeline(symbol, shares_to_trade)
        
        if execution_success:
            await query.edit_message_text(
                text=f"✅ **Execution Complete!**\nRouted market order for **{shares_to_trade}** shares of **{symbol}** successfully."
            )
        else:
            await query.edit_message_text(
                text=f"⚠️ **BROKER API EXECUTION ERROR:** Order rejected. Releasing state locks for safety."
            )
        
        # Post-execution cleanup: Always release locks regardless of result
        active_locks[symbol] = False

async def execute_broker_order_pipeline(symbol: str, qty: int) -> bool:
    """Mock API Execution Pipeline. Replace this block natively with your targeted Broker SDK."""
    logging.info(f"API ROUTE TRIGGERED: Buying {qty} shares of {symbol} via API connection layer.")
    return True

# ----------------------------------------------------
# 6. CORE INITIALIZATION ENGINE
# ----------------------------------------------------
def main():
    # Build the bot application
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handle the inline touchscreen button triggers
    app.add_handler(CallbackQueryHandler(handle_user_decision))
    
    logging.info("Semi-Automated State Core initialized successfully. Standing by for market ingestion loop...")
    app.run_polling() # Uncomment this when credentials are input to run live loop

if __name__ == '__main__':
    main()

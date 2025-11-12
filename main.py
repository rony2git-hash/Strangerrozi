import json
import re
import requests
from urllib.parse import quote_plus
import asyncio

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# === CONFIG ===
BOT_TOKEN = "7549965981:AAH4gvaz18_bkUhJHaHffKfkabABJXm-ATk"

# Channel / Group Check
CHANNEL_USERNAME = "@stangerboy"
CHANNEL_JOIN_URL = "https://t.me/stangerboy"

WELCOME_IMAGE = "https://i.ibb.co/ccV44ZRS/STRANGER-BOY.jpg"
WELCOME_TEXT = (
"╔══════════════════════════════╗\n"
"║ 🔥 Welcome to STRANGER-X Bot🔥 \n"
"╠══════════════════════════════╣\n"
"║ Select an option below to search 💥\n"
"╠═══════════════════════════╣                            \n"
"║  🛠️ Developed By: @strangersboys24 \n"
"╚═══════════════════════════╝"
)

# --- APIs ---
MOBILE_API = "https://number-to-information.vercel.app/fetch?key=NO-LOVE&num="
AADHAR_API = "https://rose-x-tool.vercel.app/fetch?key=@Ros3_x&aadhaar="
VEHICLE_API = "https://vehicle-2-info.vercel.app/rose-x?vehicle_no="
PAK_API = "https://seller-ki-mkc.taitanx.workers.dev/?aadhar="

# Blocked numbers
BLOCKED_NUMBERS = {
    "8859772859": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "9756887329": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆", 
    "9045772859": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "7500194354": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "8439474543": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "8791849129": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "8869014354": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "6387346308": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "8817332717": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
    "7818853969": "Ooh STRANGER  Ka Number Ka Info Chahiye 😁😆",
}

# Developer contact URL (used for the button)
DEVELOPER_CONTACT_URL = "https://t.me/strangersboys24"  
DEVELOPER_TAG = "Developer ➜ @strangersboys24" 

# Track pending input type per user
USER_PENDING_TYPE = {}  # key = user_id, value = "mobile" / "aadhar" / "pak" / "vehicle"

# ---------- helpers ----------
def main_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("👭👬 Enter Aadhar to Family", callback_data="aadhar")],
        [InlineKeyboardButton("📞 Enter Mobile Number", callback_data="mobile")],
        [InlineKeyboardButton("🧍🏻 Enter Aadhar Number", callback_data="pak")],
        [InlineKeyboardButton("🚗 Enter Vehicle Number", callback_data="vehicle")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)], 
    ]
    return InlineKeyboardMarkup(keyboard)

def result_inline_keyboard():
    keyboard = [
        [InlineKeyboardButton("↩️ Back to Main Menu", callback_data="main_menu")],
        [InlineKeyboardButton("🪪 Developer Contact", url=DEVELOPER_CONTACT_URL)], 
    ]
    return InlineKeyboardMarkup(keyboard)

def join_channel_markup():
    keyboard = [[InlineKeyboardButton("✅ Join Our Channel", url=CHANNEL_JOIN_URL)]]
    return InlineKeyboardMarkup(keyboard)

def clean_number(number: str) -> str:
    return re.sub(r"[^\d+]", "", number or "")

def is_blocked_number(number: str):
    number_clean = clean_number(number)
    for blocked, response in BLOCKED_NUMBERS.items():
        blocked_clean = clean_number(blocked)
        if blocked_clean in number_clean or number_clean.endswith(blocked_clean):
            return response
    return False

async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not CHANNEL_USERNAME or CHANNEL_USERNAME.startswith("YOUR_"):
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        return member.status in ['member', 'creator', 'administrator']
    except:
        return False

async def check_and_block_if_not_joined(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    if not user:
        return False
    is_joined = await check_subscription(user.id, context)
    if not is_joined:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="⚠️ ACCESS DENIED ⚠️\n\nYou must join our channel to use this bot. Press /start after joining.",
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=join_channel_markup()
        )
        return False
    return True

# ---------- handlers ----------
async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_block_if_not_joined(update, context):
        return
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=WELCOME_IMAGE,
        caption=WELCOME_TEXT,
        parse_mode=ParseMode.HTML,
        reply_markup=main_inline_keyboard(),
    )

async def process_number(chat_id: int, number_type: str, number: str, context: ContextTypes.DEFAULT_TYPE):
    blocked_response = is_blocked_number(number)
    if blocked_response:
        await context.bot.send_message(chat_id=chat_id, text=blocked_response, reply_markup=main_inline_keyboard())
        return

    number_clean = clean_number(number)
    
    # Input Validation
    if number_type == "mobile" and len(number_clean) != 10:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid mobile number. Must be 10 digits.", reply_markup=main_inline_keyboard())
        return
    if number_type == "aadhar" and len(number_clean) != 12:
        await context.bot.send_message(chat_id=chat_id, text="❌ Invalid Aadhar number. Must be 12 digits.", reply_markup=main_inline_keyboard())
        return
    
    loading_msg = await context.bot.send_message(chat_id=chat_id, text="⏳ Processing...", parse_mode=ParseMode.HTML)

    # Select API
    if number_type == "mobile":
        api_url = MOBILE_API + quote_plus(number_clean)
    elif number_type == "aadhar":
        api_url = AADHAR_API + quote_plus(number_clean)
    elif number_type == "vehicle":
        api_url = VEHICLE_API + quote_plus(number_clean)
    else:  # pak
        api_url = PAK_API + quote_plus(number_clean)

    try:
        resp = requests.get(api_url, timeout=15)
        try:
            data = resp.json()
        except Exception:
            data = {"error": resp.text or "No response"}
    except Exception as e:
        data = {"error": str(e)}

    developer_credit = f"\n\n {DEVELOPER_TAG}"
    final_text = f"<b>Result for {number_type.capitalize()} Number:</b>\n<pre>{json.dumps(data, indent=2)}</pre>{developer_credit}"
    reply_markup = result_inline_keyboard()

    try:
        msg = await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=loading_msg.message_id,
            text=final_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except:
        msg = await context.bot.send_message(
            chat_id=chat_id,
            text=final_text,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        ) 

    # 🔥 Auto-delete after 5 minutes
    async def auto_delete():
        await asyncio.sleep(300)  # 5 minutes
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        except:
            pass

    asyncio.create_task(auto_delete())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if not await check_and_block_if_not_joined(update, context):
        return
    
    if query.data in ["aadhar", "mobile", "pak", "vehicle"]:
        USER_PENDING_TYPE[user_id] = query.data
        prompt = {
            "aadhar": "Please enter your 12-digit Aadhar number:",
            "mobile": "Please enter your 10-digit mobile number:",
            "pak": "Please enter your 12-digit Aadhar number:",
            "vehicle": "Please enter the IFSC CODE"
        }
        await query.message.reply_text(prompt[query.data])
    
    elif query.data == "main_menu":
        try:
            await query.message.delete()
        except:
            pass
            
        await context.bot.send_photo(
            chat_id=update.effective_chat.id,
            photo=WELCOME_IMAGE,
            caption=WELCOME_TEXT,
            parse_mode=ParseMode.HTML,
            reply_markup=main_inline_keyboard(),
        )

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_and_block_if_not_joined(update, context):
        return

    user_id = update.effective_user.id
    text = (update.message.text or "").strip()
    
    if user_id in USER_PENDING_TYPE:
        number_type = USER_PENDING_TYPE.pop(user_id)
        await process_number(update.effective_chat.id, number_type, text, context)
        return
        
    await update.message.reply_text(
        "Please select an option from the menu below.",
        reply_markup=main_inline_keyboard()
    )

# ---------- main ----------
def main():
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_router))
    application.add_handler(CallbackQueryHandler(button_handler))
    print("Bot starting...")
    application.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
    try:
        print("🚀 Starting Stranger-X Bot...")
        main()
    except KeyboardInterrupt:
        print("🛑 Bot stopped manually.")
    except Exception as e:
        import traceback
        print("❌ Error while running the bot:")
        traceback.print_exc()


import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from googletrans import Translator, LANGUAGES
import re

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize translator
translator = Translator()

# Language codes for quick selection
QUICK_LANGUAGES = {
    'en': 'English',
    'es': 'Spanish',
    'fr': 'French',
    'de': 'German',
    'it': 'Italian',
    'pt': 'Portuguese',
    'ru': 'Russian',
    'zh-cn': 'Chinese (Simplified)',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ar': 'Arabic',
    'hi': 'Hindi',
    'bn': 'Bengali',
    'ur': 'Urdu',
    'tl': 'Tagalog',
    'vi': 'Vietnamese',
    'th': 'Thai',
    'id': 'Indonesian',
    'ms': 'Malay',
    'sw': 'Swahili',
    'ha': 'Hausa',
    'yo': 'Yoruba',
    'ig': 'Igbo',
    'zu': 'Zulu'
}

# User preferences storage (simple dict, consider using database for production)
user_prefs = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a welcome message when /start is issued."""
    user = update.effective_user
    welcome_text = f"""
👋 Hello {user.first_name}! Welcome to LingoGlobal Bot!

🌍 I can translate text between 100+ languages instantly.

📌 **How to use me:**
• Send any text and I'll auto-detect and translate it
• Use /translate [text] to translate specific text
• Use /lang [language_code] to change your target language
• Use /languages to see all supported languages
• Use /quick to set a quick language

🔧 **Commands:**
/start - Show this welcome message
/help - Show help information
/translate [text] - Translate specific text
/languages - Show all supported languages
/lang [code] - Change target language
/quick - Quick language selection
/setlang - Interactive language setup
/about - About this bot

🎯 Your current target language is: {context.user_data.get('target_lang', 'English (en)')}

Simply send me any text to get started!
    """
    await update.message.reply_text(welcome_text)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a help message."""
    help_text = """
📖 **LingoGlobal Bot Help**

**Basic Usage:**
• Send any text → Auto-detect and translate to your target language
• Reply to a message with /translate → Translate the replied message

**Commands:**
/start - Welcome message
/help - This help menu
/translate [text] - Translate specific text
/languages - List all supported languages
/lang [code] - Set your target language
/quick - Quick language selection menu
/setlang - Step-by-step language setup
/about - About this bot
/detect [text] - Detect language of text

**Examples:**
• Send: "Hello world" → Translated to your target language
• /translate "Bonjour tout le monde" → Translate to your target language
• /lang es → Set Spanish as your target language
• /detect "Hola" → Returns: Spanish

**Tips:**
• Use /quick for fast language switching
• Reply to any message with /translate to translate it
• Your language preference is saved

**Supported Languages:** 100+ languages including English, Spanish, French, German, Chinese, Japanese, Arabic, Hindi, and many more!
    """
    await update.message.reply_text(help_text)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send about information."""
    about_text = """
🌐 **LingoGlobal Bot v1.0**

A powerful translation bot that supports 100+ languages with auto-detection and smart features.

**Features:**
• Auto language detection
• 100+ language support
• Quick language switching
• Reply translation
• Interactive setup

**Technology:**
• Python Telegram Bot API
• Google Translate API
• Railway Cloud Hosting
• GitHub Integration

**Developer:** LingoGlobal Team
**Source Code:** Available on GitHub
**Feedback:** Contact @LingoGlobalSupport

Made with ❤️ for global communication!
    """
    await update.message.reply_text(about_text)

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Translate text using /translate command."""
    text_to_translate = ' '.join(context.args) if context.args else None
    
    # If user replied to a message, translate that
    if update.message.reply_to_message:
        text_to_translate = update.message.reply_to_message.text
    
    if not text_to_translate:
        await update.message.reply_text("❌ Please provide text to translate.\nExample: /translate Hello world")
        return
    
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        result = translator.translate(text_to_translate, dest=target_lang)
        detected_lang = LANGUAGES.get(result.src, result.src).title()
        target_lang_name = LANGUAGES.get(target_lang, target_lang).title()
        
        response = f"""
📝 **Original:** {text_to_translate}
🌐 **Detected:** {detected_lang}
🎯 **Target:** {target_lang_name}
✨ **Translation:** {result.text}
        """
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't translate that text. Please try again.")

async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Detect language of text."""
    text_to_detect = ' '.join(context.args) if context.args else None
    
    if update.message.reply_to_message:
        text_to_detect = update.message.reply_to_message.text
    
    if not text_to_detect:
        await update.message.reply_text("❌ Please provide text to detect.\nExample: /detect Hello world")
        return
    
    try:
        result = translator.detect(text_to_detect)
        lang_name = LANGUAGES.get(result.lang, result.lang).title()
        confidence = result.confidence * 100
        
        response = f"""
🔍 **Language Detection Results**

📝 **Text:** {text_to_detect}
🌐 **Detected Language:** {lang_name} ({result.lang})
📊 **Confidence:** {confidence:.1f}%
        """
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Detection error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't detect the language. Please try again.")

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show all supported languages."""
    # Create a list of languages with their codes
    lang_list = []
    for code, name in sorted(LANGUAGES.items()):
        if len(code) == 2 or code.startswith('zh-'):
            lang_list.append(f"• {code}: {name.title()}")
    
    # Paginate results (show 30 languages per page)
    page_size = 30
    total_pages = (len(lang_list) + page_size - 1) // page_size
    
    if total_pages == 0:
        await update.message.reply_text("❌ No languages found.")
        return
    
    page = 0  # Start with first page
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(lang_list))
    
    response = f"🌍 **Supported Languages** (Page {page+1}/{total_pages})\n\n"
    response += "\n".join(lang_list[start_idx:end_idx])
    response += "\n\n💡 Use /lang [code] to set your target language"
    
    await update.message.reply_text(response)

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Set target language."""
    if not context.args:
        current_lang = context.user_data.get('target_lang', 'en')
        lang_name = LANGUAGES.get(current_lang, current_lang).title()
        await update.message.reply_text(f"🌐 Your current target language is: **{lang_name}** ({current_lang})\n\nUse /lang [code] to change it.\nExample: /lang es")
        return
    
    lang_code = context.args[0].lower()
    
    # Check if language code is valid
    if lang_code in LANGUAGES:
        context.user_data['target_lang'] = lang_code
        lang_name = LANGUAGES[lang_code].title()
        await update.message.reply_text(f"✅ Target language set to: **{lang_name}** ({lang_code})")
    else:
        await update.message.reply_text(f"❌ Invalid language code: '{lang_code}'. Use /languages to see all supported codes.")

async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show quick language selection menu."""
    keyboard = []
    row = []
    for code, name in QUICK_LANGUAGES.items():
        row.append(InlineKeyboardButton(name[:15], callback_data=f'lang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton("📋 View All Languages", callback_data='view_all_languages')])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🌐 **Quick Language Selection**\n\nChoose your target language:", reply_markup=reply_markup)

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Interactive language setup."""
    await update.message.reply_text("🌐 **Language Setup**\n\nPlease send me the language code you want to use.\n\nExample: `en` for English, `es` for Spanish, `fr` for French\n\nUse /languages to see all available codes.")
    context.user_data['awaiting_lang_setup'] = True

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('lang_'):
        lang_code = data.replace('lang_', '')
        if lang_code in LANGUAGES:
            context.user_data['target_lang'] = lang_code
            lang_name = LANGUAGES[lang_code].title()
            await query.edit_message_text(f"✅ Language set to: **{lang_name}** ({lang_code})\n\nNow send me any text to translate!")
        else:
            await query.edit_message_text("❌ Invalid language code.")
    
    elif data == 'view_all_languages':
        await languages_command(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle regular text messages."""
    # Check if user is in language setup mode
    if context.user_data.get('awaiting_lang_setup'):
        lang_code = update.message.text.lower()
        if lang_code in LANGUAGES:
            context.user_data['target_lang'] = lang_code
            context.user_data['awaiting_lang_setup'] = False
            lang_name = LANGUAGES[lang_code].title()
            await update.message.reply_text(f"✅ Language set to: **{lang_name}** ({lang_code})\n\nNow send me any text to translate!")
        else:
            await update.message.reply_text(f"❌ Invalid language code: '{lang_code}'. Please use /languages to see all available codes.")
        return
    
    # Auto-detect and translate
    text = update.message.text
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        result = translator.translate(text, dest=target_lang)
        detected_lang = LANGUAGES.get(result.src, result.src).title()
        target_lang_name = LANGUAGES.get(target_lang, target_lang).title()
        
        if result.src != target_lang:
            response = f"""
🌐 **Translation**
📝 **Original:** {text}
🔍 **Detected:** {detected_lang}
🎯 **Target:** {target_lang_name}
✨ **Result:** {result.text}
            """
        else:
            response = f"""
ℹ️ **Same Language Detected**
📝 **Text:** {text}
🌐 **Language:** {detected_lang}
💡 The text appears to already be in your target language ({target_lang_name}).
            """
        
        await update.message.reply_text(response)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't translate that text. Please try again.")

def main():
    """Start the bot."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable not set!")
        return
    
    # Create application
    application = ApplicationBuilder().token(token).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    application.add_handler(CommandHandler("translate", translate_command))
    application.add_handler(CommandHandler("detect", detect_command))
    application.add_handler(CommandHandler("languages", languages_command))
    application.add_handler(CommandHandler("lang", lang_command))
    application.add_handler(CommandHandler("quick", quick_command))
    application.add_handler(CommandHandler("setlang", setlang_command))
    
    # Add callback handler for inline buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handler for regular text
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start polling
    logger.info("Bot started! Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()

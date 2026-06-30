"""
LingoGlobal Bot - A Powerful Telegram Translation Bot
Supports 100+ languages with auto-detection
Deployed on Railway with GitHub integration
"""

import os
import sys
import logging
from typing import Dict, Optional, Any

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ==================== CONFIGURATION ====================

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Bot version
VERSION = "1.0.0"

# ==================== LANGUAGE DATA ====================

# Complete language dictionary (Google Translate supported languages)
LANGUAGES = {
    'af': 'Afrikaans',
    'sq': 'Albanian',
    'am': 'Amharic',
    'ar': 'Arabic',
    'hy': 'Armenian',
    'az': 'Azerbaijani',
    'eu': 'Basque',
    'be': 'Belarusian',
    'bn': 'Bengali',
    'bs': 'Bosnian',
    'bg': 'Bulgarian',
    'ca': 'Catalan',
    'ceb': 'Cebuano',
    'ny': 'Chichewa',
    'zh-cn': 'Chinese (Simplified)',
    'zh-tw': 'Chinese (Traditional)',
    'co': 'Corsican',
    'hr': 'Croatian',
    'cs': 'Czech',
    'da': 'Danish',
    'nl': 'Dutch',
    'en': 'English',
    'eo': 'Esperanto',
    'et': 'Estonian',
    'tl': 'Filipino',
    'fi': 'Finnish',
    'fr': 'French',
    'fy': 'Frisian',
    'gl': 'Galician',
    'ka': 'Georgian',
    'de': 'German',
    'el': 'Greek',
    'gu': 'Gujarati',
    'ht': 'Haitian Creole',
    'ha': 'Hausa',
    'haw': 'Hawaiian',
    'iw': 'Hebrew',
    'hi': 'Hindi',
    'hmn': 'Hmong',
    'hu': 'Hungarian',
    'is': 'Icelandic',
    'ig': 'Igbo',
    'id': 'Indonesian',
    'ga': 'Irish',
    'it': 'Italian',
    'ja': 'Japanese',
    'jw': 'Javanese',
    'kn': 'Kannada',
    'kk': 'Kazakh',
    'km': 'Khmer',
    'rw': 'Kinyarwanda',
    'ko': 'Korean',
    'ku': 'Kurdish (Kurmanji)',
    'ky': 'Kyrgyz',
    'lo': 'Lao',
    'la': 'Latin',
    'lv': 'Latvian',
    'lt': 'Lithuanian',
    'lb': 'Luxembourgish',
    'mk': 'Macedonian',
    'mg': 'Malagasy',
    'ms': 'Malay',
    'ml': 'Malayalam',
    'mt': 'Maltese',
    'mi': 'Maori',
    'mr': 'Marathi',
    'mn': 'Mongolian',
    'my': 'Myanmar (Burmese)',
    'ne': 'Nepali',
    'no': 'Norwegian',
    'or': 'Odia (Oriya)',
    'ps': 'Pashto',
    'fa': 'Persian',
    'pl': 'Polish',
    'pt': 'Portuguese',
    'pa': 'Punjabi',
    'ro': 'Romanian',
    'ru': 'Russian',
    'sm': 'Samoan',
    'gd': 'Scots Gaelic',
    'sr': 'Serbian',
    'st': 'Sesotho',
    'sn': 'Shona',
    'sd': 'Sindhi',
    'si': 'Sinhala',
    'sk': 'Slovak',
    'sl': 'Slovenian',
    'so': 'Somali',
    'es': 'Spanish',
    'su': 'Sundanese',
    'sw': 'Swahili',
    'sv': 'Swedish',
    'tg': 'Tajik',
    'ta': 'Tamil',
    'te': 'Telugu',
    'th': 'Thai',
    'tr': 'Turkish',
    'uk': 'Ukrainian',
    'ur': 'Urdu',
    'ug': 'Uyghur',
    'uz': 'Uzbek',
    'vi': 'Vietnamese',
    'cy': 'Welsh',
    'xh': 'Xhosa',
    'yi': 'Yiddish',
    'yo': 'Yoruba',
    'zu': 'Zulu'
}

# Quick access languages (most commonly used)
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
    'tl': 'Filipino',
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

# ==================== CUSTOM TRANSLATION ENGINE ====================

class TranslationEngine:
    """Custom translation engine using multiple free APIs with fallback"""
    
    def __init__(self):
        self.session = None
        self._init_session()
    
    def _init_session(self):
        """Initialize HTTP session"""
        try:
            import requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })
        except ImportError:
            logger.warning("Requests module not available")
            self.session = None
    
    def translate(self, text: str, target_lang: str = 'en', source_lang: str = 'auto') -> Dict:
        """Translate text using MyMemory API (free, no API key required)"""
        try:
            import requests
            
            # Clean text
            text = text.strip()
            if not text:
                return {'success': False, 'error': 'Empty text'}
            
            # MyMemory API endpoint (free, no API key needed)
            url = "https://api.mymemory.translated.net/get"
            params = {
                'q': text,
                'langpair': f'{source_lang}|{target_lang}',
                'de': 'your_email@example.com'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('responseStatus') == 200:
                translated_text = data.get('responseData', {}).get('translatedText', '')
                if translated_text:
                    detected_source = source_lang
                    if source_lang == 'auto':
                        detected_source = data.get('responseData', {}).get('detectedSourceLanguage', 'en')
                    
                    return {
                        'success': True,
                        'source': detected_source,
                        'target': target_lang,
                        'translated': translated_text,
                        'original': text
                    }
            
            return self._translate_fallback(text, target_lang, source_lang)
            
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {'success': False, 'error': str(e)}
    
    def _translate_fallback(self, text: str, target_lang: str, source_lang: str = 'auto') -> Dict:
        """Fallback translation using LibreTranslate (free, no API key)"""
        try:
            import requests
            
            url = "https://libretranslate.de/translate"
            payload = {
                'q': text,
                'source': source_lang if source_lang != 'auto' else 'auto',
                'target': target_lang,
                'format': 'text'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if 'translatedText' in data:
                return {
                    'success': True,
                    'source': data.get('detectedLanguage', {}).get('language', source_lang),
                    'target': target_lang,
                    'translated': data['translatedText'],
                    'original': text
                }
            else:
                return {
                    'success': False,
                    'error': 'All translation services unavailable',
                    'translated': text
                }
                
        except Exception as e:
            logger.error(f"Fallback translation error: {e}")
            return {
                'success': False,
                'error': str(e),
                'translated': text
            }
    
    def detect_language(self, text: str) -> Dict:
        """Detect language using LibreTranslate"""
        try:
            import requests
            
            url = "https://libretranslate.de/detect"
            payload = {'q': text}
            
            response = requests.post(url, json=payload, timeout=10)
            data = response.json()
            
            if data and len(data) > 0:
                best = data[0]
                return {
                    'success': True,
                    'language': best.get('language', 'en'),
                    'confidence': best.get('confidence', 0.5)
                }
            else:
                return {'success': False, 'error': 'Could not detect language'}
                
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return {'success': False, 'error': str(e)}

# Initialize translation engine
translator = TranslationEngine()

# ==================== HELPER FUNCTIONS ====================

def get_language_name(lang_code: str) -> str:
    """Get language name from code, handle fallback."""
    return LANGUAGES.get(lang_code, lang_code).title()

def format_translation_response(result: Dict) -> str:
    """Format translation response for display."""
    if not result.get('success', False):
        return f"❌ **Translation Failed**\n\nError: {result.get('error', 'Unknown error')}"
    
    original = result.get('original', '')
    translated = result.get('translated', '')
    source_lang = result.get('source', 'auto')
    target_lang = result.get('target', 'en')
    
    source_name = get_language_name(source_lang)
    target_name = get_language_name(target_lang)
    
    if source_lang == target_lang or (source_lang == 'auto' and translated == original):
        return f"""
ℹ️ **Same Language Detected**

📝 **Text:** {original}
🌐 **Language:** {source_name}

💡 This text appears to already be in your target language ({target_name}).
"""
    
    return f"""
🌐 **Translation Complete**

📝 **Original:** {original}
🔍 **Detected:** {source_name}
🎯 **Target:** {target_name}
✨ **Result:** {translated}
"""
    
def format_languages_list(page: int = 0, page_size: int = 30) -> str:
    """Format languages list with pagination."""
    lang_items = []
    for code, name in sorted(LANGUAGES.items()):
        lang_items.append(f"• `{code}` → {name}")
    
    total_pages = (len(lang_items) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(lang_items))
    
    if start_idx >= len(lang_items):
        return "❌ No more languages to display."
    
    response = f"🌍 **Supported Languages** (Page {page+1}/{total_pages})\n\n"
    response += "\n".join(lang_items[start_idx:end_idx])
    response += f"\n\n📊 {len(lang_items)} languages total"
    response += "\n💡 Use `/lang [code]` to set your target language"
    
    return response

# ==================== COMMAND HANDLERS ====================

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    user = update.effective_user
    target_lang = context.user_data.get('target_lang', 'en')
    lang_name = get_language_name(target_lang)
    
    welcome_text = f"""
👋 **Hello {user.first_name}!** Welcome to LingoGlobal Bot! 🌍

I'm your AI-powered translation assistant that can translate between **{len(LANGUAGES)}+ languages** instantly.

---

📌 **Quick Start**
• Send me any text → I'll auto-detect and translate it
• Reply to a message with `/translate` → Translate that message
• Use `/quick` → Quick language selection menu

---

🔧 **Commands**
/start - Show this welcome message
/help - Detailed help guide
/translate [text] - Translate specific text
/detect [text] - Detect language of text
/languages - View all supported languages
/lang [code] - Set your target language
/quick - Quick language selection
/setlang - Interactive language setup
/about - About this bot

---

🎯 **Your Target Language:** {lang_name} (`{target_lang}`)

_Simply send me any text to get started!_
"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Quick Language", callback_data='quick_lang')],
        [InlineKeyboardButton("📚 All Languages", callback_data='view_languages')],
        [InlineKeyboardButton("ℹ️ Help", callback_data='help_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    help_text = f"""
📖 **LingoGlobal Bot Help Guide**

---

**🌟 Basic Usage**

1. **Direct Translation**
   Just send any text message and I'll auto-detect the language and translate it to your target language.

2. **Reply Translation**
   Reply to any message with `/translate` to translate that specific message.

3. **Quick Language Switch**
   Use `/quick` to open a menu for fast language selection.

---

**📝 Commands**

| Command | Description |
|---------|-------------|
| `/start` | Welcome message |
| `/help` | This help menu |
| `/translate [text]` | Translate specific text |
| `/detect [text]` | Detect language of text |
| `/languages` | List all supported languages |
| `/lang [code]` | Set target language (e.g., `/lang es`) |
| `/quick` | Quick language selection menu |
| `/setlang` | Interactive step-by-step language setup |
| `/about` | Bot information |

---

**💡 Examples**
• `Hello world` → Translates to your target language
• `/translate "Bonjour tout le monde"` → Translates to target language
• `/lang es` → Sets Spanish as target
• `/detect "Hola"` → Returns: Spanish
• `/quick` → Opens language selection menu

---

**🌍 Supported Languages**
Over {len(LANGUAGES)} languages including English, Spanish, French, German, Chinese, Japanese, Arabic, Hindi, and many more!

Use `/languages` to see the full list.
"""
    
    keyboard = [
        [InlineKeyboardButton("🌐 Quick Language", callback_data='quick_lang')],
        [InlineKeyboardButton("📚 All Languages", callback_data='view_languages')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(help_text, reply_markup=reply_markup)

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /about command."""
    about_text = f"""
🌐 **LingoGlobal Bot** v{VERSION}

A powerful multilingual translation bot with auto-detection and smart features.

---

**✨ Features**
• Auto language detection
• {len(LANGUAGES)}+ language support
• Quick language switching
• Reply translation
• Interactive setup
• User preferences
• Inline keyboards

---

**🛠️ Technology**
• Python 3.11
• python-telegram-bot
• MyMemory API (free)
• LibreTranslate (fallback)
• Railway Cloud Hosting
• GitHub Integration

---

**📊 Statistics**
• Languages: {len(LANGUAGES)}+
• Free to use
• 24/7 uptime

---

**👨‍💻 Developer**
LingoGlobal Team
📧 support@lingoglobal.com

---

_Translating the world, one message at a time._ 🌍
"""
    await update.message.reply_text(about_text)

async def translate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /translate command."""
    text_to_translate = None
    
    if update.message.reply_to_message:
        text_to_translate = update.message.reply_to_message.text
        if not text_to_translate:
            await update.message.reply_text("❌ The replied message doesn't contain any text to translate.")
            return
    
    if not text_to_translate and context.args:
        text_to_translate = ' '.join(context.args)
    
    if not text_to_translate:
        await update.message.reply_text(
            "❌ Please provide text to translate.\n\n"
            "Examples:\n"
            "• `/translate Hello world`\n"
            "• Reply to a message with `/translate`"
        )
        return
    
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        await update.message.chat.send_action(action="typing")
        
        result = translator.translate(text_to_translate, target_lang, 'auto')
        response = format_translation_response(result)
        
        keyboard = [[InlineKeyboardButton("🌐 Change Language", callback_data='quick_lang')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Translation error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I couldn't translate that text.\n"
            "Please check the text and try again."
        )

async def detect_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /detect command."""
    text_to_detect = None
    
    if update.message.reply_to_message:
        text_to_detect = update.message.reply_to_message.text
    
    if not text_to_detect and context.args:
        text_to_detect = ' '.join(context.args)
    
    if not text_to_detect:
        await update.message.reply_text(
            "❌ Please provide text to detect.\n\n"
            "Examples:\n"
            "• `/detect Hello world`\n"
            "• Reply to a message with `/detect`"
        )
        return
    
    try:
        result = translator.detect_language(text_to_detect)
        
        if result.get('success', False):
            lang_name = get_language_name(result['language'])
            confidence = result.get('confidence', 0.5) * 100
            
            response = f"""
🔍 **Language Detection Results**

📝 **Text:** {text_to_detect}
🌐 **Detected Language:** {lang_name} (`{result['language']}`)
📊 **Confidence:** {confidence:.1f}%

{ '✅ High confidence' if confidence > 70 else '⚠️ Moderate confidence' }
"""
            await update.message.reply_text(response)
        else:
            await update.message.reply_text("❌ Could not detect the language. Please try again.")
        
    except Exception as e:
        logger.error(f"Detection error: {e}")
        await update.message.reply_text("❌ Sorry, I couldn't detect the language.")

async def languages_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /languages command."""
    page = context.user_data.get('lang_page', 0)
    response = format_languages_list(page)
    
    total_pages = (len(LANGUAGES) + 29) // 30
    
    if total_pages > 1:
        keyboard = []
        row = []
        if page > 0:
            row.append(InlineKeyboardButton("◀️ Previous", callback_data=f'lang_page_{page-1}'))
        if page < total_pages - 1:
            row.append(InlineKeyboardButton("Next ▶️", callback_data=f'lang_page_{page+1}'))
        keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='quick_lang')])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(response, reply_markup=reply_markup)
        return
    
    await update.message.reply_text(response)

async def lang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /lang command - Set target language."""
    if not context.args:
        current_lang = context.user_data.get('target_lang', 'en')
        lang_name = get_language_name(current_lang)
        await update.message.reply_text(
            f"🌐 **Current Target Language**\n\n"
            f"Language: **{lang_name}** (`{current_lang}`)\n\n"
            f"To change it, use: `/lang [code]`\n"
            f"Example: `/lang es` for Spanish\n\n"
            f"Use `/languages` to see all available codes."
        )
        return
    
    lang_code = context.args[0].lower()
    
    if lang_code in LANGUAGES:
        context.user_data['target_lang'] = lang_code
        lang_name = get_language_name(lang_code)
        await update.message.reply_text(
            f"✅ **Target Language Updated!**\n\n"
            f"Language: **{lang_name}** (`{lang_code}`)\n\n"
            f"All future translations will be in {lang_name}."
        )
    else:
        await update.message.reply_text(
            f"❌ Invalid language code: `{lang_code}`\n\n"
            f"Use `/languages` to see all supported language codes."
        )

async def quick_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /quick command - Quick language selection."""
    keyboard = []
    row = []
    
    for code, name in QUICK_LANGUAGES.items():
        row.append(InlineKeyboardButton(name, callback_data=f'setlang_{code}'))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    
    keyboard.extend([
        [InlineKeyboardButton("📚 View All Languages", callback_data='view_languages')],
        [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
    ])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 **Quick Language Selection**\n\n"
        "Choose your target language from the buttons below:",
        reply_markup=reply_markup
    )

async def setlang_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /setlang command - Interactive language setup."""
    keyboard = [
        [InlineKeyboardButton("🇺🇸 English", callback_data='setlang_en')],
        [InlineKeyboardButton("🇪🇸 Spanish", callback_data='setlang_es')],
        [InlineKeyboardButton("🇫🇷 French", callback_data='setlang_fr')],
        [InlineKeyboardButton("🇩🇪 German", callback_data='setlang_de')],
        [InlineKeyboardButton("🇨🇳 Chinese", callback_data='setlang_zh-cn')],
        [InlineKeyboardButton("🇯🇵 Japanese", callback_data='setlang_ja')],
        [InlineKeyboardButton("🇦🇪 Arabic", callback_data='setlang_ar')],
        [InlineKeyboardButton("🇮🇳 Hindi", callback_data='setlang_hi')],
        [InlineKeyboardButton("📚 More Languages", callback_data='view_languages')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌐 **Interactive Language Setup**\n\n"
        "Select your preferred language from the options below.\n\n"
        "Or type a language code (e.g., `es`, `fr`, `de`).",
        reply_markup=reply_markup
    )
    context.user_data['awaiting_lang_setup'] = True

# ==================== MESSAGE HANDLERS ====================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    text = update.message.text
    
    if context.user_data.get('awaiting_lang_setup'):
        lang_code = text.lower()
        if lang_code in LANGUAGES:
            context.user_data['target_lang'] = lang_code
            context.user_data['awaiting_lang_setup'] = False
            lang_name = get_language_name(lang_code)
            await update.message.reply_text(
                f"✅ **Language Set!**\n\n"
                f"Target language: **{lang_name}** (`{lang_code}`)\n\n"
                f"Now send me any text to translate!"
            )
        else:
            await update.message.reply_text(
                f"❌ Invalid language code: `{lang_code}`\n\n"
                f"Please use a valid code from `/languages`."
            )
        return
    
    target_lang = context.user_data.get('target_lang', 'en')
    
    try:
        await update.message.chat.send_action(action="typing")
        
        result = translator.translate(text, target_lang, 'auto')
        response = format_translation_response(result)
        
        keyboard = [[InlineKeyboardButton("🌐 Change Language", callback_data='quick_lang')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        
    except Exception as e:
        logger.error(f"Message handling error: {e}")
        await update.message.reply_text(
            "❌ Sorry, I encountered an error processing your message.\n"
            "Please try again or use `/help` for assistance."
        )

# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all button callbacks."""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data.startswith('setlang_'):
        lang_code = data.replace('setlang_', '')
        if lang_code in LANGUAGES:
            context.user_data['target_lang'] = lang_code
            lang_name = get_language_name(lang_code)
            await query.edit_message_text(
                f"✅ **Language Set!**\n\n"
                f"Target language: **{lang_name}** (`{lang_code}`)\n\n"
                f"Now send me any text to translate!"
            )
    
    elif data == 'quick_lang':
        keyboard = []
        row = []
        for code, name in QUICK_LANGUAGES.items():
            row.append(InlineKeyboardButton(name, callback_data=f'setlang_{code}'))
            if len(row) == 2:
                keyboard.append(row)
                row = []
        if row:
            keyboard.append(row)
        
        keyboard.extend([
            [InlineKeyboardButton("📚 All Languages", callback_data='view_languages')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='main_menu')]
        ])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "🌐 **Quick Language Selection**\n\nChoose your target language:",
            reply_markup=reply_markup
        )
    
    elif data == 'view_languages':
        page = 0
        response = format_languages_list(page)
        total_pages = (len(LANGUAGES) + 29) // 30
        
        keyboard = []
        if total_pages > 1:
            row = []
            if page < total_pages - 1:
                row.append(InlineKeyboardButton("Next ▶️", callback_data=f'lang_page_{page+1}'))
            row.append(InlineKeyboardButton("🔙 Back", callback_data='quick_lang'))
            keyboard.append(row)
        else:
            keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='quick_lang')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup)
    
    elif data.startswith('lang_page_'):
        page = int(data.replace('lang_page_', ''))
        response = format_languages_list(page)
        total_pages = (len(LANGUAGES) + 29) // 30
        
        keyboard = []
        row = []
        if page > 0:
            row.append(InlineKeyboardButton("◀️ Previous", callback_data=f'lang_page_{page-1}'))
        if page < total_pages - 1:
            row.append(InlineKeyboardButton("Next ▶️", callback_data=f'lang_page_{page+1}'))
        if row:
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton("🔙 Back", callback_data='view_languages')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(response, reply_markup=reply_markup)
    
    elif data == 'help_menu':
        await help_command(update, context)
    
    elif data == 'main_menu':
        await start_command(update, context)

# ==================== ERROR HANDLER ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors."""
    logger.error(f"Update {update} caused error {context.error}")
    
    try:
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An unexpected error occurred. Please try again later."
            )
    except Exception as e:
        logger.error(f"Error in error handler: {e}")

# ==================== MAIN FUNCTION ====================

def main() -> None:
    """Start the bot."""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    
    if not token:
        logger.error("❌ TELEGRAM_BOT_TOKEN environment variable not set!")
        logger.error("Please set it in Railway environment variables.")
        logger.error("Go to Railway Dashboard → Variables → Add Variable")
        logger.error("Key: TELEGRAM_BOT_TOKEN, Value: <your-token-from-BotFather>")
        sys.exit(1)
    
    logger.info("🚀 Starting LingoGlobal Bot...")
    logger.info(f"✅ TELEGRAM_BOT_TOKEN found (length: {len(token)} characters)")
    
    try:
        application = ApplicationBuilder() \
            .token(token) \
            .build()
        
        application.add_handler(CommandHandler("start", start_command))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("about", about_command))
        application.add_handler(CommandHandler("translate", translate_command))
        application.add_handler(CommandHandler("detect", detect_command))
        application.add_handler(CommandHandler("languages", languages_command))
        application.add_handler(CommandHandler("lang", lang_command))
        application.add_handler(CommandHandler("quick", quick_command))
        application.add_handler(CommandHandler("setlang", setlang_command))
        
        application.add_handler(CallbackQueryHandler(button_callback))
        
        application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
        )
        
        application.add_error_handler(error_handler)
        
        logger.info("✅ Bot started successfully! Press Ctrl+C to stop.")
        application.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        raise

if __name__ == '__main__':
    main()

# 📄 bot.py (Updated for python-telegram-bot v20+)
import logging
import os
import telegram
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, Defaults
import google.generativeai as genai
import requests
import pytz
from config import Config

# === API Keys and Telegram Bot Token ===
GEMINI_API_KEY = Config.GEMINI_API_KEY
TELEGRAM_TOKEN = Config.TELEGRAM_TOKEN
DEEPSEEK_API_KEY = Config.DEEPSEEK_API_KEY

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

# Configure Gemini API
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

def gemini_pro_response(prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error in Gemini API: {e}")
        return "Waan ka xumahay, waxaanan awoodin inaan ka jawaabo hadda. Fadlan isku day mar kale."

def deepseek_pro_response(prompt):
    if not DEEPSEEK_API_KEY:
        logger.error("Deepseek API key not found in config.")
        return "Waan ka xumahay, Deepseek AI lama heli karo hadda. Fadlan dib ugu noqo later."
    
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat", # Or another appropriate Deepseek model
        "messages": [{"role": "user", "content": prompt}],
        "stream": False
    }
    try:
        response = requests.post("https://api.deepseek.com/chat/completions", headers=headers, json=payload)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
        return response.json()["choices"][0]["message"]["content"]
    except requests.exceptions.RequestException as e:
        logger.error(f"Error in Deepseek API request: {e}")
        return "Waan ka xumahay, Deepseek AI waxa ay la kulantay cilad. Fadlan isku day mar kale."
    except KeyError as e:
        logger.error(f"Deepseek API response format error: {e}")
        return "Waan ka xumahay, Deepseek AI waxa ay la kulantay cilad. Fadlan isku day mar kale."

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    buttons = [
        ["👨‍💻 Talk Human", "🤖 Talk Bot"],
        ["🛂 Contacts", "❓ More Info"],
        ["☘️ Ibara AI", "📺 Channels & Posts"]
    ]
    
    welcome_text = f"""
🎉 **Welcome {user.first_name}!**

🤖 **SomalibotMaster AI Bot** waa diyaar!
🎯 **Features:**
• AI Chat (Gemini & DeepSeek)
• Content Management  
• Multi-Channel Support
• Mini App Integration

💡 **Dooro mid ka mid ah options-ka hoose:**
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons, 
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def talk_to_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """AI Chat Handler"""
    buttons = [
        ["🤖 Talk Gemini", "🤖 Talk Deepseek"],
        ["⛔ Stop AI Chat"]
    ]
    await update.message.reply_text(
        "🤖 **AI Chat Services!**\n"
        "Fadlan dooro adeega AI ee aad rabto inaad isticmaasho:\n\n"
        "• **Gemini AI**: Xoog badan oo iskaashan kara.\n"
        "• **Deepseek AI**: Habboon hawlaha gaarka ah.",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def contacts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show contact information"""
    contacts_text = f"""
📞 **Contact Information:**

🛂 **Telegram:** @Mfaratoon
📧 **Email:** info@somalibotmaster.com
🌐 **Website:** https://somalibotmaster.com

📚 **Learning Channels:**
• @Farsamada - Koorsada Bots
• Somali Podcast - Facebook
• YouTube: Somalibotmaster

📅 **Book Appointment:**
https://calendly.com/somaliboks
    """
    await update.message.reply_text(contacts_text)

async def add_channel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Add Your Channel menu option"""
    context.user_data['adding_channel'] = True
    await update.message.reply_text(
        "➕ **Ku dar Channel-kaaga**\n\n"
        "Fadlan ii soo dir **channel ID**-ga ama **username**-ka channelka aad rabto inaad ku darto.\n"
        "Tusaale: `@my_channel` ama `-1001234567890`\n\n"
        "*Si aad u hesho channel ID, waxaad isticmaali kartaa bots kale sida @getidsbot.*"
    )

async def text_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Text Post creation"""
    context.user_data['creating_text_post'] = True
    await update.message.reply_text(
        "✍️ **Qor Qoraalkaaga**\n\n"
        "Fadlan soo geli qoraalka aad rabto inaad dirto."
    )

async def media_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Media Post creation"""
    context.user_data['creating_media_post'] = True
    await update.message.reply_text(
        "🖼️ **Ku dar Media-gaaga**\n\n"
        "Fadlan ii soo dir sawir, video gaaban (round video), file (ilaa 5MB), GIF, sticker, ama audio file aad rabto inaad dirto.\n"
        "*Fiican: Video-yada caadiga ah lama ogola.*"
    )

async def link_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Link Post creation"""
    context.user_data['creating_link_post'] = True
    await update.message.reply_text(
        "🔗 **Ku dar Link-gaaga**\n\n"
        "Fadlan soo geli URL-ka aad rabto inaad dirto, waxaad kaloo ku dari kartaa qoraal gaaban.\n"
        "Tusaale: `https://example.com Kani waa link tusaale ah.`"
    )

async def create_posts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Create Posts menu option"""
    buttons = [
        ["✍️ Text Post", "🖼️ Media Post"],
        ["🔗 Link Post"],
        ["⬅️ Back to Channels & Posts"]
    ]
    create_posts_text = """
📝 **Create New Post**

Maxaad dooneysaa inaad dirto?
    """
    await update.message.reply_text(
        create_posts_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def channels_posts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Channels & Posts menu option"""
    buttons = [
        ["➕ Add Your Channel"],
        ["📝 Create Posts"],
        ["🔄 Multipost"],
        ["🔒 Protected Content"],
        ["⚙️ Settings"],
        ["📮 My Posts"],
        ["💾 Saved Posts"],
        ["⬅️ Back to Main Menu"]
    ]
    channels_posts_text = """
👋 **Channels & Posts Management**

Dooro mid ka mid ah doorashooyinka hoose si aad u maamusho channelada iyo qoraalada.
    """
    await update.message.reply_text(
        channels_posts_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def confirm_send_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Confirm & Send Post button"""
    post_text = context.user_data.pop('current_post_text', None)
    link_url = context.user_data.pop('current_link_url', None)
    media_file_id = context.user_data.pop('current_media_file_id', None)
    media_type = context.user_data.pop('current_media_type', None)
    
    if post_text:
        await update.message.reply_text(f"✅ Qoraalkaaga: '{post_text}' waa la diray!")
    elif link_url:
        await update.message.reply_text(f"✅ Link-gaaga: '{link_url}' waa la diray!")
    elif media_file_id and media_type:
        await update.message.reply_text(f"✅ {media_type.capitalize() if media_type else 'Media'}-gaaga waa la diray!")
    else:
        await update.message.reply_text("Waan ka xumahay, ma jiro qoraal la diro.")
    
    await create_posts_handler(update, context)

async def cancel_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Cancel Post button"""
    context.user_data.pop('current_post_text', None)
    context.user_data.pop('current_link_url', None)
    context.user_data.pop('current_media_file_id', None)
    context.user_data.pop('current_media_type', None)
    context.user_data.pop('current_media_caption', None)
    context.user_data['creating_text_post'] = False
    context.user_data['creating_media_post'] = False
    context.user_data['creating_link_post'] = False

    await update.message.reply_text("❌ Post-ka waa la joojiyay.")
    await create_posts_handler(update, context)

async def preview_post_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Preview Post button"""
    post_text = context.user_data.get('current_post_text')
    link_url = context.user_data.get('current_link_url')
    media_file_id = context.user_data.get('current_media_file_id')
    media_type = context.user_data.get('current_media_type')

    temp_multipost_item = context.user_data.get('temp_multipost_item')
    if temp_multipost_item:
        post_type = temp_multipost_item.get('type')
        if post_type == 'text':
            post_text = temp_multipost_item.get('text_post')
            await update.message.reply_text(f"👁️ **Halkan waa preview-ga Multipost qoraalkaaga:**\n\n```\n{post_text}\n```")
        elif post_type == 'link':
            link_url = temp_multipost_item.get('link_post')
            await update.message.reply_text(f"👁️ **Halkan waa preview-ga Multipost link-gaaga:**\n\n```\n{link_url}\n```")
        elif post_type == 'media':
            media_data = temp_multipost_item.get('media_post', {})
            media_file_id = media_data.get('file_id')
            media_type = media_data.get('type')
            caption = media_data.get('caption', '')
            
            if media_file_id and media_type:
                if media_type == 'photo':
                    await update.message.reply_photo(media_file_id, caption=caption)
                elif media_type == 'document':
                    await update.message.reply_document(media_file_id, caption=caption)
                elif media_type == 'audio':
                    await update.message.reply_audio(media_file_id, caption=caption)
                elif media_type == 'animation':
                    await update.message.reply_animation(media_file_id, caption=caption)
                elif media_type == 'sticker':
                    await update.message.reply_sticker(media_file_id)
                elif media_type == 'video_note':
                    await update.message.reply_video_note(media_file_id)
                elif media_type == 'voice':
                    await update.message.reply_voice(media_file_id)
                await update.message.reply_text(f"👁️ **Halkan waa preview-ga Multipost {media_type.capitalize() if media_type else 'Media'}-gaaga.**")
            else:
                await update.message.reply_text("Ma jiro wax media ah oo la daawado Multipost-ka.")
    elif post_text:
        await update.message.reply_text(f"👁️ **Halkan waa preview-ga qoraalkaaga:**\n\n```\n{post_text}\n```")
    elif link_url:
        await update.message.reply_text(f"👁️ **Halkan waa preview-ga link-gaaga:**\n\n```\n{link_url}\n```")
    elif media_file_id and media_type:
        caption = context.user_data.get('current_media_caption', '')
        if media_type == 'photo':
            await update.message.reply_photo(media_file_id, caption=caption)
        elif media_type == 'document':
            await update.message.reply_document(media_file_id, caption=caption)
        elif media_type == 'audio':
            await update.message.reply_audio(media_file_id, caption=caption)
        elif media_type == 'animation':
            await update.message.reply_animation(media_file_id, caption=caption)
        elif media_type == 'sticker':
            await update.message.reply_sticker(media_file_id)
        elif media_type == 'video_note':
            await update.message.reply_video_note(media_file_id)
        elif media_type == 'voice':
            await update.message.reply_voice(media_file_id)
        await update.message.reply_text(f"👁️ **Halkan waa preview-ga {media_type.capitalize() if media_type else 'Media'}-gaaga.**")
    else:
        await update.message.reply_text("Ma jiro wax la daawado.")

async def settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Settings menu option"""
    buttons = [
        ["⚙️ Service Messages"],
        ["⭐ Favorite Settings Sets"],
        ["👍 Default Reactions"],
        ["📌 Favorite Buttons Set"],
        ["📊 Channel Settings"],
        ["📎 Enable Attached Link"],
        ["✍️ Signature"],
        ["👋 Welcome Message"],
        ["⬅️ Back to Channels & Posts"]
    ]
    settings_text = """
⚙️ **Bot Settings**

Configure various aspects of your bot.
    """
    await update.message.reply_text(
        settings_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def enable_protected_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['protected_content_enabled'] = True
    await update.message.reply_text("🛡️ Content Protection waa la shiday (for channels where bot is admin).")
    await protected_content_handler(update, context)

async def disable_protected_content(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['protected_content_enabled'] = False
    await update.message.reply_text("🔓 Content Protection waa la damiyay.")
    await protected_content_handler(update, context)

async def protected_content_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle Protected Content menu option"""
    buttons = [
        ["🛡️ Enable Protected Content"],
        ["🔓 Disable Protected Content"],
        ["⬅️ Back to Channels & Posts"]
    ]
    protected_content_text = """
🔒 **Protected Content Management**

Configure options to prevent media copying and forwarding.
Status: {}
    """.format("🛡️ Enabled" if context.user_data.get('protected_content_enabled', False) else "🔓 Disabled")
    await update.message.reply_text(
        protected_content_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def add_to_multipost_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    temp_post_data = context.user_data.pop('temp_multipost_item', None)

    if temp_post_data:
        if 'scheduled_multiposts' not in context.user_data:
            context.user_data['scheduled_multiposts'] = []
        context.user_data['scheduled_multiposts'].append(temp_post_data)
        await update.message.reply_text("✅ Post-ka waa lagu daray Multipost-ka!")
    else:
        await update.message.reply_text("Waan ka xumahay, ma jiro post la diro.")
    
    context.user_data['multipost_post_creation_active'] = False
    context.user_data.pop('current_post_type', None)
    await multipost_handler(update, context)

async def cancel_multipost_item_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.pop('temp_multipost_item', None)
    context.user_data['multipost_post_creation_active'] = False
    context.user_data.pop('current_post_type', None)
    await update.message.reply_text("❌ Post-ka waa la joojiyay.")
    await multipost_handler(update, context)

async def add_new_multipost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['multipost_active'] = True 
    await create_posts_handler(update, context) 

async def view_multiposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('scheduled_multiposts'):
        text = "📋 **Scheduled Multiposts:**\n\n"
        for i, post in enumerate(context.user_data['scheduled_multiposts'], 1):
            text += f"{i}. {post['type'].capitalize()} Post: {post['text_post'] if post['type'] == 'text' else post['link_post']}\n"
        await update.message.reply_text(text)
    else:
        await update.message.reply_text("Waan ka xumahay, ma jiro Multipost-ka waa la helay.")

async def send_all_multiposts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('scheduled_multiposts'):
        for post_data in context.user_data['scheduled_multiposts']:
            post_type = post_data['type']
            if post_type == 'text':
                await update.message.reply_text(f"Sending Text Post: {post_data['text_post']}")
            elif post_type == 'link':
                await update.message.reply_text(f"Sending Link Post: {post_data['link_post']}")
            elif post_type == 'media':
                media_post_data = post_data['media_post']
                media_type = media_post_data['type']
                caption = media_post_data['caption']
                if media_type == 'photo':
                    await update.message.reply_photo(media_post_data['file_id'], caption=caption)
                elif media_type == 'document':
                    await update.message.reply_document(media_post_data['file_id'], caption=caption)
                elif media_type == 'audio':
                    await update.message.reply_audio(media_post_data['file_id'], caption=caption)
                elif media_type == 'animation':
                    await update.message.reply_animation(media_post_data['file_id'], caption=caption)
                elif media_type == 'sticker':
                    await update.message.reply_sticker(media_post_data['file_id'])
                elif media_type == 'video_note':
                    await update.message.reply_video_note(media_post_data['file_id'])
                elif media_type == 'voice':
                    await update.message.reply_voice(media_post_data['file_id'])
        await update.message.reply_text("✅ All Multiposts sent!")
        context.user_data['scheduled_multiposts'] = [] 
    else:
        await update.message.reply_text("Waan ka xumahay, ma jiro Multipost-ka waa la helay.")

async def cancel_multipost_creation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['multipost_active'] = False
    context.user_data['scheduled_multiposts'] = []
    await update.message.reply_text("❌ Multipost creation cancelled.")
    await channels_posts_handler(update, context)

async def multipost_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["➕ Add New Post"],
        ["👀 View Posts"],
        ["🚀 Send All"],
        ["✖️ Cancel Multipost"],
        ["⬅️ Back to Channels & Posts"]
    ]
    multipost_text = """
🔄 **Multipost Management**

Abuur oo jadwal dhawr qoraal ah markiiba.
    """
    await update.message.reply_text(
        multipost_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def service_messages_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⚙️ **Service Messages Settings** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def favorite_settings_sets_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⭐ **Favorite Settings Sets** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def default_reactions_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👍 **Default Reactions Settings** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def favorite_buttons_set_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📌 **Favorite Buttons Set** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def channel_settings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["➡️ Move Channel", "🔄 Override Channel", "🗑️ Remove Channel"],
        ["⬅️ Back to Settings"]
    ]
    await update.message.reply_text(
        "📊 **Channel Settings**\n\nConfigure individual channel settings.",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def enable_attached_link_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📎 **Enable Attached Link** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def signature_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✍️ **Signature Settings** (Placeholder)")
    await update.message.reply_text("⬅️ Back to Settings",
        reply_markup=ReplyKeyboardMarkup(
            [["⬅️ Back to Settings"]],
            resize_keyboard=True,
            one_time_keyboard=False
        )
    )

async def welcome_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["📝 Welcome Post", "✅ Self-Approval"],
        ["🤖 Captcha", "🚫 Force Join"],
        ["⬅️ Back to Settings"]
    ]
    await update.message.reply_text(
        "👋 **Welcome Message Settings**\n\nConfigure welcome features for private channels.",
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def my_posts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["👀 View My Posts"],
        ["✏️ Edit My Posts"],
        ["⬅️ Back to Channels & Posts"]
    ]
    my_posts_text = """
📮 **My Posts Management**

View or edit your saved posts.
    """
    await update.message.reply_text(
        my_posts_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def saved_posts_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        ["👀 View Saved Posts"],
        ["✏️ Edit Saved Posts"],
        ["⬅️ Back to Channels & Posts"]
    ]
    saved_posts_text = """
💾 **Saved Posts Management**

View or edit your saved posts.
    """
    await update.message.reply_text(
        saved_posts_text,
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True,
            one_time_keyboard=False
        ),
        parse_mode='Markdown'
    )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all text messages"""
    text = update.message.text
    
    if text == "👨‍💻 Talk Human":
        await update.message.reply_text(
            "📞 **Contact Human Support:**\n"
            "Telegram: @Mfaratoon\n"
            "Calendar: https://calendly.com/somaliboks\n\n"
            "💡 *Fadlan:* Scientific inquiries to bot, "
            "other questions direct contact."
        )
    
    elif text == "🤖 Talk Bot":
        await talk_to_bot(update, context)
    
    elif text == "🤖 Talk Gemini":
        context.user_data['ai_chat_active'] = True
        context.user_data['current_ai_model'] = 'gemini'
        buttons = [["⛔ Stop AI Chat"]]
        await update.message.reply_text(
            "🤖 **Gemini AI Selected!**\nMaxaan ku caawin karaa?",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )

    elif text == "🤖 Talk Deepseek":
        context.user_data['ai_chat_active'] = True
        context.user_data['current_ai_model'] = 'deepseek'
        buttons = [["⛔ Stop AI Chat"]]
        await update.message.reply_text(
            "🤖 **Deepseek AI Selected!**\nMaxaan ku caawin karaa?",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
    
    elif text == "⛔ Stop AI Chat":
        context.user_data['ai_chat_active'] = False
        context.user_data.pop('current_ai_model', None)
        buttons = [
            ["👨‍💻 Talk Human", "🤖 Talk Bot"],
            ["🛂 Contacts", "❓ More Info"],
            ["☘️ Ibara AI", "📺 Channels & Posts"]
        ]
        await update.message.reply_text(
            "🚫 **AI Chat Deactivated!**\nFadlan dooro ikhtiyaarkaaga.",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True,
                one_time_keyboard=False
            )
        )
    
    elif text == "🛂 Contacts":
        await contacts_handler(update, context)
    
    elif text == "❓ More Info":
        await update.message.reply_text(
            "📚 **More Information:**\n\n"
            "🎓 **Courses Available:**\n"
            "• Telegram Bot Development\n"
            "• AI Integration\n"
            "• Automation Systems\n\n"
            "🔗 **Follow us on:**\n"
            "YouTube, Facebook, Telegram Channels\n\n"
            "💼 **Professional Somali LLM Development**"
        )
    
    elif text == "📺 Channels & Posts":
        await channels_posts_handler(update, context)
    
    elif text == "⬅️ Back to Main Menu":
        await start_command(update, context)

    elif text == "➕ Add Your Channel":
        await add_channel_handler(update, context)

    elif text == "📝 Create Posts":
        await create_posts_handler(update, context)

    elif text == "⬅️ Back to Channels & Posts":
        await channels_posts_handler(update, context)

    elif text == "✍️ Text Post":
        if context.user_data.get('multipost_active'):
            context.user_data['multipost_post_creation_active'] = True
            context.user_data['current_post_type'] = 'text'
            await update.message.reply_text("✍️ **Qor qoraalka post-ka (Multipost):**")
        else:
            await text_post_handler(update, context)

    elif text == "🖼️ Media Post":
        if context.user_data.get('multipost_active'):
            context.user_data['multipost_post_creation_active'] = True
            context.user_data['current_post_type'] = 'media'
            await update.message.reply_text("🖼️ **U soo dir media-ga post-ka (Multipost):**")
        else:
            await media_post_handler(update, context)

    elif text == "🔗 Link Post":
        if context.user_data.get('multipost_active'):
            context.user_data['multipost_post_creation_active'] = True
            context.user_data['current_post_type'] = 'link'
            await update.message.reply_text("🔗 **U soo dir URL-ka post-ka (Multipost):**")
        else:
            await link_post_handler(update, context)

    elif text == "✅ Confirm & Send":
        await confirm_send_post_handler(update, context)
    
    elif text == "❌ Cancel Post":
        await cancel_post_handler(update, context)

    elif text == "👁️ Preview Post":
        await preview_post_handler(update, context)

    elif text == "➕ Add New Post":
        await add_new_multipost(update, context)

    elif text == "👀 View Posts":
        await view_multiposts(update, context)

    elif text == "🚀 Send All":
        await send_all_multiposts(update, context)

    elif text == "✖️ Cancel Multipost":
        await cancel_multipost_creation(update, context)

    elif text == "✅ Add to Multipost":
        await add_to_multipost_confirm_handler(update, context)

    elif text == "❌ Cancel Current Post":
        await cancel_multipost_item_handler(update, context)

    elif text == "🔒 Protected Content":
        await protected_content_handler(update, context)

    elif text == "🛡️ Enable Protected Content":
        await enable_protected_content(update, context)

    elif text == "🔓 Disable Protected Content":
        await disable_protected_content(update, context)

    elif text == "⚙️ Settings":
        await settings_handler(update, context)

    elif text == "⚙️ Service Messages":
        await service_messages_handler(update, context)

    elif text == "⭐ Favorite Settings Sets":
        await favorite_settings_sets_handler(update, context)

    elif text == "👍 Default Reactions":
        await default_reactions_handler(update, context)

    elif text == "📌 Favorite Buttons Set":
        await favorite_buttons_set_handler(update, context)

    elif text == "📊 Channel Settings":
        await channel_settings_handler(update, context)
        
    elif text == "📎 Enable Attached Link":
        await enable_attached_link_handler(update, context)

    elif text == "✍️ Signature":
        await signature_handler(update, context)

    elif text == "👋 Welcome Message":
        await welcome_message_handler(update, context)

    elif text == "⬅️ Back to Settings":
        await settings_handler(update, context)

    elif text == "📮 My Posts":
        await my_posts_handler(update, context)

    elif text == "💾 Saved Posts":
        await update.message.reply_text("💾 **Saved Posts Management** (Placeholder)")
        await channels_posts_handler(update, context)

    elif text == "👀 View My Posts":
        await update.message.reply_text("👀 **Your Posts** (Placeholder for viewing posts)")
        await my_posts_handler(update, context)

    elif text == "✏️ Edit My Posts":
        await update.message.reply_text("✏️ **Edit Your Posts** (Placeholder for editing posts)")
        await my_posts_handler(update, context)

    elif text == "⬅️ Back to My Posts":
        await my_posts_handler(update, context)
        
    elif text == "👀 View Saved Posts":
        await update.message.reply_text("👀 **Your Saved Posts** (Placeholder for viewing saved posts)")
        await saved_posts_handler(update, context)

    elif text == "✏️ Edit Saved Posts":
        await update.message.reply_text("✏️ **Edit Your Saved Posts** (Placeholder for editing posts)")
        await saved_posts_handler(update, context)

    elif text == "⬅️ Back to Channels & Posts":
        await channels_posts_handler(update, context)

    elif context.user_data.get('adding_channel') and text:
        channel_identifier = text.strip()
        if channel_identifier:
            await update.message.reply_text(
                f"Channel-ka '{channel_identifier}' waa la helay. Waanu baadhi doonaa."
            )
            context.user_data['adding_channel'] = False
        else:
            await update.message.reply_text("Fadlan soo geli channel ID ama username sax ah.")
        await channels_posts_handler(update, context)

    elif (text and (context.user_data.get('creating_text_post') or 
         (context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'text'))):
        post_text = text
        if context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'text':
            context.user_data['temp_multipost_item'] = {'type': 'text', 'text_post': post_text}
            context.user_data['multipost_post_creation_active'] = False
            buttons = [
                ["✅ Add to Multipost", "❌ Cancel Current Post"],
                ["👁️ Preview Current Post"]
            ]
            await update.message.reply_text(
                f"Qoraalkaaga Multipost-ka waa diyaar: \n\n```\n{post_text}\n```\n\nMaxaad dooneysaa inaad sameyso?",
                reply_markup=ReplyKeyboardMarkup(
                    buttons,
                    resize_keyboard=True,
                    one_time_keyboard=False
                ),
                parse_mode='Markdown'
            )
        else:
            context.user_data['current_post_text'] = post_text
            context.user_data['creating_text_post'] = False
            buttons = [
                ["✅ Confirm & Send", "❌ Cancel Post"],
                ["👁️ Preview Post"]
            ]
            await update.message.reply_text(
                f"Qoraalkaagu waa diyaar: \n\n```\n{post_text}\n```\n\nMaxaad dooneysaa inaad sameyso?",
                reply_markup=ReplyKeyboardMarkup(
                    buttons,
                    resize_keyboard=True,
                    one_time_keyboard=False
                ),
                parse_mode='Markdown'
            )

    elif (text and (context.user_data.get('creating_link_post') or 
          (context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'link'))):
        link_url = text
        if context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'link':
            context.user_data['temp_multipost_item'] = {'type': 'link', 'link_post': link_url}
            context.user_data['multipost_post_creation_active'] = False
            buttons = [
                ["✅ Add to Multipost", "❌ Cancel Current Post"],
                ["👁️ Preview Current Post"]
            ]
            await update.message.reply_text(
                f"Link-gaagu Multipost-ka waa diyaar: \n\n```\n{link_url}\n```\n\nMaxaad dooneysaa inaad sameyso?",
                reply_markup=ReplyKeyboardMarkup(
                    buttons,
                    resize_keyboard=True,
                    one_time_keyboard=False
                ),
                parse_mode='Markdown'
            )
        else:
            context.user_data['current_link_url'] = link_url
            context.user_data['creating_link_post'] = False
            buttons = [
                ["✅ Confirm & Send", "❌ Cancel Post"],
                ["👁️ Preview Post"]
            ]
            await update.message.reply_text(
                f"Link-gaagu waa diyaar: \n\n```\n{link_url}\n```\n\nMaxaad dooneysaa inaad sameyso?",
                reply_markup=ReplyKeyboardMarkup(
                    buttons,
                    resize_keyboard=True,
                    one_time_keyboard=False
                ),
                parse_mode='Markdown'
            )
    
    # Handle Media (Check for media without specific text command)
    elif (context.user_data.get('creating_media_post') or 
          (context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'media')):
        # Media handling in message_handler should check for persistence of non-text updates
        # But this handler is filtered for TEXT usually...
        # Wait, if I set filter to ALL, then text might be None.
        # Logic here for media...
        pass 
        # Since this 'message_handler' will be attached to filters.ALL, this block needs to be outside the 'if text:' block or handle None text.
        # See below for separate media handling logic.

    else:
        # Default AI response for text messages
        if context.user_data.get('ai_chat_active') and text:
            current_ai_model = context.user_data.get('current_ai_model', 'gemini')
            ai_response = ""
            if current_ai_model == 'gemini':
                ai_response = gemini_pro_response(text)
            elif current_ai_model == 'deepseek':
                ai_response = deepseek_pro_response(text)
            await update.message.reply_text(ai_response)
        elif text:
            await update.message.reply_text(
                "🤖 Waan ku fahmay...\n"
                "Hada AI service-ka waa la diyaariyayaa.\n"
                "Fadlan isticmaal buttons-ka kor ku yaal."
            )

async def global_media_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Separate handler for media uploads"""
    if context.user_data.get('creating_media_post') or (context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'media'):
        media_file_id = None
        media_type = None
        caption = None

        if update.message.photo:
            media_file_id = update.message.photo[-1].file_id
            media_type = 'photo'
            caption = update.message.caption
        elif update.message.document:
            media_file_id = update.message.document.file_id
            media_type = 'document'
            caption = update.message.caption
        elif update.message.audio:
            media_file_id = update.message.audio.file_id
            media_type = 'audio'
            caption = update.message.caption
        elif update.message.animation:
            media_file_id = update.message.animation.file_id
            media_type = 'animation'
            caption = update.message.caption
        elif update.message.sticker:
            media_file_id = update.message.sticker.file_id
            media_type = 'sticker'
        elif update.message.video_note:
            media_file_id = update.message.video_note.file_id
            media_type = 'video_note'
        elif update.message.voice:
            media_file_id = update.message.voice.file_id
            media_type = 'voice'

        if media_file_id:
            if context.user_data.get('multipost_post_creation_active') and context.user_data.get('current_post_type') == 'media':
                context.user_data['temp_multipost_item'] = {'type': 'media', 'media_post': {'file_id': media_file_id, 'type': media_type, 'caption': caption}}
                context.user_data['multipost_post_creation_active'] = False
                buttons = [
                    ["✅ Add to Multipost", "❌ Cancel Current Post"],
                    ["👁️ Preview Current Post"]
                ]
                await update.message.reply_text(
                    f"🖼️ **Media-gaagu Multipost-ka waa diyaar ({media_type.capitalize() if media_type else 'Media'}):**\n\nMaxaad dooneysaa inaad sameyso?",
                    reply_markup=ReplyKeyboardMarkup(
                        buttons,
                        resize_keyboard=True,
                        one_time_keyboard=False
                    ),
                    parse_mode='Markdown'
                )
            else:
                context.user_data['current_media_file_id'] = media_file_id
                context.user_data['current_media_type'] = media_type
                context.user_data['current_media_caption'] = caption
                context.user_data['creating_media_post'] = False

                buttons = [
                    ["✅ Confirm & Send", "❌ Cancel Post"],
                    ["👁️ Preview Post"]
                ]
                await update.message.reply_text(
                    f"🖼️ **Media-gaagu waa diyaar ({media_type.capitalize() if media_type else 'Media'}):**\n\nMaxaad dooneysaa inaad sameyso?",
                    reply_markup=ReplyKeyboardMarkup(
                        buttons,
                        resize_keyboard=True,
                        one_time_keyboard=False
                    ),
                    parse_mode='Markdown'
                )
        else:
            await update.message.reply_text(
                "Waan ka xumahay, ma aqoonsan karo nooca media-gaas. Fadlan isku day file kale (ilaa 5MB) ama isticmaal buttons-ka."
            )
    else:
        # Not expecting media, ignore or handle nicely
        pass

def main():
    """Start the bot"""
    try:
        # Ensure TELEGRAM_TOKEN is not None
        if not TELEGRAM_TOKEN:
            print("TELEGRAM_TOKEN is missing. Please check .env file.")
            return

        # Create Application
        defaults = Defaults(tzinfo=pytz.timezone('UTC'))
        app = Application.builder().token(TELEGRAM_TOKEN).defaults(defaults).build()

        # Add handlers
        app.add_handler(CommandHandler("start", start_command))
        
        # Handler for Media (Photos, Documents, etc.)
        # Important: Add this BEFORE the general text handler if possible, or filter appropriately.
        # We use filters.ATTACHMENT or specific media filters.
        media_filters = (filters.PHOTO | filters.Document.ALL | filters.AUDIO | filters.ANIMATION | filters.Sticker.ALL | filters.VIDEO_NOTE | filters.VOICE)
        app.add_handler(MessageHandler(media_filters, global_media_handler))

        # Handler for Text
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

        # Start bot
        print("SomalibotMaster Bot waa live! (v20+)")
        print("Gali Telegram -> Search bot -> /start")
        app.run_polling()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
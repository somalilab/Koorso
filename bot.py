import os
import sys

try:
	# Required for python-telegram-bot v20+
	from telegram import ReplyKeyboardMarkup, Update
	from telegram.ext import Application, CommandHandler, ContextTypes
except ImportError:
	print("Error: python-telegram-bot is not installed or cannot be imported.")
	print("Install it with: pip install 'python-telegram-bot>=20.0' --upgrade")
	sys.exit(1)

# Ku dar token-kaaga (better to set TOKEN as an environment variable)
TOKEN = os.environ.get("TOKEN", "8089857470:AAFYTis8GLLg005tzw62c-TmXNEAnygScI0")

# Start command (async for PTB v20+)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	buttons = [
		["👨‍💻 Talk Human", "🤖 Talk Bot"],
		["🛂 Contacts", "❓ More Info"]
	]
	reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
	await update.message.reply_text(
		"🎉 Welcome to SomalibotMaster AI!",
		reply_markup=reply_markup
	)

# Main function
def main():
	"""Start the bot."""
	# Create the Application and pass it your bot's token.
	app = Application.builder().token(TOKEN).build()

	# on different commands - answer in Telegram
	app.add_handler(CommandHandler("start", start))

	# Run the bot until the user presses Ctrl-C
	app.run_polling()

if __name__ == "__main__":
	main()
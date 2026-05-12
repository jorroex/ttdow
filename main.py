import logging
import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- SERVIDOR WEB PARA ENGAÑAR A RENDER ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run_web():
    # Render asigna un puerto automáticamente en la variable PORT
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- LÓGICA DEL BOT ---
TELEGRAM_TOKEN = 'TU_TOKEN_AQUÍ'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('🤖 Bot en Render activo.')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_tiktok = update.message.text
    if "tiktok.com" not in url_tiktok: return
    
    msg = await update.message.reply_text("Descargando... ⏳")
    filename = f"{update.message.chat_id}.mp4"
    ydl_opts = {'format': 'best', 'outtmpl': filename, 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_tiktok])
        with open(filename, 'rb') as video:
            await update.message.reply_video(video=video)
        os.remove(filename)
        await msg.delete()
    except Exception as e:
        await msg.edit_text(f"Error: {e}")

# --- EJECUCIÓN ---
if __name__ == '__main__':
    # Iniciamos el servidor web en un hilo aparte
    t = Thread(target=run_web)
    t.start()
    
    # Iniciamos el bot
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.run_polling()

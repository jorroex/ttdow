import logging
import os
import yt_dlp
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from flask import Flask
from threading import Thread

# --- CONFIGURACIÓN DEL SERVIDOR WEB (Para evitar que el hosting se apague) ---
app = Flask('')

@app.route('/')
def home():
    return "El bot está vivo y funcionando 24/7"

def run_web():
    # Render usa la variable PORT automáticamente
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

# --- CONFIGURACIÓN DEL BOT ---
# Aquí leemos la variable que configuraste en el panel (TELEGRAM_TOKEN)
TOKEN = os.environ.get('TELEGRAM_TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🎬 ¡Bienvenido! Envíame un enlace de TikTok y te lo devolveré como video sin marca de agua.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url_tiktok = update.message.text
    
    # Filtro básico para asegurar que sea de TikTok
    if "tiktok.com" not in url_tiktok:
        return

    msg_espera = await update.message.reply_text("Descargando video... esto puede tardar unos segundos. ⏳")

    # Nombre de archivo único usando el ID del chat
    filename = f"video_{update.message.chat_id}.mp4"
    
    ydl_opts = {
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': filename,
        'quiet': True,
        'no_warnings': True,
    }

    try:
        # Descarga el video al servidor
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url_tiktok])

        # Envía el video descargado a Telegram
        if os.path.exists(filename):
            with open(filename, 'rb') as video:
                await update.message.reply_video(
                    video=video, 
                    caption="Aquí tienes tu video descargado exitosamente. ✅"
                )
            
            # Borra el archivo del servidor para no gastar espacio
            os.remove(filename)
            await msg_espera.delete()
        else:
            await msg_espera.edit_text("Error: No se pudo generar el archivo de video.")

    except Exception as e:
        logging.error(f"Error en la descarga: {e}")
        await msg_espera.edit_text("Lo siento, no pude procesar este video. Asegúrate de que el enlace sea público.")

# --- INICIO DEL PROGRAMA ---
if __name__ == '__main__':
    if not TOKEN:
        print("ERROR: No se encontró la variable TELEGRAM_TOKEN en el sistema.")
    else:
        # 1. Iniciar el servidor web en un hilo secundario
        t = Thread(target=run_web)
        t.start()
        
        # 2. Iniciar el bot de Telegram
        application = Application.builder().token(TOKEN).build()
        
        application.add_handler(CommandHandler("start", start))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        print("Servidor web iniciado y Bot de Telegram escuchando...")
        application.run_polling(drop_pending_updates=True)

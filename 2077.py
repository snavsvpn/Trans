import os
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters
)

from deep_translator import GoogleTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0

# ------------------------------
# CONFIGURACIÓN
# ------------------------------
TOKEN = os.getenv("BOT_TOKEN") or "8466421746:AAENWQ0-PqYmonpWmba4BDZnRaC9YS105as"

GRUPOS_PERMITIDOS = {
    -1002935005613,
    -1001757153683
}

translator = GoogleTranslator(source="auto", target="es")

traducciones = {}


# ---------------------------------------
# UTILIDADES
# ---------------------------------------
def grupo_valido(msg):
    return msg and msg.chat_id in GRUPOS_PERMITIDOS


def es_espanol(texto):
    try:
        return detect(texto) == "es"
    except:
        return False


def extraer_texto(msg):
    if msg.text:
        return msg.text.strip()
    if msg.caption:
        return msg.caption.strip()
    return None


def traducir_texto(texto):
    return translator.translate(texto)


# ---------------------------------------
# MANEJAR MENSAJES NUEVOS
# ---------------------------------------
async def manejar_mensaje(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.message or update.channel_post
    if not grupo_valido(msg):
        return

    texto = extraer_texto(msg)
    if not texto:
        return

    if es_espanol(texto):
        return

    resultado = traducir_texto(texto)

    bot_msg = await msg.reply_text(resultado)

    traducciones[msg.message_id] = bot_msg.message_id


# ---------------------------------------
# EDITAR TRADUCCIÓN
# ---------------------------------------
async def editar_traduccion(update: Update, context: ContextTypes.DEFAULT_TYPE):

    msg = update.edited_message or update.edited_channel_post
    if not grupo_valido(msg):
        return

    texto = extraer_texto(msg)
    if not texto:
        return

    original_id = msg.message_id

    if original_id not in traducciones:
        return

    bot_msg_id = traducciones[original_id]

    if es_espanol(texto):
        await context.bot.edit_message_text(
            chat_id=msg.chat_id,
            message_id=bot_msg_id,
            text="(mensaje ahora en español — traducción eliminada)"
        )
        return

    nueva_traduccion = traducir_texto(texto)

    await context.bot.edit_message_text(
        chat_id=msg.chat_id,
        message_id=bot_msg_id,
        text=nueva_traduccion
    )


# ---------------------------------------
# MAIN
# ---------------------------------------
if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()

    # Mensajes normales
    app.add_handler(MessageHandler(
        filters.ALL & ~filters.UpdateType.EDITED_MESSAGE & ~filters.UpdateType.EDITED_CHANNEL_POST,
        manejar_mensaje
    ))

    # Mensajes editados
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, editar_traduccion))
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_CHANNEL_POST, editar_traduccion))

    print("🤖 BOT TRADUCTOR — SOLO TEXTO + CAPTIONS — ACTIVADO ✔")
    app.run_polling()

u    msg = update.edited_message or update.edited_channel_post
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

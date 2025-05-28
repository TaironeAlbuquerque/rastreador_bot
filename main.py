import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ConversationHandler
from flask import Flask, request, jsonify
import threading

# Configuração do logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

# Estados da conversa
MENU, RASTREAR_CPF, SUPORTE = range(3)

# Dados fictícios para rastreamento
dados_rastreamento = {
    "12345678900": [
        {"codigo": "ABC123", "status": "Em trânsito"},
        {"codigo": "DEF456", "status": "Entregue"},
    ],
    "98765432100": [
        {"codigo": "GHI789", "status": "Aguardando envio"},
    ],
}

# Função para gerar dados fictícios
def gerar_dados_ficticios():
    cpfs = ["11122233344", "55566677788", "99988877766"]
    for cpf in cpfs:
        dados_rastreamento[cpf] = []
        for _ in range(random.randint(1, 3)):
            codigo = "".join(random.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=6))
            status = random.choice(["Em trânsito", "Entregue", "Aguardando envio"])
            dados_rastreamento[cpf].append({"codigo": codigo, "status": status})

# Comando /start
async def start(update: Update, context) -> int:
    gerar_dados_ficticios()
    keyboard = [
        [
            InlineKeyboardButton("📦 Rastrear Pedido", callback_data="rastrear"),
            InlineKeyboardButton("🛠️ Suporte", callback_data="suporte"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "Olá! 🤖 Eu sou o *Bot de Atendimento*.\nComo posso ajudá-lo hoje?",
        parse_mode="Markdown",
        reply_markup=reply_markup,
    )
    return MENU

# Manipulador de botões
async def menu(update: Update, context) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "rastrear":
        await query.edit_message_text("Por favor, informe seu CPF para rastrear o pedido:")
        return RASTREAR_CPF
    elif query.data == "suporte":
        await query.edit_message_text("Por favor, descreva sua dúvida ou problema:")
        return SUPORTE

# Função para rastrear pedidos
async def rastrear(update: Update, context) -> int:
    cpf = update.message.text.strip()
    pedidos = dados_rastreamento.get(cpf)
    if pedidos:
        mensagem = f"Pedidos encontrados para o CPF {cpf}:\n"
        for pedido in pedidos:
            mensagem += f"📦 Código: {pedido['codigo']} - Status: {pedido['status']}\n"
    else:
        mensagem = "Nenhum pedido encontrado para o CPF informado."
    await update.message.reply_text(mensagem)
    return ConversationHandler.END

# Função para suporte
async def suporte(update: Update, context) -> int:
    mensagem = update.message.text
    await update.message.reply_text("Obrigado por entrar em contato! Nossa equipe responderá em breve.")
    # Aqui você pode adicionar lógica para enviar a mensagem para um canal ou salvar em um banco de dados
    return ConversationHandler.END

# Comando /cancel
async def cancel(update: Update, context) -> int:
    await update.message.reply_text("Operação cancelada. Volte sempre que precisar!")
    return ConversationHandler.END

# Função principal
def main():
    # Inicializa o aplicativo Flask para manter o serviço ativo no Render
    app = Flask(__name__)

    @app.route('/')
    def home():
        return "Bot está ativo!"

    def run():
        app.run(host='0.0.0.0', port=5000)

    threading.Thread(target=run).start()

    # Inicializa o bot do Telegram
    application = Application.builder().token("SEU_TOKEN_AQUI").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(menu)],
            RASTREAR_CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, rastrear)],
            SUPORTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, suporte)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling()

if __name__ == "__main__":
    main()

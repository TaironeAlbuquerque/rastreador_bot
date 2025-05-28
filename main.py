import logging
import random
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from flask import Flask
import threading

# Configuração do logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Estados da conversa
MENU, RASTREAR_CPF, INSTRUCOES = range(3)

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
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    gerar_dados_ficticios()
    keyboard = [
        [
            InlineKeyboardButton("📦 Rastrear Pedido", callback_data="rastrear"),
            InlineKeyboardButton("📖 Instruções", callback_data="instrucoes"),
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
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    if query.data == "rastrear":
        await query.edit_message_text("Por favor, informe seu CPF para rastrear o pedido:")
        return RASTREAR_CPF
    elif query.data == "instrucoes":
        await query.edit_message_text(
            "📖 *Instruções de Uso:*\n\n"
            "1. Envie /start para iniciar a conversa.\n"
            "2. Escolha entre \"📦 Rastrear Pedido\" ou \"📖 Instruções\".\n"
            "3. Para encerrar a conversa, envie /sair.\n"
            "4. Para reiniciar a conversa, envie qualquer mensagem ou /start.",
            parse_mode="Markdown"
        )
        return MENU

# Função para rastrear pedidos
async def rastrear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    cpf = update.message.text.strip()
    pedidos = dados_rastreamento.get(cpf)
    if pedidos:
        mensagem = f"Pedidos encontrados para o CPF {cpf}:\n"
        for pedido in pedidos:
            mensagem += f"📦 Código: {pedido['codigo']} - Status: {pedido['status']}\n"
    else:
        mensagem = "Nenhum pedido encontrado para o CPF informado."
    await update.message.reply_text(mensagem)
    return MENU

# Comando /sair
async def sair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Operação encerrada. Volte sempre que precisar!")
    return ConversationHandler.END

# Manipulador de mensagens fora da conversa
async def mensagem_fora_conversa(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Olá! Parece que você deseja iniciar uma nova conversa. Envie /start para começar."
    )

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
    application = ApplicationBuilder().token("7304383872:AAH9jS7Vgix9TrgwjDWRBfg1ejgN6haik-0").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            MENU: [CallbackQueryHandler(menu)],
            RASTREAR_CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, rastrear)],
        },
        fallbacks=[CommandHandler("sair", sair)],
        allow_reentry=True,
    )

    application.add_handler(conv_handler)

    # Manipulador para mensagens fora da conversa
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mensagem_fora_conversa))

    application.run_polling()

if __name__ == "__main__":
    main()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

from config import TOKEN
from database import *
from messages import *
from tracking import rastrear_pedido

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Estados da conversa
CADASTRAR_CPF, ADICIONAR_PEDIDO, DESCRICAO_PEDIDO = range(3)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"Olá {user.first_name}!\n\n{mensagem_boas_vindas()}",
        reply_markup=menu_principal()
    )

async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Por favor, digite seu CPF (apenas números) para cadastrar:"
    )
    return CADASTRAR_CPF

async def receber_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cpf = update.message.text
    user = update.effective_user
    
    # Validação simples do CPF
    if not cpf.isdigit() or len(cpf) != 11:
        await update.message.reply_text("CPF inválido. Por favor, digite apenas os 11 números do CPF.")
        return CADASTRAR_CPF
    
    # Verificar se CPF já existe
    if buscar_usuario_por_cpf(cpf):
        await update.message.reply_text("Este CPF já está cadastrado.")
        return ConversationHandler.END
    
    # Adicionar usuário ao banco de dados
    adicionar_usuario(user.id, cpf, user.full_name)
    await update.message.reply_text(
        f"✅ Cadastro realizado com sucesso!\n\nCPF: {cpf}\nNome: {user.full_name}",
        reply_markup=menu_principal()
    )
    return ConversationHandler.END

async def adicionar_pedido_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Por favor, digite o código de rastreio do pedido:"
    )
    return ADICIONAR_PEDIDO

async def receber_codigo_rastreio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    codigo_rastreio = update.message.text.strip()
    context.user_data['codigo_rastreio'] = codigo_rastreio
    
    await update.message.reply_text(
        "Agora, digite uma descrição para este pedido (ex: 'Tênis Nike', 'Livro Python'):"
    )
    return DESCRICAO_PEDIDO

async def receber_descricao_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    descricao = update.message.text
    codigo_rastreio = context.user_data['codigo_rastreio']
    user = update.effective_user
    
    # Adicionar pedido ao banco de dados
    adicionar_pedido(user.id, codigo_rastreio, descricao)
    
    # Verificar status do pedido
    info_rastreio = rastrear_pedido(codigo_rastreio)
    
    await update.message.reply_text(
        f"✅ Pedido adicionado com sucesso!\n\n"
        f"📦 Descrição: {descricao}\n"
        f"📌 Código: {codigo_rastreio}\n"
        f"🔄 Status atual: {info_rastreio['status']}\n\n"
        f"Você pode verificar seus pedidos a qualquer momento com /meuspedidos",
        reply_markup=menu_principal()
    )
    return ConversationHandler.END

async def meus_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    # Buscar CPF do usuário
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT cpf FROM usuarios WHERE user_id = ?', (user.id,))
        resultado = cursor.fetchone()
    
    if not resultado:
        await update.message.reply_text(
            "Você ainda não cadastrou seu CPF. Por favor, use /cadastrar primeiro."
        )
        return
    
    cpf = resultado[0]
    pedidos = buscar_pedidos_por_cpf(cpf)
    
    await update.message.reply_text(
        formatar_lista_pedidos(pedidos),
        reply_markup=menu_principal()
    )

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'add_pedido':
        await query.edit_message_text(
            "Por favor, digite o código de rastreio do pedido:"
        )
        context.user_data['conversation'] = 'add_pedido'
        return ADICIONAR_PEDIDO
    elif query.data == 'meus_pedidos':
        await meus_pedidos(update, context)
    elif query.data == 'ajuda':
        await query.edit_message_text(
            mensagem_ajuda(),
            reply_markup=menu_principal()
        )

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Operação cancelada.",
        reply_markup=menu_principal()
    )
    return ConversationHandler.END

def main():
    # Inicializar banco de dados
    init_db()
    
    # Criar a aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Configurar handlers
    conv_handler_cadastro = ConversationHandler(
        entry_points=[CommandHandler('cadastrar', cadastrar)],
        states={
            CADASTRAR_CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cpf)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )
    
    conv_handler_pedido = ConversationHandler(
        entry_points=[
            CommandHandler('adicionar', adicionar_pedido_cmd),
            CallbackQueryHandler(button_click, pattern='^add_pedido$')
        ],
        states={
            ADICIONAR_PEDIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_codigo_rastreio)],
            DESCRICAO_PEDIDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao_pedido)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)]
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('meuspedidos', meus_pedidos))
    application.add_handler(CommandHandler('ajuda', lambda u, c: u.message.reply_text(mensagem_ajuda())))
    application.add_handler(conv_handler_cadastro)
    application.add_handler(conv_handler_pedido)
    application.add_handler(CallbackQueryHandler(button_click))
    
    # Iniciar o bot
    application.run_polling()

if __name__ == '__main__':
    main()

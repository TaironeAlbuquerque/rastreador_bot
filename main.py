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
from database import *
from messages import *
from tracking import rastrear_pedido
import random
from datetime import datetime, timedelta

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filters=[lambda record: 'token' not in record.getMessage().lower()]
)
logger = logging.getLogger(__name__)

# Estados da conversa
CADASTRAR_CPF, ADICIONAR_PEDIDO, DESCRICAO_PEDIDO = range(3)

# Dados de teste para pré-carregar
TEST_USERS = [
    {"user_id": 123456, "cpf": "11122233344", "nome": "João Silva"},
    {"user_id": 789012, "cpf": "55566677788", "nome": "Maria Souza"},
    {"user_id": 345678, "cpf": "99988877766", "nome": "Carlos Oliveira"}
]

TEST_ORDERS = [
    {"codigo": "AB123456789BR", "descricao": "Tênis Esportivo", "status": "Em trânsito"},
    {"codigo": "CD987654321BR", "descricao": "Livro Python", "status": "Postado"},
    {"codigo": "EF456789123BR", "descricao": "Smartphone", "status": "Entregue"},
    {"codigo": "GH789123456BR", "descricao": "Notebook", "status": "Saiu para entrega"},
    {"codigo": "IJ321654987BR", "descricao": "Fones de Ouvido", "status": "Na unidade de distribuição"}
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        await update.message.reply_text(
            f"Olá {user.first_name}!\n\n{mensagem_boas_vindas()}",
            reply_markup=menu_principal()
        )
    except Exception as e:
        logger.error(f"Error in start: {e}")
        await update.message.reply_text("❌ Ocorreu um erro ao iniciar. Tente novamente.")

async def cadastrar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Por favor, digite seu CPF (apenas números) para cadastrar:"
        )
        return CADASTRAR_CPF
    except Exception as e:
        logger.error(f"Error in cadastrar: {e}")
        await update.message.reply_text("❌ Erro no comando de cadastro.")
        return ConversationHandler.END

async def receber_cpf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        cpf = update.message.text
        user = update.effective_user
        
        if not cpf.isdigit() or len(cpf) != 11:
            await update.message.reply_text("CPF inválido. Por favor, digite apenas os 11 números do CPF.")
            return CADASTRAR_CPF
        
        if buscar_usuario_por_cpf(cpf):
            await update.message.reply_text("Este CPF já está cadastrado.")
            return ConversationHandler.END
        
        adicionar_usuario(user.id, cpf, user.full_name)
        await update.message.reply_text(
            f"✅ Cadastro realizado com sucesso!\n\nCPF: {cpf}\nNome: {user.full_name}",
            reply_markup=menu_principal()
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in receber_cpf: {e}")
        await update.message.reply_text("❌ Erro ao processar CPF.")
        return ConversationHandler.END

async def adicionar_pedido_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Por favor, digite o código de rastreio do pedido:"
        )
        return ADICIONAR_PEDIDO
    except Exception as e:
        logger.error(f"Error in adicionar_pedido_cmd: {e}")
        await update.message.reply_text("❌ Erro no comando de adicionar pedido.")
        return ConversationHandler.END

async def receber_codigo_rastreio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        codigo_rastreio = update.message.text.strip()
        context.user_data['codigo_rastreio'] = codigo_rastreio
        
        await update.message.reply_text(
            "Agora, digite uma descrição para este pedido (ex: 'Tênis Nike', 'Livro Python'):"
        )
        return DESCRICAO_PEDIDO
    except Exception as e:
        logger.error(f"Error in receber_codigo_rastreio: {e}")
        await update.message.reply_text("❌ Erro ao processar código de rastreio.")
        return ConversationHandler.END

async def receber_descricao_pedido(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        descricao = update.message.text
        codigo_rastreio = context.user_data['codigo_rastreio']
        user = update.effective_user
        
        adicionar_pedido(user.id, codigo_rastreio, descricao)
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
    except Exception as e:
        logger.error(f"Error in receber_descricao_pedido: {e}")
        await update.message.reply_text("❌ Erro ao adicionar pedido.")
        return ConversationHandler.END

async def meus_pedidos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user = update.effective_user
        
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
    except Exception as e:
        logger.error(f"Error in meus_pedidos: {e}")
        await update.message.reply_text("❌ Erro ao buscar pedidos.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
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
    except Exception as e:
        logger.error(f"Error in button_click: {e}")
        await query.edit_message_text("❌ Ocorreu um erro. Tente novamente.")

async def cancelar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_text(
            "Operação cancelada.",
            reply_markup=menu_principal()
        )
        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error in cancelar: {e}")
        return ConversationHandler.END

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Tratamento global de erros"""
    try:
        error = context.error
        user = update.effective_user if update else None
        
        logger.error(f"Error for user {user.id if user else 'UNKNOWN'}: {str(error)}", exc_info=error)
        
        if update and update.effective_message:
            await update.effective_message.reply_text(
                "⚠️ Ocorreu um erro inesperado. Nossa equipe foi notificada.\n"
                "Por favor, tente novamente mais tarde."
            )
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")

def carregar_dados_teste():
    """Carrega dados de teste no banco de dados"""
    try:
        for user in TEST_USERS:
            if not buscar_usuario_por_cpf(user['cpf']):
                adicionar_usuario(user['user_id'], user['cpf'], user['nome'])
        
        for order in TEST_ORDERS:
            user = random.choice(TEST_USERS)
            adicionar_pedido(
                user['user_id'],
                order['codigo'],
                order['descricao']
            )
            atualizar_status_pedido(order['codigo'], order['status'])
        
        logger.info("Dados de teste carregados com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar dados de teste: {e}")

def main():
    # Inicializar banco de dados
    init_db()
    
    # Carregar dados de teste
    carregar_dados_teste()
    
    # Criar a aplicação
    application = Application.builder().token(TOKEN).build()
    
    # Configurar handlers
    conv_handler_cadastro = ConversationHandler(
        entry_points=[CommandHandler('cadastrar', cadastrar)],
        states={
            CADASTRAR_CPF: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_cpf)]
        },
        fallbacks=[CommandHandler('cancelar', cancelar)],
        per_message=True
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
        fallbacks=[CommandHandler('cancelar', cancelar)],
        per_message=True
    )
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('meuspedidos', meus_pedidos))
    application.add_handler(CommandHandler('ajuda', lambda u, c: u.message.reply_text(mensagem_ajuda())))
    application.add_handler(conv_handler_cadastro)
    application.add_handler(conv_handler_pedido)
    application.add_handler(CallbackQueryHandler(button_click))
    
    # Adicionar tratamento de erros
    application.add_error_handler(error_handler)
    
    # Iniciar o bot
    application.run_polling()

if __name__ == '__main__':
    main()

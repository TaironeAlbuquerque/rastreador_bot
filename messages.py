from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def mensagem_boas_vindas():
    return (
        "👋 Bem-vindo ao Rastreador de Pedidos!\n\n"
        "Aqui você pode acompanhar todos os seus pacotes em um só lugar.\n\n"
        "Use os comandos abaixo para interagir comigo:\n"
        "/cadastrar - Para cadastrar seu CPF\n"
        "/adicionar - Para adicionar um novo código de rastreio\n"
        "/meuspedidos - Para ver todos os seus pedidos\n"
        "/ajuda - Para obter ajuda"
    )

def menu_principal():
    keyboard = [
        [InlineKeyboardButton("📦 Adicionar Pedido", callback_data='add_pedido')],
        [InlineKeyboardButton("📋 Meus Pedidos", callback_data='meus_pedidos')],
        [InlineKeyboardButton("ℹ️ Ajuda", callback_data='ajuda')]
    ]
    return InlineKeyboardMarkup(keyboard)

def formatar_lista_pedidos(pedidos):
    if not pedidos:
        return "📭 Você não tem nenhum pedido cadastrado."
    
    mensagem = "📦 Seus Pedidos:\n\n"
    for idx, pedido in enumerate(pedidos, 1):
        codigo, descricao, status, data = pedido
        mensagem += (
            f"🔹 Pedido {idx}\n"
            f"📌 Descrição: {descricao}\n"
            f"📦 Código: {codigo}\n"
            f"🔄 Status: {status}\n"
            f"📅 Última atualização: {data}\n\n"
        )
    return mensagem

def mensagem_ajuda():
    return (
        "ℹ️ Ajuda - Rastreador de Pedidos\n\n"
        "Como usar este bot:\n\n"
        "1. Primeiro, cadastre seu CPF usando /cadastrar\n"
        "2. Adicione códigos de rastreio com /adicionar\n"
        "3. Veja todos seus pedidos com /meuspedidos\n\n"
        "O bot irá automaticamente verificar atualizações nos seus pedidos periodicamente."
    )

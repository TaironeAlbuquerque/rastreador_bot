# README - Bot de Rastreio de Pedidos para Telegram

## 📦 Visão Geral

Este é um bot para Telegram desenvolvido em Python que permite aos usuários rastrear seus pedidos associando códigos de rastreio ao seu CPF. O bot oferece uma interface amigável para cadastro, adição de pedidos e consulta de status.

## ✨ Funcionalidades

- ✅ Cadastro de usuários com CPF
- 📦 Adição de códigos de rastreio com descrição
- 🔍 Consulta de todos os pedidos associados a um CPF
- 🔄 Atualização de status dos pedidos
- 📱 Interface intuitiva com menus interativos
- 💾 Armazenamento persistente em banco de dados SQLite

## 🛠️ Pré-requisitos

- Python 3.8 ou superior
- Conta no Telegram e token do BotFather
- Conta no Render (para deploy)

## 🚀 Como Executar Localmente

1. Clone o repositório:
   ```bash
   git clone https://github.com/seu-usuario/rastreador-bot.git
   cd rastreador-bot
   ```

2. Crie e ative um ambiente virtual (recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Crie um arquivo `.env` com seu token do Telegram:
   ```
   TELEGRAM_BOT_TOKEN=seu_token_aqui
   ```

5. Execute o bot:
   ```bash
   python main.py
   ```

## 🌐 Como Deployar no Render

1. Crie um novo serviço Web no Render
2. Conecte ao seu repositório GitHub
3. Configure as variáveis de ambiente:
   - `TELEGRAM_BOT_TOKEN` - Token do seu bot obtido com o BotFather
4. Defina os comandos:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `python main.py`
5. Deploy!

## 🗂️ Estrutura do Projeto

```
/rastreador_bot
├── main.py             # Código principal do bot
├── database.py         # Manipulação do banco de dados
├── messages.py         # Mensagens pré-definidas
├── tracking.py         # Lógica de rastreamento
├── requirements.txt    # Dependências do projeto
├── config.py           # Configurações (API key, etc.)
└── README.md           # Este arquivo
```

## 🤖 Comandos Disponíveis

- `/start` - Inicia o bot e mostra mensagem de boas-vindas
- `/cadastrar` - Inicia o processo de cadastro com CPF
- `/adicionar` - Adiciona um novo código de rastreio
- `/meuspedidos` - Lista todos os pedidos do usuário
- `/ajuda` - Mostra informações de ajuda
- `/cancelar` - Cancela a operação atual

## 🔄 Fluxo de Uso

1. O usuário inicia o bot com `/start`
2. Cadastra seu CPF com `/cadastrar`
3. Adiciona pedidos com `/adicionar`
4. Consulta status com `/meuspedidos`

## 📝 Notas de Implementação

- O módulo de rastreamento atual usa uma implementação simulada
- Para uso em produção, implemente a integração com APIs reais de rastreio
- O banco de dados SQLite é criado automaticamente na primeira execução

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🙋‍♂️ Suporte

Para dúvidas ou problemas, abra uma issue no repositório do projeto.

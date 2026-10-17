import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, CommandHandler, filters

# Carrega as variáveis de ambiente (token do bot)
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Comando simples /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    chat_type = update.effective_chat.type
    
    if chat_type in ["group", "supergroup"]:
        await update.message.reply_text(f"Olá, {user_name}! Salve a todos no grupo {update.effective_chat.title}!")
    else:
        await update.message.reply_text(f"Olá, {user_name}! Estou rodando no chat privado.")

# Função que escuta mensagens de texto comuns no grupo
async def handle_group_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Evita processar mensagens que não venham de texto válido
    if not update.message or not update.message.text:
        return

    chat = update.effective_chat
    user = update.effective_user
    
    # Verifica se a mensagem veio de um grupo ou supergrupo
    if chat.type in ["group", "supergroup"]:
        print(f"[GRUPO: {chat.title} | ID: {chat.id}] Mensagem de {user.first_name} (ID: {user.id}): {update.message.text}")
        
        # Exemplo de lógica: se alguém mandar "preco" ou "preço", o bot responde
        if "preço" in update.message.text.lower() or "preco" in update.message.text.lower():
            await update.message.reply_text(f"Opa, {user.first_name}, quer saber de preços? Em breve trago os dados da API!")

def main():
    # Inicializa a aplicação
    app = ApplicationBuilder().token(TOKEN).build()

    # Registra os handlers
    app.add_handler(CommandHandler("start", start))
    
    # Handler para mensagens de texto (filtra por chats de grupo e supergrupo)
    # IMPORTANTE: Para o bot ler mensagens comuns em grupos, desative o "Group Privacy" no BotFather!
    group_filter = filters.ChatType.GROUPS & filters.TEXT & ~filters.COMMAND
    app.add_handler(MessageHandler(group_filter, handle_group_messages))

    print("Bot rodando em modo de teste para grupos... Pressione Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
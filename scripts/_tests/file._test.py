import os
import ccxt
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, filters

# Carrega as variáveis de ambiente
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Inicializa a exchange para consultas de cripto (ex: Binance)
exchange = ccxt.binance()

# 1. Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    chat_title = update.effective_chat.title or "Chat Privado"
    
    texto = (
        f"Olá, **{user_name}**! 🤖\n"
        f"Estou ativo no grupo **{chat_title}**.\n\n"
        f"**Comandos disponíveis:**\n"
        f"• `/preco BTC` - Consulta o preço atual de uma cripto\n"
        f"• `/relatorio` - Simula o envio de um relatório gerado\n"
        f"• `/status` - Verifica o estado do bot"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

# 2. Comando /preco (Exemplo: /preco btc ou /preco eth)
async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verifica se o usuário digitou o ativo (ex: /preco BTC)
    if not context.args:
        await update.message.reply_text("⚠️ Uso incorreto. Digite por exemplo: `/preco BTC` ou `/preco ETH`", parse_mode="Markdown")
        return

    simbolo = context.args[0].upper() + "/USDT"
    
    try:
        # Busca o ticker na exchange
        ticker = exchange.fetch_ticker(simbolo)
        preco_atual = ticker['last']
        
        await update.message.reply_text(f"📈 O preço atual de **{simbolo}** é **US$ {preco_atual:,.2f}**", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Não foi possível encontrar o ativo `{simbolo}`. Verifique se o par está correto.", parse_mode="Markdown")

# 3. Comando /relatorio (Estrutura pronta para integrar com seus scripts PDF/Excel)
async def relatorio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    await update.message.reply_text(f"📊 Gerando relatório solicitado por {user_name}...")
    
    # Aqui você colocaria a lógica de gerar o PDF/Excel com reportlab/pandas e enviar:
    # Exemplo: await context.bot.send_document(chat_id=update.effective_chat.id, document=open("relatorio.pdf", "rb"))
    
    await update.message.reply_text("✅ Relatório gerado com sucesso! *(Simulação: aqui o bot enviaria o arquivo)*")

# 4. Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Bot operando normalmente na VPS via PM2 e pronto para o grupo!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registra os comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("preco", preco))
    app.add_handler(CommandHandler("relatorio", relatorio))
    app.add_handler(CommandHandler("status", status))

    print("Bot rodando com os novos comandos... Pressione Ctrl+C para parar.")
    app.run_polling()

if __name__ == "__main__":
    main()
import os
import logging
import ccxt
from dotenv import load_dotenv
from telegram import Update
from telegram.error import NetworkError, TimedOut, TelegramError
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler

# Configura o sistema de logs para monitorar a saúde do bot na VPS/PM2
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

exchange = ccxt.binance()

# Função global para capturar erros de rede, timeouts ou sobrecarga
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    """Captura erros inesperados, problemas de conexão e sobrecarga."""
    error = context.error
    logger.error(f"Erro capturado pelo gerenciador: {error}", exc_info=error)

    # Identifica o tipo de problema de conexão ou sobrecarga
    if isinstance(error, (NetworkError, TimedOut)):
        logger.warning("⚠️ Alerta: Detectada instabilidade de rede ou timeout com a API do Telegram.")
    elif isinstance(error, TelegramError):
        logger.error(f"❌ Erro do Telegram: {error}")
    
    # Se houver um update válido associado ao erro, podemos tentar avisar o usuário/grupo
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⚠️ Opa! O bot detectou uma instabilidade momentânea de conexão ou sobrecarga. "
                "Tentando normalizar a operação..."
            )
        except Exception as ex:
            logger.error(f"Não foi possível enviar a mensagem de erro ao chat: {ex}")

# 1. Comando /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    chat_title = update.effective_chat.title or "Chat Privado"
    
    texto = (
        f"Olá, **{user_name}**! 🤖\n"
        f"Estou ativo no grupo **{chat_title}**.\n\n"
        f"• `/preco BTC` - Consulta o preço atual\n"
        f"• `/status` - Verifica o estado da conexão"
    )
    await update.message.reply_text(texto, parse_mode="Markdown")

# 2. Comando /preco com tratamento local de sobrecarga/timeout na API externa
async def preco(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Uso incorreto. Digite: `/preco BTC`", parse_mode="Markdown")
        return

    simbolo = context.args[0].upper() + "/USDT"
    
    try:
        # Define um timeout explícito caso a exchange demore a responder
        ticker = exchange.fetch_ticker(simbolo)
        preco_atual = ticker['last']
        await update.message.reply_text(f"📈 Preço de **{simbolo}**: **US$ {preco_atual:,.2f}**", parse_mode="Markdown")
    
    except ccxt.NetworkError:
        logger.warning(f"Falha de conexão com a exchange ao buscar {simbolo}")
        await update.message.reply_text("⚠️ O servidor de criptomoedas está demorando para responder (Sobrecarga/Timeout de rede). Tente novamente em instantes.")
    except ccxt.ExchangeError:
        await update.message.reply_text(f"❌ O ativo `{simbolo}` não foi encontrado.")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        await update.message.reply_text("❌ Ocorreu um erro inesperado ao processar sua cotação.")

# 3. Comando /status
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🟢 Conexão estável. Bot operando normalmente na VPS!")

def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # Registra os comandos
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("preco", preco))
    app.add_handler(CommandHandler("status", status))

    # REGISTRA O GERENCIADOR DE ERROS (Essencial para sobrecarga e queda de conexão)
    app.add_error_handler(error_handler)

    print("Bot rodando com monitoramento de erros e conexão... Pressione Ctrl+C para parar.")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
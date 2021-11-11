# despues de instarlo hay que hacer un Restart del RUNTIME para que funcione correctamente
# !pip install python-telegram-bot


# https://www.youtube.com/watch?v=i3ExsxpFOZ8 para terminar de configurar el docker y heroku
# https://dashboard.heroku.com/apps/precios-dolar-ambito-bot/settings perez.moleroc@gmail.com argentina.19

def generar_string_dolares():
    # https://curlconverter.com/#
    import requests

    headers = {
        'sec-ch-ua': '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
        'Accept': '*/*',
        'Referer': 'https://www.ambito.com/',
        'sec-ch-ua-mobile': '?0',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
        'sec-ch-ua-platform': '"Windows"',
    }

    response_informal = requests.get('https://mercados.ambito.com//dolar/informal/variacion', headers=headers)
    response_turista = requests.get('https://mercados.ambito.com//dolarturista/variacion', headers=headers)
    response_oficial = requests.get('https://mercados.ambito.com//dolar/oficial/variacion', headers=headers)

    responses = [response_informal, response_oficial, response_turista]


    data_dict = {
        "dolar": ["informal", "oficial", "turista"],
        "venta": [],
        "promedio": [],
        "compra": [],
        "variacion":[],
        "fecha": [],
        "hora": []
    }
    for response in responses:
        resp = response.json()
        venta = float(resp["venta"].replace(",","."))
        compra = float(resp["compra"].replace(",","."))
        promedio = (venta + compra) / 2.00
        data_dict["venta"].append(venta)
        data_dict["compra"].append(compra)
        data_dict["promedio"].append(promedio)
        data_dict["variacion"].append(float(resp["variacion"][:-1].replace(",",".")))
        data_dict["fecha"].append(resp["fecha"].split("-")[0].strip().replace("/", "-"))
        data_dict["hora"].append(resp["fecha"].split("-")[1].strip())

    texto_a_enviar = f"""
<b>Dolar informal (Blue):</b>
    <b>Venta:</b>     {data_dict["venta"][0]} ARS
    <b>Compra:</b>    {data_dict["compra"][0]} ARS
    <b>Promedio:</b>  {round(data_dict["promedio"][0], 2)} ARS
    <b>Variación:</b> {data_dict["variacion"][0]} %
    <b>Fecha:</b>     {data_dict["fecha"][0]}
    <b>Hora:</b>      {data_dict["hora"][0]}

\r<b>Dolar oficial:</b>
    <b>Venta:</b>     {data_dict["venta"][1]} ARS
    <b>Compra:</b>    {data_dict["compra"][1]} ARS
    <b>Promedio:</b>  {round(data_dict["promedio"][1], 2)} ARS
    <b>Variación:</b> {data_dict["variacion"][1]} %
    <b>Fecha:</b>     {data_dict["fecha"][1]}
    <b>Hora:</b>      {data_dict["hora"][1]}

\r<b>Dolar turista:</b>
    <b>Venta:</b>     {data_dict["venta"][2]} ARS
    <b>Compra:</b>    {data_dict["compra"][2]} ARS
    <b>Promedio:</b>  {round(data_dict["promedio"][2], 2)} ARS
    <b>Variación:</b> {data_dict["variacion"][2]} %
    <b>Fecha:</b>     {data_dict["fecha"][2]}
    <b>Hora:</b>      {data_dict["hora"][2]}
    """

    return texto_a_enviar


    import logging
import telegram
from telegram.ext import Updater, CommandHandler
import sys
import os

# Configurar Logging
logging.basicConfig(
    level = logging.INFO, format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s,"
)
logger = logging.getLogger()

# Solicitar TOKEN

# Para produccion
# TOKEN = os.getenv("TOKEN")
# mode = os.getenv("MODE")

# Para desarrollo (local)
mode = "dev"
TOKEN = "2085622215:AAETYK_a2ZRNOo8KcioQBo8J4Gg5yX4Z40E"

if mode == "dev":
    # Acceso Locar (desarrollo):
    def run(updater):
        updater.start_polling()
        print("BOT CARGADO")
        updater.idle() # permite finalizar el bot con Ctrl + C

elif mode =="prod":
    # Acceso HEROKU (produccion)
    def run(updater):
        PORT = int(os.environ.get("PORT", "8443K"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=PORT, url_path=TOKEN)
        update.bot.set_webhook(f"https://{HEROKU_APP_NAME}.herokuapp.com/{TOKEN}")

else:
    logger.info("No se especifico el MODE.")
    sys.exit()


def start(update, context):
    name = update.effective_user['first_name']
    logger.info(f"El usuario {update.effective_user['username']}/{name}, ha iniciado una conversacion")
    update.message.reply_text(f"Hola {name} bienvenidx al bot de Dolar Argentina. Usa el comando /dolar para conocer los precios del dia.")


def enviar_precios_dolar(update, context):
    user_id = update.effective_user['id']
    name = update.effective_user['first_name']
    username = update.effective_user['username']
    logger.info(f"El usuario {name}/{username}/{user_id}, ha solicitado precios de dolar.")
    texto_precios_dolar = generar_string_dolares()
    context.bot.sendMessage(chat_id = user_id, parse_mode="HTML", text = texto_precios_dolar)



if __name__ == "__main__":
    # Obtenemos informacion de nuestro bot
    my_bot = telegram.Bot(token = TOKEN)
    print(my_bot.getMe())

# Enlazamos nuestro updater
updater = Updater(my_bot.token, use_context=True)

# Creamos un despachador
dp = updater.dispatcher

# Creamos los manejadores
dp.add_handler(CommandHandler("start", start))
dp.add_handler(CommandHandler("dolar", enviar_precios_dolar))


run(updater)



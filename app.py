from flask import Flask, Response, request
from bot import LanguageLearningBot
import os
import sqlalchemy

# https://api.telegram.org/bot1623674677:AAFNHd1PgUbzKH3YW7nUoUGXKzEePGGq3tY/setWebhook?url=https://5ac3d6c47f25.ngrok.io
from db import User, Session

TOKEN = "1610355784:AAHUz0b-GSk8iOlwlrR0jiLTkAeXYEOcw1M"  # '1623674677:AAGhGrT-8icuj1niyMnD5fntn2MmsCH7vB4'  # AAFNHd1PgUbzKH3YW7nUoUGXKzWePGGGq3tY
URL = os.getenv('URL')
# Хитро получаем абсолютный путь (для локального сервера)
DEBUG = False

app = Flask(__name__)
bot = LanguageLearningBot(TOKEN)


@app.route(f"/{TOKEN}", methods=["GET", "POST"])
def receive_update():
    bot.handle_update(request.json)

    return Response(status=200)


@app.route("/setWebhook")
def set_webhook():
    response = bot.set_webhook(f'{URL}/{TOKEN}')
    return Response(response)


@app.route("/sendmessage")
def send_message():
    bot.send_message(request.args.get('to'), request.args.get('message'))

    return Response(status=200)

@app.route('/broadcast')
def broadcast():
    session = Session()
    users = session.query(User).all()
    for user in users:
        bot.send_message(user.id, request.args.get('message'))

    return Response(request.args.get('message'))

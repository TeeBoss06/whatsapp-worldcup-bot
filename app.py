"""
WhatsApp World Cup Bot
Powered by Flask + Twilio
"""

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

import worldcup

load_dotenv()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def home():
    return "🏆 World Cup WhatsApp Bot is running!"


@app.route("/whatsapp", methods=["POST"])
def whatsapp():

    incoming = request.form.get("Body", "").strip()

    replies = worldcup.handle_command(incoming)

    response = MessagingResponse()

    for reply in replies:
        response.message(reply)

    return str(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
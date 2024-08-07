from flask import Flask, request, jsonify

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import Campaign

from uuid import uuid4

app = Flask(__name__)

message = """
🚨 New Campagn 🚨

🔗 [X Link]({})
💰 Budget: {}

👍 Like
💬 Comment
🔁 Share

"""


@app.route("/influfun", methods=['GET', 'POST'])
async def hello_world():
    if request.is_json:
        # Extraire les données JSON
        data = request.get_json()
        
        
        # Traiter les données comme vous le souhaitez
        print("Données reçues :", data)
        
        id_campaign = str(uuid4())
        x_url = data.get("url")
        x_budget = data.get("budget")
        
        Campaign().add(id_campaign, x_url, x_budget)
        
        msg = message.format(x_url, x_budget)
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text='➡ CLICK TO START', url="https://t.me/Automate_y_bot?start={}".format(id_campaign))        
        
        bot = Bot(token="7378128032:AAEqUoSRiuazSZS7gmaeSEasZnzfaP-C31U")
        
        await bot.send_message("-1002245377748", msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        # Envoyer une réponse
        return jsonify({"message": "Données reçues avec succès", "data": data}), 200

    else:
        return jsonify({"error": "Requête non JSON"}), 400
    

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5005)
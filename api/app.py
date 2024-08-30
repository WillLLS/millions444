from flask import Flask, request, jsonify

from aiogram import Bot
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import InlineKeyboardBuilder

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import PendingCampaign

from uuid import uuid4

import requests

app = Flask(__name__)

from dataclasses import dataclass, astuple

@dataclass
class campaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    is_finished: str = None
    
    def __str__(self):
        tm_username = self.tm_username.replace("@", "\@")
        return f"{self.tm_username} - {self.budget}$ - [Link]({self.x_url})"


@app.route("/", methods=['GET'])
def hello():
    return "Hello World!"

@app.route("/influfun", methods=['GET', 'POST'])
async def influfun():
    if request.is_json:
        # Extraire les données JSON
        data = request.get_json()
        
        # Traiter les données comme vous le souhaitez
        print("Données reçues :", data)
        
        camp = campaign()
        
        camp.id_campaign = str(uuid4())
        camp.x_url = data.get("url")
        camp.tm_username = data.get("username")

        solana_budget = data.get("budget") # In solana

        camp.budget = round(get_solana_price() * (int(solana_budget) - 0.1*int(solana_budget)))
        
        camp.is_finished = False
        
        
        PendingCampaign.add(*astuple(camp))
        
        
        #bot = Bot(token="7436273086:AAEa-w6y44EvNwFhFH4W2U-iIPfaUBOQ1Wc")
        async with Bot(token="7436273086:AAEa-w6y44EvNwFhFH4W2U-iIPfaUBOQ1Wc") as bot:

            admin_users_id = ["6534222555", "1924764922"]
            
            for admin_id in admin_users_id:
                await bot.send_message(admin_id, "New Pending Campaign!")
                        
        # Envoyer une réponse
        return jsonify({"message": "Données reçues avec succès", "data": data}), 200

    else:
        return jsonify({"error": "Requête non JSON"}), 400
    

def get_solana_price():
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {
        "ids": "solana",        # ID de la cryptomonnaie sur CoinGecko
        "vs_currencies": "usd"  # La devise dans laquelle le prix doit être renvoyé
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        solana_price = data.get("solana", {}).get("usd", None)
        if solana_price is not None:
            return solana_price
        else:
            return "Le prix du Solana n'a pas pu être récupéré."
    else:
        return f"Erreur lors de la requête: {response.status_code}"
    

if __name__ == "__main__":
    app.run(debug=True)
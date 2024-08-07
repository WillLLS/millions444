from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.link_preview_options import LinkPreviewOptions
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import asyncio
import websockets
import json

import logging

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import Campaign, Influencer

from pprint import pprint

bot = Bot(token="7378128032:AAEqUoSRiuazSZS7gmaeSEasZnzfaP-C31U")

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)


campaign_msg = """
Welcome !

To complete the campaign:
- Like the post
- Comment the post
- Share the post

Link: {}

"""

# Admin command

from dataclasses import dataclass

@dataclass
class influencer:
    id_influencer: str = None
    x_name: str = None
    price: float = None
    tm_name: str = None
    wallet: str = None
    
    def __str__(self):
        return f"{self.tm_name} - {self.x_name} - {self.price} - {self.wallet}"
    
@dataclass
class campaign:
    id_campaign: str = None
    x_url: str = None
    budget: float = None
    
    def __str__(self):
        return f"[{self.x_url[0:10]}...]({self.x_url}) - {self.budget}"


def influencer_verification(tm_username):
    res = Influencer().get_from_tm_name(tm_username)

    if res:
        return True
    else:
        return False



@dp.message(CommandStart())
async def send_message(message: Message):
    command_text = message.text.split()
            
    if not influencer_verification(message.from_user.username):
        await message.answer("You are not allowed to use this bot")
        return
    
    if len(command_text) == 1:
        await message.answer("No campaign associated")
        return
    
    else:
        data = Campaign().get_from_id(command_text[-1])
            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text='➡ Verification', callback_data='verification')

        msg = campaign_msg.format(data[1])
            
        await message.answer(text=msg, parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
            
    
@form_router.callback_query()
async def callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    message = call.message
    data = call.data    
    
    if data == "verification":
        await message.edit_text("Verification started...")
        
        import time
        time.sleep(5)
        
        await message.edit_text("Verification completed!")
    
    if data == "view_influencers":
        data = Influencer().get_all()        
        
        influencers = ""
        for influ in data:
            i = influencer(*influ)
            influencers += str(i) + "\n"
            
        await message.answer(influencers)
        
    if data == "view_campaigns":
        data = Campaign().get_all()
        
        campaigns = ""
        for camp in data:
            c = campaign(*camp)
            campaigns += str(c) + "\n"
            
        await message.answer(campaigns, parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True))
        
    if data == "add_influencer":
        
        await state.set_state(Form.x_name)
        await message.answer("Send the X name")
        
    if data == "add_influ_yes":
        
        influ_data = await state.get_data()
        print(influ_data)
        await state.clear()
        await message.edit_text("Influencer added !")
    
    if data == "add_influ_no":
        await state.clear()
        await message.delete()
        

class Form(StatesGroup):
    x_name = State()
    price = State()
    tm_name = State()
    wallet = State()


    
    
        
@form_router.message(Form.x_name)
async def add_influ_name(message: Message, state: FSMContext):
    await state.update_data(x_name=message.text)

    await message.answer("Send the wallet")
    await state.set_state(Form.wallet)
    
@form_router.message(Form.wallet)
async def add_influ_name(message: Message, state: FSMContext):
    await state.update_data(wallet=message.text)
    
    await message.answer("Send the price")
    await state.set_state(Form.price)
    
@form_router.message(Form.price)
async def add_influ_name(message: Message, state: FSMContext):
    await state.update_data(price=message.text)

    await message.answer("Send the tm name")
    await state.set_state(Form.tm_name)
    
@form_router.message(Form.tm_name)
async def add_influ_name(message: Message, state: FSMContext):
    await state.update_data(tm_name=message.text)
    
    data = await state.get_data()
    
    print(data)    
    

    resume = f"New influencer\n\n\
*X username:* {data["x_name"]}\n\
*Tm username:* {data["tm_name"]}\n\
*Price:* {data["price"]}\n\
*Wallet:* {data["wallet"]}"  
    
    mk_b = InlineKeyboardBuilder()
   
    mk_b.button(text="? Validate ?", callback_data="None")
    mk_b.button(text='Yes', callback_data='add_influ_yes')
    mk_b.button(text='No', callback_data='add_influ_no')

    mk_b.adjust(1, 2)
    
    await message.answer(resume, parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
    
    

@dp.message(Command("admin"))
async def admin_command(message: Message):
    
    print(message.from_user.username == "automate_y")
    
    if (message.from_user.username != "automate_y"):
        print("Not allowed")
        return
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='View Influencers', callback_data='view_influencers')
    mk_b.button(text='View Campaigns', callback_data='view_campaigns')
    mk_b.button(text='Add Influencer', callback_data='add_influencer')
    
    
    mk_b.adjust(1,)
    
    await message.answer("Admin panel", reply_markup=mk_b.as_markup())
    
async def add_influencer(message: Message):
    
    await message.answer("Enter the influencer's data")






async def send_command(url, username):
    uri = "ws://localhost:8766"
    async with websockets.connect(uri) as websocket: 
        
        command = {
            "url": url,
            "username": username
        }
        # Envoie de la commande au serveur
        await websocket.send(json.dumps(command))
        print(f"Sent command: {command}")

        # Réception de la réponse du serveur
        response = await websocket.recv()
        print(f"Received response: {response}")
        
        
async def main():
    
    await asyncio.gather(dp.start_polling(bot))


if __name__ == "__main__":
    
    
    
    logging.basicConfig(level=logging.INFO)
    
    asyncio.get_event_loop().run_until_complete(main())

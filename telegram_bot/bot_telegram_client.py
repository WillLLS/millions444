from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.link_preview_options import LinkPreviewOptions
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

import logging
import asyncio 
import requests
import math
import re

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import Campaign, PendingCampaign, RefusedCampaign, Influencer, PendingInfluencer, Validation, Affiliation, Checker

from uuid import uuid4

from utils.messages import *
from utils.paths import *
from config.token import *

bot = Bot(token=token_bot_client)

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)


class FormInfluencer(StatesGroup):
    audience_type = State()
    x_name = State()
    followers = State()
    wallet = State()
    price = State()
    
class Dashboard(StatesGroup):
    dashboard = State()
    create_campaign = State()
 
class FormClient(StatesGroup):
    project_type = State()
    x_url = State()
    budget = State()
        
class FormClient(StatesGroup):
    project_type = State()
    x_url = State()
    budget = State()
    
class FormRefund(StatesGroup):
    ask_wallet = State()

class FormNewPrice(StatesGroup):
    ask_new_price = State()



txt_btn_tech = "Tech project 👨‍💻"
txt_btn_meme = "Meme coin 🐕"
txt_btn_nft  = "NFT 🖼"
txt_btn_away = "Giveaways 🎁"


from dataclasses import dataclass, astuple

@dataclass
class influencer:
    id_influencer: str = None
    x_name: str = None
    price: float = None
    tm_name: str = None
    tm_id: str = None
    wallet: str = None
    followers: int = None
    audience_type: int = None
    
    def __str__(self):
        return f"{self.tm_name} - {self.x_name} - {self.price} - {self.wallet}"
    
@dataclass
class campaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    budget_left: float = None
    id_message: str = None
    is_finished: str = None
    project_type: int = None
    
    def __str__(self):
        tm_username = self.tm_username.replace("@", "\@")
        return f"{self.tm_username} - {self.budget}$ - [Link]({self.x_url})"
    
@dataclass
class pendingCampaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    is_finished: str = None
    project_type: int = None
    
    def __str__(self):
        tm_username = self.tm_username.replace("@", "\@")
        return f"{self.tm_username} - {self.budget}$ - [Link]({self.x_url})"
    

def encode_type(_type: dict):
    # {"tech": 0, "meme": 0, "nft": 0, "giveaway": 0}
    value = 0
    if _type["tech"]:
        value += 1
    if _type["meme"]:
        value += 2
    if _type["nft"]:
        value += 4
    if _type["giveaway"]:
        value += 8
    return value

def decode_type(value: int):
    _type = {"tech": 0, "meme": 0, "nft": 0, "giveaway": 0}
    if (value >> 3) & 0b0001:
        _type["giveaway"] = 1
    if (value >> 2) & 0b0001:
        _type["nft"] = 1
    if (value >> 1) & 0b0001:
        _type["meme"] = 1
    if value & 0b0001:
        _type["tech"] = 1
    return _type

def format_number(number : float or int):
    return f"{number:,}".replace(",", ".")

@form_router.message(CommandStart())
async def send_message(message: Message, state: FSMContext):
    
    command_text = message.text.split()
    print(command_text)
    
    if len(command_text) == 2:
        
        
        id_influ_referent = command_text[1]
        
        if Checker.is_influencer_from_id(id_influ_referent):
            
            inf = influencer(*Influencer.get_from_tm_name(message.from_user.username))
            
            
            if id_influ_referent == inf.id_influencer:
                await message.answer("[DEBUG MESSAGE]\n\nYou cannot affiliate to yourself :)\n\nPas bloquant pour les tests")
            print("[+] Referent link used")
            await state.update_data(referent=id_influ_referent)
        
    
    tm_username = message.from_user.username
    
    await state.update_data(tm_username=tm_username)
    await state.update_data(first_name=message.from_user.first_name)
    await state.update_data(tm_id=message.from_user.id)
        
        
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="I'm launching a project 🚀", callback_data='client')
    mk_b.button(text="I'm an influencer 👨‍🚀", callback_data='influencer')
    mk_b.button(text="I'm Lost 😢", callback_data='lost')
        
    mk_b.adjust(1,)
        
    image = FSInputFile(path_img_whoareyou)

    await message.delete()
        
    await message.answer_photo(photo=image, 
                                caption=message_start.format(message.from_user.first_name), 
                                reply_markup=mk_b.as_markup(), 
                                parse_mode=ParseMode.MARKDOWN)


#----- Influencer DashBoard

@form_router.message(Command("dashboard"))
async def dashboard(message: Message, state: FSMContext, edit=False):
    
    
    if not edit:
        tm_username = message.from_user.username
        first_name  = message.from_user.first_name
        
        await state.update_data(tm_username=tm_username)
        await state.update_data(first_name=message.from_user.first_name)
        await state.update_data(tm_id=message.from_user.id)
        
    else:
        
        cache_data = await state.get_data()
        
        try:
            tm_username = cache_data["tm_username"]
            first_name  = cache_data["first_name"]
        except KeyError:
            await message.delete()
            await message.answer(message_bot_reset)
            return
    
    if not Checker.is_influencer(tm_username) and not Checker.is_client(tm_username):
        await message.delete()
        await message.answer("Not saved in the databased, please use the command /start")
        await state.clear()
        return    
    
    
    await state.set_state(Dashboard.dashboard)
    
    category = {"pending_influ": 0, "influ": 0, "pending_camp": 0, "camp": 0}
    
    
    if PendingInfluencer.get_from_tm_name(tm_username):
        category["pending_influ"] = 1
        
    if Influencer.get_from_tm_name(tm_username):
        category["influ"] = 1
        
    if PendingCampaign.get_from_tm_name(tm_username):
        category["pending_camp"] = 1
        
    if Campaign.get_from_tm_name(tm_username):
        category["camp"] = 1
    
    await state.update_data(category=category)
    
    
    msg = f"*Welcome {first_name}* 👋"
    
    mk_b = InlineKeyboardBuilder()
    
    mk_b.button(text="DASHBOARD", callback_data='None')
    mk_b.button(text="Profile  👨‍🚀", callback_data='dashboard:my_profile')
    mk_b.button(text="Campaign 🚀", callback_data='dashboard:campaign:running')
    
    mk_b.adjust(1, 2, 1)
    
    if edit:
                            
        new_photo = FSInputFile(path_img_dashboard)
        media = InputMediaPhoto(media=new_photo, caption=msg, parse_mode=ParseMode.MARKDOWN)
                                            
        await message.edit_media(media=media, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
            
    else:
        
        await message.answer_photo(photo=FSInputFile(path_img_dashboard), caption=msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    

@form_router.message(FormRefund.ask_wallet)
async def get_refund_wallet(message: Message, state: FSMContext):
    
    wallet = message.text

    
    def is_valid_solana_wallet(wallet: str) -> bool:
        
        solana_wallet_regex = r'^[A-HJ-NP-Za-km-z1-9]{44}$'
        return re.match(solana_wallet_regex, wallet) is not None
    
    if not is_valid_solana_wallet(wallet):
        await message.answer("Please send a valid wallet")
        return
    
    cache_data = await state.get_data()
    
    try:
        refused_id_campaign = cache_data["refused_id_campaign"]
    except KeyError:
        await message.delete()
        await message.answer(message_bot_reset)
        return
    
    RefusedCampaign.update_wallet(refused_id_campaign, wallet)

    async with Bot(token=token_bot_admin) as bot:
        
                admin_users_id = ["6534222555", "1924764922"]
            
                for admin_id in admin_users_id:
                    await bot.send_message(admin_id, "New refund asking, wallet updated!")
    
    
    await state.clear()
    await message.answer("Thanks you for your wallet, you will be refunded soon!")

    
@form_router.callback_query()
async def callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    message = call.message
    data = call.data    
    
    #--- Influencer CallBack
    
    if data == "influencer":
        
        cache_data = await state.get_data()
        
        try:
            tm_username = cache_data["tm_username"]
        except KeyError:
            await message.delete()
            await message.answer(message_bot_reset)
            return
            
        
        
        if Checker.is_influencer(tm_username):
            await message.delete()
            await message.answer("You already are an influencer")
            return
        
        
        await state.set_state(FormInfluencer.audience_type)
        
        await message.answer("🚀")
        await message.delete()
        
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=txt_btn_tech, callback_data='audience:tech')
        mk_b.button(text=txt_btn_meme, callback_data='audience:meme')
        mk_b.button(text=txt_btn_nft,  callback_data='audience:nft')
        mk_b.button(text=txt_btn_away, callback_data='audience:giveaway')
    
        mk_b.adjust(1,)
        
        await state.update_data(audience_type={"tech": 0, "meme": 0, "nft": 0, "giveaway": 0})
        
        await message.answer("Let's start with a fast form :\n\nSelect your audience type 👇", reply_markup=mk_b.as_markup())
          
    if data.split(":")[0] == "audience":
        selection = data.split(":")[1]
        
        cache_data = await state.get_data()
        
        try:
            audience_type = cache_data["audience_type"]
        except KeyError:
            await message.delete()
            await message.answer(message_bot_reset)
            return
        
        audience_type[selection] = 1 - audience_type[selection]
                
        await state.update_data(audience_type=audience_type)
        
        btn_tech = "✅ " + txt_btn_tech if audience_type["tech"] else txt_btn_tech
        btn_meme = "✅ " + txt_btn_meme if audience_type["meme"] else txt_btn_meme
        btn_nft  = "✅ " + txt_btn_nft  if audience_type["nft"] else txt_btn_nft
        btn_away = "✅ " + txt_btn_away if audience_type["giveaway"] else txt_btn_away
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=btn_tech, callback_data='audience:tech')
        mk_b.button(text=btn_meme, callback_data='audience:meme')
        mk_b.button(text=btn_nft,  callback_data='audience:nft')
        mk_b.button(text=btn_away, callback_data='audience:giveaway')
        
        if audience_type["tech"] or audience_type["meme"] or audience_type["nft"] or audience_type["giveaway"]:
            mk_b.button(text="▶ Validate",  callback_data='validate_audience_type')
    
        mk_b.adjust(1,)
        
        await message.edit_text("Let's start with a fast form:\n\nSelect your audience type", reply_markup=mk_b.as_markup())

    if data == "validate_audience_type":
        await state.set_state(FormInfluencer.x_name)
        
        cache_date = await state.get_data()
        
        audience_type = cache_date["audience_type"]
        
        message_project_updated = "Your audience type:\n"
        message_project_updated += "\n✅ " + txt_btn_tech if audience_type["tech"] else "\n❌ " + txt_btn_tech
        message_project_updated += "\n✅ " + txt_btn_meme if audience_type["meme"] else "\n❌ " + txt_btn_meme
        message_project_updated += "\n✅ " + txt_btn_nft  if audience_type["nft"]  else "\n❌ " + txt_btn_nft
        message_project_updated += "\n✅ " + txt_btn_away if audience_type["giveaway"] else "\n❌ " + txt_btn_away
        
        await message.edit_text(message_project_updated)
        
        image = FSInputFile(path_img_ask_x_name)

        await message.answer_photo(photo=image, 
                                   caption="🤓 Send your X name (@example)", 
                                   parse_mode=ParseMode.MARKDOWN) 
                           
    if data.split(":")[0] == "accept_fees":
        choice = data.split(":")[1]
        
        if choice == "yes":
            
            previous_message = "You accept that INFLU.FUN takes 10% of your price 👇\n\n► Yes bro 😇"
            await message.edit_text(previous_message)
            
            cache_data = await state.get_data()
            
            id_influencer = str(uuid4())
            
            try:
                x_name  = cache_data["x_name"]
                price   = cache_data["price"]
                tm_username = cache_data["tm_username"]
                tm_id = cache_data["tm_id"]
                wallet = cache_data["wallet"]
                followers = cache_data["followers"]
                audience_type = encode_type(cache_data["audience_type"])
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return

            PendingInfluencer.add(id_influencer, x_name, price, tm_username, tm_id, wallet, followers, audience_type)
            
            
            async with Bot(token=token_bot_admin) as bot:
        
                admin_users_id = ["6534222555", "1924764922"]
            
                for admin_id in admin_users_id:
                    await bot.send_message(admin_id, "New Pending Influencer!")
                    
            
            try:
                first_name = cache_data['first_name']
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
            
            final_msg = f"🥳 Thank you {first_name}, we will get back to you after studying your profile and your price 🧐"
            
            image = FSInputFile(path_img_pending_influ)
            
            await state.clear()

            await message.answer_photo(photo=image, 
                                        caption=final_msg, 
                                        parse_mode=ParseMode.MARKDOWN)
            #await message.answer(final_msg)
            
        elif choice == "no":
            
            accept_fees_msg = "You accept that INFLU.FUN takes 10% of your price 👇"
    
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="❔ Are you sure ❔", callback_data='None')
            mk_b.button(text="Yes 💩", callback_data='None')
            mk_b.button(text="No sorry bro 🙏", callback_data='accept_fees:yes')
            
            mk_b.adjust(1, 2)
            
            await message.edit_text(accept_fees_msg, reply_markup=mk_b.as_markup())
            
            
    #--- Client CallBack

    if data == "client":
        await state.set_state(FormClient.project_type)
        
        await message.answer("🚀")
        await message.delete()
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=txt_btn_tech, callback_data='project:tech')
        mk_b.button(text=txt_btn_meme, callback_data='project:meme')
        mk_b.button(text=txt_btn_nft,  callback_data='project:nft')
        mk_b.button(text=txt_btn_away, callback_data='project:giveaway')
    
        mk_b.adjust(1,)
        
        await state.update_data(project_type={"tech": 0, "meme": 0, "nft": 0, "giveaway": 0})
        
        await message.answer("Let's start with a fast form :\n\nSelect your project type 👇", reply_markup=mk_b.as_markup())
          
    if data.split(":")[0] == "project":
        selection = data.split(":")[1]
        
        cache_data = await state.get_data()
        
        try:
            project_type = cache_data["project_type"]
        except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
        project_type[selection] = 1 - project_type[selection]
                
        await state.update_data(audience_type=project_type)
        
        btn_tech = "✅ " + txt_btn_tech if project_type["tech"] else txt_btn_tech
        btn_meme = "✅ " + txt_btn_meme if project_type["meme"] else txt_btn_meme
        btn_nft =  "✅ " + txt_btn_nft  if project_type["nft"]  else txt_btn_nft
        btn_away = "✅ " + txt_btn_away if project_type["giveaway"] else txt_btn_away
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=btn_tech, callback_data='project:tech')
        mk_b.button(text=btn_meme, callback_data='project:meme')
        mk_b.button(text=btn_nft,  callback_data='project:nft')
        mk_b.button(text=btn_away,  callback_data='project:giveaway')
        
        if project_type["tech"] or project_type["meme"] or project_type["nft"] or project_type["giveaway"]:
            mk_b.button(text="▶ Validate",  callback_data='validate_project_type')
    
        mk_b.adjust(1,)
        
        await message.edit_text("Let's start with a fast form :\n\nSelect your project type 👇", reply_markup=mk_b.as_markup())
        
    if data == "validate_project_type":
        
        cache_date = await state.get_data()
        
        project_type = cache_date["project_type"]
        
        message_project_updated = "Your project type:\n"
        message_project_updated += "\n✅ " + txt_btn_tech if project_type["tech"] else "\n❌ " + txt_btn_tech
        message_project_updated += "\n✅ " + txt_btn_meme if project_type["meme"] else "\n❌ " + txt_btn_meme
        message_project_updated += "\n✅ " + txt_btn_nft  if project_type["nft"]  else "\n❌ " + txt_btn_nft
        message_project_updated += "\n✅ " + txt_btn_away if project_type["giveaway"] else "\n❌ " + txt_btn_away
        
        await message.edit_text(message_project_updated)
        
        await state.set_state(FormClient.x_url)
        #await message.answer("Send your X Post Link 🔗:")
        
        image = FSInputFile(path_img_ask_x_name)

        await message.answer_photo(photo=image, 
                                    caption="Send your X Post Link 🔗:", 
                                    parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "budget":
        choice = data.split(":")[1]
        
        if choice == "no":
            await message.delete()
        
        elif choice == "yes":
            
            cache_data = await state.get_data()
            
            try:
                msg_live = cache_data["msg_live"]
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
            
            await message.edit_text(msg_live)
            
            p_camp = pendingCampaign()
        
            try:
                p_camp.id_campaign = str(uuid4())
                p_camp.x_url = cache_data["x_url"]
                p_camp.tm_username = cache_data["tm_username"]
                p_camp.tm_id = cache_data["tm_id"]
                p_camp.budget = math.floor(float(cache_data["budget"]) * cache_data["solana_price"])
                p_camp.is_finished = False
                p_camp.project_type = encode_type(cache_data["project_type"])
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
            
            
            if "referent" in cache_data.keys():
                print("[+] Referent found for this campaign")
                
                try:
                    id_influ_referent = cache_data["referent"]
                except KeyError:
                    await message.delete()
                    await message.answer(message_bot_reset)
                    return
            
                Affiliation.add(id_influ_referent, p_camp.id_campaign)
            
            
            PendingCampaign.add(*astuple(p_camp))
            
            
            async with Bot(token=token_bot_admin) as bot:
        
                admin_users_id = ["6534222555", "1924764922"]
            
                for admin_id in admin_users_id:
                    await bot.send_message(admin_id, "New Pending Campaign!")
            
            
            await state.clear()
            
            image = FSInputFile(path_img_pending_campaign)

            await message.answer_photo(photo=image, 
                                        caption=message_send_to_wallet, 
                                        parse_mode=ParseMode.MARKDOWN)
            
            #await message.answer(message_send_to_wallet, parse_mode=ParseMode.MARKDOWN)
    
    
    #--- Lost Callback
    
    if data == "quit":
        await message.delete()
    
    if data == "lost":
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="🫡 Understood my Loard ", callback_data=f'quit')
        
        await message.answer(message_lost, reply_markup=mk_b.as_markup())
    
    #--- Refund Callback
    
    if data.split(":")[0] == "refund":
        id_campaign = data.split(":")[1]
        
        await state.set_state(FormRefund.ask_wallet)
        await state.update_data(refused_id_campaign=id_campaign)
        await message.answer("Please send your wallet for a refund")
        
    #--- New price 
    
    if data.split(":")[0] == "accept":
        new_price = data.split(":")[1]
        id_influencer = data.split(":")[2]
        
        inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        
        PendingInfluencer.update_price(id_influencer, new_price)
        
        await message.edit_text("Thank you, wait now for the approuval")
        
        async with Bot(token=token_bot_admin) as bot: # Automate_bot
        
                admin_users_id = ["6534222555", "1924764922"]
                
                mk_b = InlineKeyboardBuilder()
                mk_b.button(text="See", callback_data=f"p_inf:{id_influencer}")
            
                for admin_id in admin_users_id:
                    await bot.send_message(admin_id, f"{inf.tm_name} accept the new price", reply_markup=mk_b.as_markup())
                    
        await state.clear()
        
    if data.split(":")[0] == "ask_price":
        proposed_price = data.split(":")[1]
        id_influencer = data.split(":")[2]
        
        await state.set_state(FormNewPrice.ask_new_price)
        await state.update_data(message_ref=message)
        await state.update_data(id_influencer=id_influencer)
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Mmm Finaly I accept the offer !", callback_data=f"accept:{proposed_price}:{id_influencer}")
        
        await message.edit_text(f"Proposed Price : {proposed_price} $\nPlease send your new price: ", reply_markup=mk_b.as_markup())  
        
    if data.split(":")[0] == "new_price":
        new_price = data.split(":")[1]
        
        try:
            id_influencer = (await state.get_data())["id_influencer"]
        except KeyError:
            await message.delete()
            await message.answer(message_bot_reset)
            return
        
        inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        
        PendingInfluencer.update_price(id_influencer, new_price)
    
        async with Bot(token=token_bot_admin) as bot:
        
            admin_users_id = ["6534222555", "1924764922"]
                
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="See", callback_data=f"p_inf:{id_influencer}")
            
            for admin_id in admin_users_id:
                await bot.send_message(admin_id, f"{inf.tm_name} proposed a new price: {new_price} $", reply_markup=mk_b.as_markup())
                
        await message.edit_text("New price sent, you will be notified if it is validated!")
    
    
    #--- Dashboard
    
    if data == "refer":
        
        cache_data = await state.get_data()
        
        # Only available for influencer ?
        
        try:
            tm_username = cache_data["tm_username"]
        except KeyError:
            await message.delete()
            await message.answer(message_bot_reset)
            return
        
        inf = influencer(*Influencer.get_from_tm_name(tm_username))
        
        
        pth_img_referal
        
        msg = message_referal.format(f"https://t.me/influ_fun_bot?start={inf.id_influencer}")
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Got it !", callback_data='quit')
        
        await message.answer_photo(photo=FSInputFile(pth_img_referal), caption=msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "back":
        link = data.split(":")[1]
        
        if link == "main_dashboard":
            await dashboard(message, state, edit=True)
            
    if data.split(":")[0] == "camp_details":
        id_campaign = data.split(":")[1]
        
        status = data.split(":")[2]
        
        if status == "running" or status == "finished":
            camp = campaign(*Campaign.get_from_id(id_campaign))
        
        elif status == "pending":
            camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
        
        msg = "*Your campaign details*\n\n"
        msg += f"*Status*: _{status.upper()}_\n"
        msg += f"*Budget*: _{int(camp.budget)}$_\n"
        msg += f"*Link*: [Here]({camp.x_url})\n"
        
        if status == "running" or status == "finished":
            
            msg += f"*Validation*: {Validation.count_validated_campaign(camp.id_campaign)}\n"
        
        
        msg += "*Project type*:\n"
        
        _type = decode_type(camp.project_type)
                
        if _type["tech"]:
            msg += "   _Tech project_ 👨‍💻\n"
        if _type["meme"]:
            msg += "   _Meme coin_ 🐕\n"
        if _type["nft"]:
            msg += "   _NFT_ 🖼\n"
        if _type["giveaway"]:
            msg += "   _Giveaways_ 🎁\n"
        
        
        mk_b = InlineKeyboardBuilder()
        
        mk_b.button(text="◀ back", callback_data=f'dashboard:campaign:{status}')

        mk_b.adjust(1,)
        
        new_photo = FSInputFile(path_img_dashboard)
        media = InputMediaPhoto(media=new_photo, caption=msg, parse_mode=ParseMode.MARKDOWN)
                                                
        await message.edit_media(media=media, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
        #await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
              
    if data.split(":")[0] == "dashboard":
        
        command = data.split(":")[1]
        
        cache_data = await state.get_data()
        
        if command == "my_profile":
            
            mk_b = InlineKeyboardBuilder()

            mk_b.button(text="DASHBOARD", callback_data='None')
            
            try:
                category_influ = cache_data["category"]["influ"]
                category_pending_influ = cache_data["category"]["pending_influ"]
                tm_username = cache_data["tm_username"]
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
        
            
            if category_influ:
                
                inf = influencer(*Influencer.get_from_tm_name(tm_username))

                count = Validation.count(inf.id_influencer)
                
                x_name = inf.x_name.replace('_', '\_')
                
                msg = "*My Profile 👨‍🚀*\n\n"
                msg += f"🤓 *X Name :* {x_name}\n"
                msg += f"💰 *Price :*  {format_number(int(inf.price))}$\n"
                msg += f"👀 *Followers :* {format_number(inf.followers)}\n"
                msg += f"✅ *Validated Campaign(s) :* {count}\n\n"
                msg += f"*Profil Type* 👇 \n"
                
                _type = decode_type(inf.audience_type)
                
                if _type["tech"]:
                    msg += "   _Tech project_ 👨‍💻\n"
                if _type["meme"]:
                    msg += "   _Meme coin_ 🐕\n"
                if _type["nft"]:
                    msg += "   _NFT_ 🖼\n"
                if _type["giveaway"]:
                    msg += "   _Giveaways_ 🎁\n"
                    
                mk_b.button(text="Refer a friend 🤝", callback_data='refer')
     
            elif category_pending_influ:
                inf = influencer(*PendingInfluencer.get_from_tm_name(tm_username))

                count = Validation.count(inf.id_influencer)
                                
                x_name = inf.x_name.replace('_', '\_')
                
                msg = "*Your profile*\n\n"
                msg += "_Your profile is currently pending\. Please wait, you will be notified as soon as it is accepted_\n\n"
                
                msg += f"*X name*: {x_name}\n"
                msg += f"*Price* : {int(inf.price)}$\n"
                msg += f"*Number of validated Campaign*: {count}\n"
            
            else:
                msg = "*You don't have influencer's profile yet*"
                mk_b.button(text="Create Influencer Profile", callback_data='influencer')
                
            mk_b.button(text="◀ back", callback_data='back:main_dashboard')

            mk_b.adjust(1,)
            
            new_photo = FSInputFile(path_img_dashboard)
            media = InputMediaPhoto(media=new_photo, caption=msg, parse_mode=ParseMode.MARKDOWN)
                                                
            await message.edit_media(media=media, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
            
            #await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
        if command == "campaign":
            mk_b = InlineKeyboardBuilder()
            
            msg = "*Your campaigns*" 
            
            try:
                category_camp = cache_data["category"]["camp"]
                category_pending_camp = cache_data["category"]["pending_camp"]
                tm_username = cache_data["tm_username"]
            except KeyError:
                await message.delete()
                await message.answer(message_bot_reset)
                return
            
            if category_camp or category_pending_camp:
                
                second_command = data.split(":")[2]
                
                if second_command == "running":
                
                    camps = Campaign.get_not_finished_from_tm_name(tm_username)

                    mk_b.button(text="◀", callback_data='dashboard:campaign:finished')
                    mk_b.button(text="✅ Running", callback_data='None')
                    mk_b.button(text="▶", callback_data='dashboard:campaign:pending')
                    
                    for i, camp in enumerate(camps):
                        cp = campaign(*camp)
                        btn_text = f"{cp.x_url} - {cp.budget}"
                        mk_b.button(text=btn_text, callback_data=f'camp_details:{cp.id_campaign}:running')

                elif second_command == "finished":
                    
                    camps = Campaign.get_finished_from_tm_name(tm_username)
                    
                    mk_b.button(text=" ", callback_data='None')
                    mk_b.button(text="🍾 Finished", callback_data='None')
                    mk_b.button(text="▶", callback_data='dashboard:campaign:running')
                    
                    for i, camp in enumerate(camps):
                        cp = campaign(*camp)
                        btn_text = f"{cp.x_url} - {cp.budget}"
                        mk_b.button(text=btn_text, callback_data=f'camp_details:{cp.id_campaign}:finished')
                        
                elif second_command == "pending":
                    
                    camps = PendingCampaign.get_from_tm_name(tm_username)

                    mk_b.button(text="◀", callback_data='dashboard:campaign:running')
                    mk_b.button(text="⏳ Pending", callback_data='None')
                    mk_b.button(text=" ", callback_data='None')
                    
                    for camp in camps:
                        cp = pendingCampaign(*camp)
                        btn_text = f"{cp.x_url} - {cp.budget}"
                        mk_b.button(text=btn_text, callback_data=f'camp_details:{cp.id_campaign}:pending')
                    
                
                mk_b.button(text="➕ Create a new Campaign ➕", callback_data='client')
                mk_b.button(text="◀ back", callback_data='back:main_dashboard')

                mk_b.adjust(3, 1,)   
                
            else:
                mk_b.button(text="➕ Create a new Campaign ➕", callback_data='client')
                mk_b.button(text="◀ back", callback_data='back:main_dashboard')
                
                mk_b.adjust(1,)               
            
            
            new_photo = FSInputFile(path_img_dashboard)
            media = InputMediaPhoto(media=new_photo, caption=msg, parse_mode=ParseMode.MARKDOWN)
                                                
            await message.edit_media(media=media, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
            #await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)
            
    
#----- Influencer route 
    
@form_router.message(FormInfluencer.x_name)
async def influ_get_x(message: Message, state: FSMContext):
    
    if "@" not in message.text:
        await message.answer("Send your X name (@example)")
        return
    
    await state.update_data(x_name=message.text)

    image = FSInputFile(path_img_ask_followers)

    await message.answer_photo(photo=image, 
                                caption="How many followers do you have? 😎 (example: 55000)", 
                                parse_mode=ParseMode.MARKDOWN)

    await state.set_state(FormInfluencer.followers)

@form_router.message(FormInfluencer.followers)
async def influ_get_followers(message: Message, state: FSMContext):
    
    def is_convertible_to_int(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False
        
    if not is_convertible_to_int(message.text):
        await message.answer("Please send a valid number")
        return
    
    await state.update_data(followers=message.text)
    
    image = FSInputFile(path_img_ask_wallet)

    await message.answer_photo(photo=image, 
                                caption="👛 Send your $SOL wallet :", 
                                parse_mode=ParseMode.MARKDOWN)
    
    await state.set_state(FormInfluencer.wallet)
    
@form_router.message(FormInfluencer.wallet)
async def influ_get_wallet(message: Message, state: FSMContext):
    
    
    def is_valid_solana_wallet(wallet: str) -> bool:
        
        solana_wallet_regex = r'^[A-HJ-NP-Za-km-z1-9]{44}$'
        return re.match(solana_wallet_regex, wallet) is not None
    
    if not is_valid_solana_wallet(message.text):
        await message.answer("Please send a valid wallet")
        return
    
    await state.update_data(wallet=message.text)
    
    image = FSInputFile(path_img_ask_price)

    await message.answer_photo(photo=image, 
                                caption="Send your price in $ for :\nLike 🩷 RT 🔄 and Com 💬", 
                                parse_mode=ParseMode.MARKDOWN)
    
    await state.set_state(FormInfluencer.price)
    
@form_router.message(FormInfluencer.price)
async def influ_get_price(message: Message, state: FSMContext):
    
    def is_convertible_to_int(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False
        
    if not is_convertible_to_int(message.text):
        await message.answer("Please send a valid number")
        return
    
    await state.update_data(price=int(message.text))
    
    accept_fees_msg = "You accept that INFLU.FUN takes 10% of your price 👇"
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="❔ Validate ❔", callback_data='None')
    mk_b.button(text="Yes bro 😇", callback_data='accept_fees:yes')
    mk_b.button(text="Fuck you 🖕", callback_data='accept_fees:no')
    
    mk_b.adjust(1, 2)
        
    await message.answer(accept_fees_msg, reply_markup=mk_b.as_markup())

@form_router.message(FormNewPrice.ask_new_price)
async def influ_get_new_price(message: Message, state: FSMContext):

    def is_convertible_to_int(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False
        
    if not is_convertible_to_int(message.text):
        await message.answer("Please send a valid number")
        return
    
    new_price = int(message.text)
    
    msg = f"*Please confirm the new price*\n\n{new_price} $"
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Confirm", callback_data=f"new_price:{new_price}")
    
    await message.delete()
    
    try:
        message = (await state.get_data())["message_ref"]
    except KeyError:
        await message.delete()
        await message.answer(message_bot_reset)
        return
    
    await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
    
    


#----- Client route 

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
            return float(solana_price)
        else:
            return "Le prix du Solana n'a pas pu être récupéré."
    else:
        return f"Erreur lors de la requête: {response.status_code}"

def get_estimated_influencers(price_usd : float or int):
    return math.floor(price_usd / 50)

def get_estimated_followers(price_usd : float or int):
    estimated_influencers = get_estimated_influencers(price_usd)
    return math.floor(estimated_influencers * ((50_000 + 200_000) / 2))
    
def get_message_live(budget : int, solana_price_usd):
    
    price_usd = math.floor(float(solana_price_usd) * budget)
    
    estimated_influencers   = get_estimated_influencers(price_usd)
    estimated_followers = get_estimated_followers(price_usd)
    
    return message_live_solana.format(format_number(solana_price_usd), 
                                      format_number(estimated_influencers), 
                                      format_number(estimated_followers), 
                                      format_number(budget), 
                                      format_number(price_usd))
    
@form_router.message(FormClient.x_url)
async def client_get_url(message: Message, state: FSMContext):
    
    # Expression régulière pour valider l'URL
    url_pattern = r'^https://x\.com/[A-Za-z0-9_]+/status/\d+(\?.*)?$'

    def is_valid_url(url):
        return re.match(url_pattern, url) is not None
    
    if not is_valid_url(message.text):
        await message.answer("Please send a valid URL")
        return
    
    await state.update_data(x_url=message.text)
    
    await state.set_state(FormClient.budget)
    #await message.answer("Send your Solana Budget 💰:")
    
    image = FSInputFile(path_img_ask_price)

    await message.answer_photo(photo=image, 
                                caption="Send your Solana Budget 💰:", 
                                parse_mode=ParseMode.MARKDOWN)
    
@form_router.message(FormClient.budget)
async def client_get_budget(message: Message, state: FSMContext):
    
    def is_convertible_to_int(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False
        
    if not is_convertible_to_int(message.text):
        await message.answer("Please send a valid number")
        return
    
    await state.update_data(budget=int(message.text))
    
    cache_data = await state.get_data()
    if("solana_price" not in list(cache_data.keys())):
        solana_price_usd = get_solana_price()
    else:
        solana_price_usd = cache_data["solana_price"]
    
    
    msg = get_message_live(int(message.text), solana_price_usd)

    await state.update_data(msg_live=msg)
    await state.update_data(solana_price=solana_price_usd)
    
    msg += "\n\nIf you want to change your budget, send it again :)"

    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="❔ Validate ❔", callback_data='None')
    mk_b.button(text="✅", callback_data='budget:yes')
    mk_b.button(text="❌",  callback_data='budget:no')
    
    mk_b.adjust(1, 2)
    
    
    await message.answer(msg, reply_markup=mk_b.as_markup())
    
 
async def main():

    await asyncio.gather(dp.start_polling(bot))
    


if __name__ == "__main__":    
    logging.basicConfig(level=logging.INFO)

    asyncio.get_event_loop().run_until_complete(main())
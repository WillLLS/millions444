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

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import Campaign, PendingCampaign, RefusedCampaign, Influencer, PendingInfluencer, Validation, Affiliation, Checker

from uuid import uuid4 

from dataclasses import dataclass

from config.token import *
from utils.messages import *
from utils.paths import *


bot = Bot(token=token_bot_admin)

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

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
        username = self.tm_username.replace("_", "\_")
        return f"@{username} - {self.budget} $"
    
    def info(self):
        
        username = self.tm_username.replace("_", "\_")
        
        info = f"*Tm username*: @{username}\n"
        info += f"*Budget*: {self.budget} $\n"
        info += f"*Link*: [Click Here]({self.x_url})\n        or (_Touch to Copy_)\n\n`{self.x_url}`\n\n"
        info += f"*Project type*:\n"
        
        # Assume decode_type is defined elsewhere
        _type = decode_type(self.project_type)
                
        if _type["tech"]:
            info += "   _Tech project_ 👨‍💻\n"
        if _type["meme"]:
            info += "   _Meme coin_ 🐕\n"
        if _type["nft"]:
            info += "   _NFT_ 🖼\n"
        if _type["giveaway"]:
            info += "   _Giveaways_ 🎁\n"
            
        return info
    
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
        tm_username = self.tm_username.replace("_", "\_")
        return f"{self.tm_username} - {self.budget}$"
    
    def info(self):
        
        username = self.tm_username.replace("_", "\_")
        
        info = f"*Tm username*: @{username}\n"
        info += f"*Total Budget*: {self.budget} $\n"
        info += f"*Budget Left*: {self.budget_left} $\n"
        info += f"*Project type*:\n"
        
        _type = decode_type(self.project_type)
                
        if _type["tech"]:
            info += "   _Tech project_ 👨‍💻\n"
        if _type["meme"]:
            info += "   _Meme coin_ 🐕\n"
        if _type["nft"]:
            info += "   _NFT_ 🖼\n"
        if _type["giveaway"]:
            info += "   _Giveaways_ 🎁\n"
            
        return info
    
@dataclass
class refusedCampaign:
    id_campaign: str = None
    x_url: str = None
    tm_username: str = None
    tm_id: str = None
    budget: float = None
    is_refund: bool = None
    wallet: str = None
    
    def __str__(self):
        return f"@{self.tm_username} - {self.budget} $"
    
    def info(self):
        
        username = self.tm_username.replace("_", "\_")
        
        info = f"*Tm username*: @{username}\n"
        info += f"*Budget Left*: {self.budget} $\n"
        info += f"*Refunded*: {'YES' if self.is_refund else 'NO'}\n"
        info += f"*Wallet*: {self.wallet}\n"
            
        return info
      
@dataclass
class influencer:
    id_influencer: str = None
    x_name: str = None
    price: float = None
    tm_username: str = None
    tm_id: str = None
    wallet: str = None
    followers: int = None
    audience_type: int = None
    
    def __str__(self):
        return f"{self.x_name}-{self.price}"
    
    def info(self):
        
        username = self.tm_username.replace("_", "\_")
        x_name = self.x_name.replace("_", "\_")
        
        info = f"*Tm username*: @{username}\n"
        info += f"*X username*: {x_name}\n"
        info += f"*Price*: {self.price} $\n"
        info += f"*Wallet*: `{self.wallet}`\n"
        info += f"*Count Followers*: {self.followers}\n"
        info += f"*Audience type*:\n"
        
        _type = decode_type(self.audience_type)
                
        if _type["tech"]:
            info += "   _Tech project_ 👨‍💻\n"
        if _type["meme"]:
            info += "   _Meme coin_ 🐕\n"
        if _type["nft"]:
            info += "   _NFT_ 🖼\n"
        if _type["giveaway"]:
            info += "   _Giveaways_ 🎁\n"
                        
        return info
        
def format_number(number : int):
    return f"{number:,}".replace(",", ".")
    
class Stater(StatesGroup):
    ask_price = State()

@form_router.message(CommandStart())
async def admin_pannel(message: Message, state: FSMContext, edit=False):
    
    
    
    if not edit:
        
        if (message.from_user.username != "automate_y") and (message.from_user.username != "jasonads24"):
            print(f"[+] {message.from_user.username} Not allowed")
            return
    
    msg = "*Admin Dashboard* 👨‍🏫\n\n"
    
    msg += "► *Info Influencer*\n\n"
    msg += " → _Total Followers_: `{}`\n".format(format_number(Influencer.get_total_followers()))
    msg += " → _Total Price_: `{}`$\n".format(format_number(int(Influencer.get_total_price())))
    
    
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Campaigns 🚀", callback_data='campaign')
    mk_b.button(text="Influenceurs 👨‍🚀", callback_data='influencer')
    mk_b.button(text="Affiliate", callback_data='affiliate')
    #mk_b.button(text="[TEST] Delete All Validation ", callback_data='delete_validation')
    mk_b.button(text="Quit 🫡", callback_data="quit")
    
    mk_b.adjust(1, )
    
    if edit:
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    else:
        await message.answer(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
    
async def list_data_pannel(message: Message, state: FSMContext, current_page : int):
    
    cache_data = await state.get_data()
    
    text = cache_data["msg"]
    data = cache_data["buttons"]
    callbacks = cache_data["callbacks"]
    back_callback = cache_data["back_callback"]
    
    max_count = 5
    
    length = len(data)
    total_page = math.ceil(length / max_count)
    
    if total_page == 0:
        
        msg = text + f"\n\npage {current_page} / {total_page}"
    else:
        msg = text + f"\n\npage {current_page+1} / {total_page}"
    
    mk_b = InlineKeyboardBuilder()
    
    start_index = current_page*5
    end_index   = current_page*5+5 if current_page*5+5 <= length else length
    
    
    for i in range(start_index, end_index):
        mk_b.button(text=data[i], callback_data=callbacks[i])
        
    
    if current_page == 0:
        mk_b.button(text=" ", callback_data="None")
    else:
        mk_b.button(text="◀", callback_data=f"before:{(current_page)}")
        
    if current_page + 1 == total_page or total_page == 0:
        mk_b.button(text=" ", callback_data="None")
    else:
        mk_b.button(text="▶", callback_data=f"next:{current_page}")
        
    mk_b.button(text="Back", callback_data=back_callback)
    
    length_btn = end_index - start_index 
    adjustment = [1 for _ in range(length_btn)] + [2, 1]
    mk_b.adjust(*adjustment)
    
    await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
@form_router.callback_query()
async def callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    message = call.message
    data = call.data  
    
    if data.split(":")[0] == "back":
        endpoint = data.split(":")[1]
        
        if endpoint == "admin":
            await admin_pannel(message, state, True)
    
    if data.split(":")[0] == "before":
        current_page = int(data.split(":")[1])
        await list_data_pannel(message, state, current_page-1)
    
    if data.split(":")[0] == "next":
        current_page = int(data.split(":")[1])
        await list_data_pannel(message, state, current_page+1)
    
    if data == "delete":
        await message.delete()
        
    if data == "quit":
        await message.delete()
        await state.clear()
    
    if data == "delete_validation":
        Validation.delete_all()
        
        mk_b = InlineKeyboardBuilder()
        
        mk_b.button(text="Back", callback_data='back:admin')
        
        mk_b.adjust(1, )
        
        await message.edit_text("_All Validation DELETE_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)    
    
    if data == "campaign":
        print("[+] Campaigns pannel")
        msg = "*Campaigns Pannel*\n\n"
        
        count_pending = PendingCampaign.count()
        count_running = Campaign.count_running()
        count_finished = Campaign.count_finished()
        count_refused = RefusedCampaign.count()
        
        btn_pending = f"Pending ({count_pending})"
        btn_running = f"Running ({count_running})"
        btn_finished = f"Finished ({count_finished})"
        btn_refused = f"Refused ({count_refused})"
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=btn_pending, callback_data='list_pending')
        mk_b.button(text=btn_running, callback_data='list_running')
        mk_b.button(text=btn_finished, callback_data='list_finished')
        mk_b.button(text=btn_refused, callback_data='list_refused')
        mk_b.button(text="Back", callback_data='back:admin')
        
        mk_b.adjust(1, )
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data == "list_pending":
        print("[+] Campaign List Pending")
        
        p_camp_all = PendingCampaign.get_all()
        
        campaigns = [str(pendingCampaign(*pc)) for pc in p_camp_all]
        callbacks = ["p_camp:" + pendingCampaign(*pc).id_campaign for pc in p_camp_all]
        
        await state.update_data(msg="*List Pensing Campaign*")
        await state.update_data(buttons=campaigns)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="campaign")
        
        await list_data_pannel(message, state, 0)
        
  
    if data.split(":")[0] == "p_camp":
        print("[+] Pending Campain")
        
        id_campaign = data.split(":")[1]
        
        p_camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
        
        msg = p_camp.info()
        
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Validate", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"validate_camp:{id_campaign}")
        mk_b.button(text="No", callback_data=f"refuse_camp:{id_campaign}")
        mk_b.button(text="Back", callback_data="list_pending")
        
        mk_b.adjust(1, 2, 1)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data.split(":")[0] == "validate_camp":
        
        id_campaign = data.split(":")[1]
    
        p_camp = campaign(*PendingCampaign.validate(id_campaign))
            
        msg = channel_msg.format(p_camp.x_url, p_camp.budget)
            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text='➡ CLICK TO START', url="https://t.me/influfun_bot?start={}".format(id_campaign))   
                            
        # Send campaign in channel               
        async with Bot(token=token_bot_campaign) as bot:
            
            image = FSInputFile(path_img_running_campaign)
            
            msg = await bot.send_photo("-1002245377748", photo=image, caption=msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
            
        Campaign.update_msg_id(id_campaign, msg.message_id)
            
        # Notify the client
        if p_camp.tm_id:
                
            async with Bot(token=token_bot_client) as bot:
                                    
                image = FSInputFile(path_validated_campaign)
                msg_caption = message_congratulation_campaign.format(p_camp.tm_username.replace("_", "\_"))

                await bot.send_photo(p_camp.tm_id, photo=image, caption=msg_caption, parse_mode=ParseMode.MARKDOWN)
                    
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_pending")
         
        await message.edit_text("*Campaign Validated*\n\n_The client has been notified_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "refuse_camp":
        
        id_campaign = data.split(":")[1]
        
        p_camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
            
        if Checker.is_affiliated(p_camp.id_campaign):
            Affiliation.delete_from_id_campaign(id_campaign)
            
        PendingCampaign.refuse(id_campaign)
        PendingCampaign.delete_from_id(id_campaign)
            
            
        # Notify the client
        if p_camp.tm_id:
                
            async with Bot(token=token_bot_client) as bot:
                                    
                image = FSInputFile(path_validated_campaign)
                
                mk_b = InlineKeyboardBuilder()
                mk_b.button(text="Start Refund", callback_data=f"refund:{p_camp.id_campaign[0:8]}")
            
                #await bot.send_message(p_camp.tm_id, "Your campaing hasn't been validated. Please send your wallet")
                await bot.send_message(p_camp.tm_id, f"Your campaing hasn't been validated. Please click here for starting the refund process: ", parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
                
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_pending")
         
        await message.edit_text("*Campaign Refused*\n\n_The client has been notified_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
        
    if data == "list_running":
        print("[+] Campaign List Running")
        
        camp_all = Campaign.get_all_running()
        
        campaigns = [str(campaign(*camp)) for camp in camp_all]
        callbacks = ["camp_running:" + campaign(*camp).id_campaign for camp in camp_all]
        
        await state.update_data(msg="*List Running Campaign*")
        await state.update_data(buttons=campaigns)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="campaign")
        
        await list_data_pannel(message, state, 0)
           
    if data.split(":")[0] == "camp_running":
        id_campaign = data.split(":")[1]
        
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        msg = "*Running Campaign*\n\n"
        msg += camp.info()
        
        count = Validation.count_validated_campaign(id_campaign)
        
        msg += f"\n*Validations Count*: {count}"
        
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Finish", callback_data=f"end_camp:{id_campaign}:0")
        mk_b.button(text="Back", callback_data="list_running")
        
        mk_b.adjust(1,)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    
    if data.split(":")[0] == "end_camp":
        id_campaign = data.split(":")[1]
        flag_verif = int(data.split(":")[2])
                
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        msg = "*FINISHING the Campaign*\n\n"
        msg += camp.info()
        
        count = Validation.count_validated_campaign(id_campaign)
        
        msg += f"\n*Validations Count*: {count}"
        
        if not flag_verif:
            
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="Are you sure ?", callback_data="None")
            mk_b.button(text="Yes", callback_data=f"end_camp:{id_campaign}:1")
            mk_b.button(text="No", callback_data=f"camp_running:{id_campaign}")
            mk_b.button(text="Back", callback_data=f"camp_running:{id_campaign}")
            
            mk_b.adjust(1, 2, 1)
            
        else:
            Campaign.update_finished(id_campaign, 1)
            
            msg +=  "\n\nCampaign FINISHED"
            
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="Back", callback_data=f"camp_running:{id_campaign}")
            
            Campaign.update_finished(id_campaign, True)
            
            channel_message_upt = channel_msg_complete.format(camp.x_url) 
                    

            async with Bot(token=token_bot_campaign) as bot:
                new_photo = FSInputFile(path_img_end_campaign)
                media = InputMediaPhoto(media=new_photo, caption=channel_message_upt, parse_mode=ParseMode.MARKDOWN)
                                
                await bot.edit_message_media(chat_id="-1002245377748", message_id=camp.id_message, media=media)
            
            
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
        
    
    if data == "list_finished":
        camp_all = Campaign.get_all_finished()
        
        campaigns = [str(campaign(*camp)) for camp in camp_all]
        callbacks = ["camp_finished:" + campaign(*camp).id_campaign for camp in camp_all]
        
        await state.update_data(msg="*List Finished Campaign*")
        await state.update_data(buttons=campaigns)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="campaign")
        
        await list_data_pannel(message, state, 0)
    
    if data.split(":")[0] == "camp_finished":
        id_campaign = data.split(":")[1]
        
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        msg = "*Finished Campaign*\n\n"
        msg += camp.info()
        
        count = Validation.count_validated_campaign(id_campaign)
        
        msg += f"\n*Validations Count*: {count}"
        
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_finished")
        

        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
    if data == "list_refused":
        print("[+] Campaign List Refused")
        
        camp_all = RefusedCampaign.get_all()
        
        campaigns = [str(refusedCampaign(*camp)) for camp in camp_all]
        callbacks = ["r_camp:" + refusedCampaign(*camp).id_campaign for camp in camp_all]
        
        await state.update_data(msg="*List Refused Campaign*")
        await state.update_data(buttons=campaigns)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="campaign")
        
        await list_data_pannel(message, state, 0)
      
    if data.split(":")[0] == "r_camp":
        id_campaign = data.split(":")[1]
        
        camp = refusedCampaign(*RefusedCampaign.get_from_id(id_campaign))
        
        msg = "*Refused Campaign*\n\n"
        msg += camp.info()
                
        mk_b = InlineKeyboardBuilder()
        if camp.wallet == "None" and camp.is_refund == 0:
            mk_b.button(text="Request Wallet", callback_data=f"request_wallet:{id_campaign}")
        elif camp.wallet != "None" and camp.is_refund == 0:
            mk_b.button(text="Validate Refund", callback_data=f"val_refund:{id_campaign}")

        mk_b.button(text="Back", callback_data="list_refused")
        
        mk_b.adjust(1,)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "request_wallet":
        id_campaign = data.split(":")[1]
        
        camp = refusedCampaign(*RefusedCampaign.get_from_id(id_campaign)) 
        
        
        if camp.tm_id:
                
            async with Bot(token=token_bot_client) as bot:
                                    
                image = FSInputFile(path_validated_campaign)
                
                mk_b = InlineKeyboardBuilder()
                mk_b.button(text="Start Refund", callback_data=f"refund:{camp.id_campaign[0:8]}")
            
                await bot.send_message(camp.tm_id, f"Your campaing hasn't been validated. Please click here for starting the refund process: ", parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
                
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_refused")
        
        await message.edit_text("_Request sent_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
     
    if data.split(":")[0] == "val_refund":
        id_campaign = data.split(":")[1]  
                        
        camp = refusedCampaign(*RefusedCampaign.get_from_id(id_campaign))
        
        msg = "*Campaign Refund*\n\n"
        msg += camp.info()
        mk_b = InlineKeyboardBuilder()
        
        mk_b.button(text="? Are You Sure ?", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"validate_refund_forever:{id_campaign}")
        mk_b.button(text="No", callback_data="list_refused")
        
        mk_b.adjust(1, 2, 1)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)

    if data.split(":")[0] == "validate_refund_forever":
        id_campaign = data.split(":")[1]
        
        RefusedCampaign.update_refund(id_campaign, 1)
        
        msg = "*Refund Validated*"
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_refused")
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    
    if data == "influencer":
        print("[+] Influencers pannel")
        
        msg = "*Influencers Pannel*\n\n"
        
        count_pending = PendingInfluencer.count()
        count_accepted = Influencer.count()
        count_waiting_paiement = Validation.count_waiting_for_paiement()

        
        btn_pending = f"Pending ({count_pending})"
        btn_accepted = f"Accepted ({count_accepted})"
        
        if count_waiting_paiement > 0:
            warning = "⚠ "
        else:
            warning = ""
        
        btn_waiting_paiement = warning + f"Waiting Paiement ({count_waiting_paiement})"
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=btn_pending, callback_data='list_influencer_pending')
        mk_b.button(text=btn_accepted, callback_data='list_influencer')
        mk_b.button(text=btn_waiting_paiement, callback_data='list_influencer_waiting_paiement')
        mk_b.button(text="Add", callback_data='add_influencer')
        mk_b.button(text="Delete", callback_data='delete_influencer')
        mk_b.button(text="Back", callback_data='back:admin')
        
        mk_b.adjust(1, 1, 1, 2, 1)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data == "list_influencer_pending":
        print("[+] Influencer List Pending")
        
        p_inf_all = PendingInfluencer.get_all()

        _influencers = [str(influencer(*inf)) for inf in p_inf_all]
        callbacks = ["p_inf:" + influencer(*inf).id_influencer for inf in p_inf_all]
                
        await state.update_data(msg="*Pending Influencers List*")
        await state.update_data(buttons=_influencers)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="influencer")
        
        await list_data_pannel(message, state, 0)
    
    if data.split(":")[0] == "p_inf":
        id_influencer = data.split(":")[1]
        
        inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        
        msg = "Pending Influencers\n\n"
        msg += inf.info()
                        
        
        mk_b = InlineKeyboardBuilder()
        
        mk_b.button(text="Validate", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"validate_inf:{id_influencer}")
        mk_b.button(text="No", callback_data=f"refuse_inf:{id_influencer}")
        mk_b.button(text="Propose Price", callback_data=f"propose_price:{id_influencer}")
        mk_b.button(text="Back", callback_data="list_influencer_pending")
        
        mk_b.adjust(1, 2, 1, 1)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "validate_inf":
        id_influencer = data.split(":")[1]
        
        p_inf = influencer(*PendingInfluencer.validate(id_influencer))
        
        
        async with Bot(token=token_bot_campaign) as bot:
            chat_invite = await bot.create_chat_invite_link(chat_id="-1002245377748", name="invite", member_limit=1)
            
        async with Bot(token=token_bot_client) as bot:
                                                            
            image = FSInputFile(path_img_influ_accepted)
            
            await bot.send_photo(p_inf.tm_id, photo=image, caption=message_congratulation_influencer.format(chat_invite.invite_link), parse_mode=ParseMode.MARKDOWN)
                        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_influencer_pending")
         
        await message.edit_text("*Influencer Validated*\n\n_The client has been notified_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN_V2)
    
    if data.split(":")[0] == "refuse_inf":
        id_influencer = data.split(":")[1]
            
            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Are you sure ?", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"confirm_r_inf:{id_influencer}")
        mk_b.button(text="No", callback_data=f"list_influencer_pending")
        
        mk_b.adjust(1, 2)
         
        await message.edit_text("*Influencer Refusing Verification*", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    # TODO!
    # Security Refuse influencer pending
    
    if data.split(":")[0] == "confirm_r_inf":
        id_influencer = data.split(":")[1]
        
        p_inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        
        PendingInfluencer.delete_from_id(id_influencer)
        
        async with Bot(token=token_bot_client) as bot:
                                                            
            await bot.send_message(p_inf.tm_id, "Sorry your influencer profile hasn't been approved", parse_mode=ParseMode.MARKDOWN)
            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data=f"list_influencer_pending")
            
        await message.edit_text("*Influencer Refused*\n\n_The client has been notified_", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
    if data.split(":")[0] == "propose_price":
        id_influencer = data.split(":")[1]
        
        await state.update_data(id_influencer=id_influencer)
        
        inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        

        await state.set_state(Stater.ask_price)
        await state.update_data(id_influencer=id_influencer)
        await state.update_data(msg_ref=message)
        
        await message.edit_text(f"Send the new price\n\nPrevious: {inf.price}")
    
    if data == "confirm_price":
        
        cache_data = await state.get_data()
        
        id_influencer = cache_data["id_influencer"]
        inf = influencer(*PendingInfluencer.get_from_id(id_influencer)) 
                
        new_price = cache_data["new_price"]
        msg_ref = cache_data["msg_ref"]
        
        await msg_ref.delete()

     
        if inf.tm_id:
                
            async with Bot(token=token_bot_client) as bot:
                                    
                #image = FSInputFile(path_validated_campaign")
                
                mk_b = InlineKeyboardBuilder()
                mk_b.button(text="Accept the new price", callback_data=f"accept:{new_price}:{id_influencer}")
                mk_b.button(text="Propose a new price", callback_data=f"ask_price:{new_price}:{id_influencer}")
                
                mk_b.adjust(1,)
            
                await bot.send_message(inf.tm_id, f"Your Influencer's profile is still pending. We propose you a new price: {new_price}. Do you accept it ? ", parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
                
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_influencer_pending")
                
        await message.edit_text("*New price sent to the customer*", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    
    if data == "list_influencer":
        print("[+] Influencer List")
        
        inf_all = Influencer.get_all()
        
        _influencers = [str(influencer(*inf)) for inf in inf_all]
        callbacks = ["inf:" + influencer(*inf).id_influencer for inf in inf_all]
        
        await state.update_data(msg="*Influencers List*")
        await state.update_data(buttons=_influencers)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="influencer")
        
        await list_data_pannel(message, state, 0)
        
    if data.split(":")[0] == "inf":
        id_influencer = data.split(":")[1]
        
        inf = influencer(*Influencer.get_from_id(id_influencer))
        
        msg = "*Influencers*\n\n"
        msg += inf.info()
        
        total_validation = Validation.count_campaign_from_influencer(id_influencer)
        msg += f"*Total Validation*: {total_validation}\n"
        
        total_affiliation = Affiliation.count_referended(id_influencer)
        msg += f"*Total Affiliation*: {total_affiliation}\n"

        waiting_paiement_campaign = Checker.is_waiting_for_paiement_campaign(id_influencer)
        waiting_paiement_affiliate = Checker.is_waiting_for_paiement_affiliate(id_influencer)
        
        msg += "*Is waiting for paiement*:\n"
        msg += f"    • _Campaign_: {'YES' if waiting_paiement_campaign else 'NO'}\n"
        msg += f"    • _Affiliation_: {'YES' if waiting_paiement_affiliate else 'NO'}\n"
                        
        mk_b = InlineKeyboardBuilder()
        
        await state.update_data(callback="list_influencer")
        
        mk_b.button(text="Delete", callback_data=f"inf_delete:{id_influencer}")
        mk_b.button(text="Back", callback_data="list_influencer")
        
        mk_b.adjust(1,)
                
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data.split(":")[0] == "inf_delete":
                        
        id_influencer = data.split(":")[1]
        
        callback = (await state.get_data())["callback"]
        
        inf = influencer(*Influencer.get_from_id(id_influencer))
        
        msg = "*Influencer Deletion*\n\n"
        msg += inf.info()
        mk_b = InlineKeyboardBuilder()
        
        mk_b.button(text="? Are You Sure ?", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"inf_delete_forever:{id_influencer}")
        mk_b.button(text="No", callback_data=callback)
        
        mk_b.adjust(1, 2, 1)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data.split(":")[0] == "inf_delete_forever":
                        
        id_influencer = data.split(":")[1]
        
        callback = (await state.get_data())["callback"]
                
        inf = influencer(*Influencer.get_from_id(id_influencer))
        Influencer.delete_from_id(id_influencer)
        
        if Checker.is_referent(id_influencer):
            Affiliation.delete_from_id_influencer(id_influencer)
            
        
        async with Bot(token=token_bot_client) as bot:
                                                            
            await bot.send_message(inf.tm_id, "Sorry your influencer profile has been delete.", parse_mode=ParseMode.MARKDOWN)
            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data=callback)
            
        await message.edit_text("*Influencer deleted*", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
        
    if data == "list_influencer_waiting_paiement":
                
        ids = Validation.get_id_influ_campaign_wating_for_paiement()
        
        inf_all = []
        camp_all = []
        for _id in ids:
            inf_all.append(Influencer.get_from_id(_id[0]))
            camp_all.append(Campaign.get_from_id(_id[1]))
                        
            
        _influencers = [str(influencer(*inf)) for inf in inf_all]
        callbacks = [f"inf_wp:{i}" for i in range(len(ids))]
        
        await state.update_data(msg="*Influencers List Waiting for Paiement*")
        await state.update_data(buttons=_influencers)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="influencer")
        
        await list_data_pannel(message, state, 0)
        
    if data.split(":")[0] == "inf_wp":
        indx = int(data.split(":")[1])
        
        ids = Validation.get_id_influ_campaign_wating_for_paiement()
        
        inf = influencer(*Influencer.get_from_id(ids[indx][0]))
        camp = campaign(*Campaign.get_from_id(ids[indx][1]))
        
        msg = "*Influencers*\n\n"
        msg += inf.info()
        msg += "\n\n*Campaign*\n\n"
        msg += camp.info()
        
        
        msg += f"\n\n*Influencer Validation*"        
        msg += f"\n\n*Paiement*: `{inf.price*0.9}`$\n"
        msg += f"*Wallet*: `{inf.wallet}`\n"
                        
        mk_b = InlineKeyboardBuilder()
                
        mk_b.button(text="Validate Paiement", callback_data=f"conf_pm:{indx}")
        mk_b.button(text="Back", callback_data="list_influencer_waiting_paiement")
        
        mk_b.adjust(1,)
                
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "conf_pm":
        indx = int(data.split(":")[1])
        
        ids = Validation.get_id_influ_campaign_wating_for_paiement()
        
        inf = influencer(*Influencer.get_from_id(ids[indx][0]))
        camp = campaign(*Campaign.get_from_id(ids[indx][1]))

        
        msg = "Validate the paiement ?"
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Yes", callback_data=f"conf_paie_forever:{indx}")
        mk_b.button(text="Back", callback_data=f"list_influencer_waiting_paiement")
        
        mk_b.adjust(1,)

        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
    
    if data.split(":")[0] == "conf_paie_forever":
        indx = int(data.split(":")[1])
        
        ids = Validation.get_id_influ_campaign_wating_for_paiement()
        
        inf = influencer(*Influencer.get_from_id(ids[indx][0]))
        camp = campaign(*Campaign.get_from_id(ids[indx][1]))
        
        
        Validation.update_paid(camp.id_campaign, inf.id_influencer, 1)
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_influencer_waiting_paiement")        
        
        await message.edit_text("*Paiement Updated*", reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    #TODO
    if data == "add_influencer":
        pass    
    
    if data == "delete_influencer":
        print("[+] Influencer List to Delete")
        
        inf_all = Influencer.get_all()
        
        _influencers = [str(influencer(*inf)) for inf in inf_all]
        callbacks = ["inf_delete:" + influencer(*inf).id_influencer for inf in inf_all]
        
        await state.update_data(msg="*Influencers List to Delete*")
        await state.update_data(buttons=_influencers)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="influencer")
        
        await state.update_data(callback="delete_influencer")
        
        await list_data_pannel(message, state, 0)
        
        
    if data == "affiliate":
        print("[+] Affiliate pannel")
        msg = "*Affiliate Pannel*\n\n"
        
        count_affiliated_influencers = Affiliation.count_influencers()
        count_affiliated_campaigns = Affiliation.count_campaigns()
        count_affiliated_waiting_paiement = Affiliation.count_waiting_for_paiement()

        btn_affiliated_influencers = f"Influencers ({count_affiliated_influencers})"
        btn_affiliated_campaigns = f"Campaigns ({count_affiliated_campaigns})"
        
        if count_affiliated_waiting_paiement:
            warning = "⚠ "
        else:
            warning = ""
            
        btn_affiliated_waiting_paiement = warning + f"Waiting Paiement ({count_affiliated_waiting_paiement})"
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text=btn_affiliated_influencers, callback_data='list_affiliated_influencer')
        mk_b.button(text=btn_affiliated_campaigns, callback_data='list_affiliated_campaigns')
        mk_b.button(text=btn_affiliated_waiting_paiement, callback_data='list_affiliated_waiting_paiement')
        mk_b.button(text="Back", callback_data='back:admin')
        
        mk_b.adjust(1,)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data == "list_affiliated_influencer":
        val_all = Affiliation.get_all()
        
        ids_influencer = list(set([val[0] for val in val_all]))
                
        inf_all = []
        for _id in ids_influencer:
            
            inf_all.append(Influencer.get_from_id(_id))
        
        _influencers = [str(influencer(*inf)) + f" ({Affiliation.count_campaign_from_influencer(influencer(*inf).id_influencer)})" for inf in inf_all]
        callbacks = ["inf_affiliation:" + influencer(*inf).id_influencer for inf in inf_all]
        
        await state.update_data(msg="*Influencers with affiliations*")
        await state.update_data(buttons=_influencers)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="affiliate")
        
        await list_data_pannel(message, state, 0)
    
    
    # TODO
    if data.split(":")[0] == "inf_affiliation":
        id_influencer = data.split(":")[1]
        
    
    # TODO
    if data == "list_affiliated_campaigns":
        print("[+] List Affiliated Campaigns")
        
        aff_all = Affiliation.get_all()
        
        ids_campaign = [aff[1] for aff in aff_all]
        
        camp_all = []
        for _id in ids_campaign:
            camp_all.append(Campaign.get_from_id(_id))
        
        _campaigns = [str(campaign(*camp)) for camp in camp_all]
        callbacks = ["camp_aff:" + campaign(*camp).id_campaign for camp in camp_all]
        
        await state.update_data(msg="*Campaigns with affiliations*")
        await state.update_data(buttons=_campaigns)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="affiliate")
        
        await list_data_pannel(message, state, 0)
        
    # TODO
    if data.split(":")[0] == "camp_aff":
        id_influencer = data.split(":")[1]
        
        id_campaign = data.split(":")[1]
        
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        if int(camp.is_finished) == 1:
        
            msg = "_Finished_ *Campaign*\n\n"
            
        else:
            
            msg =  "_Finished_ *Campaign*\n\n"
        msg += camp.info()
        
        count = Validation.count_validated_campaign(id_campaign)
        
        msg += f"\n*Validations Count*: {count}"
        
        
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text="Back", callback_data="list_affiliated_campaigns")
        

        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
             
             
    if data == "list_affiliated_waiting_paiement":
    
        ids_ = Affiliation.get_influencers_campaign_finished_not_paid()
        
        
        print(ids_)
        
        _influencer = [str(influencer(*Influencer.get_from_id(id_[0]))) for id_ in ids_]
        callbacks = [f"inf_af_wp:{indx}:0" for indx in range(len(ids_))]
        
        await state.update_data(ids=ids_)
        
        await state.update_data(msg="*Influencers Waiting for Paiement*")
        await state.update_data(buttons=_influencer)
        await state.update_data(callbacks=callbacks)
        await state.update_data(back_callback="affiliate")

        
        await list_data_pannel(message, state, 0)
    
    
    # TODO
    if data.split(":")[0] == "inf_af_wp":
        indx = int(data.split(":")[1])
        flag_verif = int(data.split(":")[2])

        
        try:
            ids_ = (await state.get_data())["ids"]
        except KeyError:
            await message.delete()
            await message.answer("The bot probably reset, please retry")
            return
        
        id_influencer = ids_[indx][0]
        id_campaign = ids_[indx][1]
        
        inf = influencer(*Influencer.get_from_id(id_influencer))
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        msg = "*Influencer*\n\n"
        msg += inf.info()
        
        total_affiliation = Affiliation.count_referended(id_influencer)
        msg += f"*Total Affiliation*: {total_affiliation}\n"
        
        camp = campaign(*Campaign.get_from_id(id_campaign))
        
        msg += "\n*Campaign*\n\n"
        msg += camp.info()
        
        msg += f"\n\n*Affiliation*"
        msg += f"\n\n*Amount*: `{camp.budget*0.1*0.5}`$" #50% des 10% du total
        msg += f"\n*Wallet*: `{inf.wallet}`\n"
        
        
        if not flag_verif:
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="Validate Paiement", callback_data=f"inf_af_wp:{indx}:1")
            mk_b.button(text="Back", callback_data="list_affiliated_waiting_paiement")
            mk_b.adjust(1,)
            
        elif flag_verif == 1:
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="Are you sure ?", callback_data="None")
            mk_b.button(text="yes", callback_data=f"inf_af_wp:{indx}:2")
            mk_b.button(text="no", callback_data=f"inf_af_wp:{indx}:0")
            mk_b.button(text="back", callback_data=f"list_affiliated_waiting_paiement")
            mk_b.adjust(1,2,1)
        
        elif flag_verif == 2:
            
            msg = "*Affiliation Paiement Updated*"
            
            Affiliation.update_is_paid(id_influencer, id_campaign, 1)
            
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text="Back", callback_data=f"list_affiliated_waiting_paiement")
            mk_b.adjust(1,)
        
        await message.edit_text(msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
        
    if data.split(":") == "val_paiement":
        flag_validation = data.split(":")[1]


@form_router.message(Stater.ask_price)
async def ask_price(message: Message, state: FSMContext):
    
    def is_convertible_to_int(text: str) -> bool:
        try:
            int(text)
            return True
        except ValueError:
            return False
        
    if not is_convertible_to_int(message.text):
        await message.answer("Please send a valid number")
        return
    
    new_price = message.text
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text="Yes", callback_data="confirm_price")
    mk_b.button(text="No", callback_data="delete")
    
    await state.update_data(new_price=new_price)
    
    await message.delete()
    await message.answer(f"Validate the new price: {new_price}", reply_markup=mk_b.as_markup())
        
 
async def main():

    await asyncio.gather(dp.start_polling(bot))
    


if __name__ == "__main__":    
    logging.basicConfig(level=logging.INFO)

    asyncio.get_event_loop().run_until_complete(main())
    

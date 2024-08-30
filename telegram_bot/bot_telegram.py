from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message, CallbackQuery, FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode
from aiogram.filters.command import Command, CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.link_preview_options import LinkPreviewOptions
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


import signal
import asyncio
import websockets
import json
import subprocess

import logging

from sys import path
import os
path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.db import Campaign, PendingCampaign, Influencer, PendingInfluencer, Validation, PendingValidation, Checker, Affiliation

from pprint import pprint

from utils.messages import *
from utils.paths import *
from config.token import *


bot = Bot(token=token_bot_campaign)

form_router = Router()
dp = Dispatcher()
dp.include_router(form_router)

# Admin command

from dataclasses import dataclass
    
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
        return f"{self.tm_username} - {self.x_name} - {self.price} - {self.wallet}"
    
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
    
@dataclass
class validation:
    id_campaign: str = None
    id_influencer: str = None
    is_paid: bool = None


def influencer_verification(tm_username):
    print("[+] Influencer Verification")
    res = Influencer.get_from_tm_name(tm_username)

    if res:
        return True
    else:
        return False

class FormVerification(StatesGroup):
    verification = State()

@form_router.message(CommandStart())
async def send_message(message: Message, state: FSMContext):
    command_text = message.text.split()
            
    if not influencer_verification(message.from_user.username):
        await message.answer("You are not allowed to use this bot")
        return
    
    if len(command_text) == 1:
        await message.answer("No campaign associated")
        return
    
    else:
        
        await state.set_state(FormVerification.verification)
        
        camp = campaign(*Campaign.get_from_id(command_text[-1]))
        inf = influencer(*Influencer.get_from_tm_name(message.from_user.username))
        
        if Validation.check(camp.id_campaign, inf.id_influencer):
            await message.answer("You have already completed this campaign")
            return
        
        if not Checker.budget(camp.id_campaign, inf.id_influencer):
            await message.answer("Not enough budget left for your price")
            return

            
        mk_b = InlineKeyboardBuilder()
        mk_b.button(text='⏳VERIFICATION 🧐', callback_data=f'verif:{camp.id_campaign}:{inf.tm_username}')

        
        image = FSInputFile(path_img_validation_campaign)

        await message.delete()
        await message.answer_photo(photo=image, 
                                    caption=campaign_msg.format(message.from_user.first_name, camp.x_url), 
                                    reply_markup=mk_b.as_markup(), 
                                    parse_mode=ParseMode.MARKDOWN)
                    
        #await message.answer(text=msg, parse_mode=ParseMode.MARKDOWN_V2, reply_markup=mk_b.as_markup())
            
    
@form_router.callback_query()
async def callback_handler(call: CallbackQuery, state: FSMContext):
    await call.answer()
    message = call.message
    data = call.data    
    
    if data.split(":")[0] == "verif":
        
        print("[+] Verification Asked")
        
        id_campaign = data.split(":")[1]
        tm_username = data.split(":")[2]
        
        
        camp = campaign(*Campaign.get_from_id(id_campaign))
        inf = influencer(*Influencer.get_from_tm_name(tm_username))


        new_photo = FSInputFile(path_img_validation_campaign)
        media = InputMediaPhoto(media=new_photo, caption="You are now in the waiting list for the verification... ⏳\n\nYou will be notified soon ;)", parse_mode=ParseMode.MARKDOWN)
                                            
        await message.edit_media(media=media, parse_mode=ParseMode.MARKDOWN)
                
        #await message.edit_text("[+] You are now in the waiting list for the verification... ⏳\n\nYou will be notified soon ;)")
        
        PendingValidation.add(camp.id_campaign, inf.id_influencer)


    if data == "view_influencers":
        data = Influencer.get_all()        
        
        influencers = ""
        for influ in data:
            i = influencer(*influ)
            influencers += str(i) + "\n"
            
        await message.answer(influencers)
        
    if data == "view_campaigns":
        data = Campaign.get_all()
        
        campaigns = ""
        for camp in data:
            c = campaign(*camp)
            campaigns += str(c) + "\n"
            
        await message.answer(campaigns, parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True))
        
    if data == "view_pending_campaigns":
        all_pending_camp = PendingCampaign.get_all()
        
        mk_b = InlineKeyboardBuilder()
        
        for p_camp in all_pending_camp:
            pc = campaign(*p_camp)
            
            callback_data = f"pending_camp:{pc.id_campaign}"
            content = str(pc)

            mk_b.button(text=content, callback_data=callback_data)
            
        mk_b.adjust(1,)
            
        await message.answer("Choose a campaigns", parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=mk_b.as_markup())
        
    if data == "view_pending_influencers":
        all_pending_inf = PendingInfluencer.get_all()
        
        mk_b = InlineKeyboardBuilder()
        
        for p_inf in all_pending_inf:
            pi = influencer(*p_inf)
            
            callback_data = f"pending_influencer:{pi.id_influencer}"
            content = str(pi)

            mk_b.button(text=content, callback_data=callback_data)
            
        mk_b.adjust(1,)
            
        await message.answer("Choose an influencer", parse_mode=ParseMode.MARKDOWN, link_preview_options=LinkPreviewOptions(is_disabled=True), reply_markup=mk_b.as_markup())
        
    if data == "view_validated":
        
        val  = Validation.get_all()
        
        answer = "Influencer - Price - Is Paid\n\n"
        
        for v in val:
            _v_ = validation(*v)
            
            inf  = influencer(*Influencer.get_from_id(_v_.id_influencer))
            camp = campaign(*Campaign.get_from_id(_v_.id_campaign))
            
            has_been_paid = "✅" if _v_.is_paid else "❌"
            
            answer += f"@{str(inf.tm_name)} - {inf.price} - {has_been_paid}\n"
                        
        await message.answer(answer)
        
    if data == "add_influencer":
        
        await state.set_state(Form.x_name)
        await message.answer("Send the X name (Start with @)")
        
    if data == "add_influ_yes":
        
        influ_data = await state.get_data()
        from uuid import uuid4

        Influencer.add(str(uuid4()), influ_data["x_name"], influ_data["price"], influ_data["tm_name"], "None", influ_data["wallet"])
        
        await state.clear()
        await message.edit_text("Influencer added !")
    
    if data == "add_influ_no":
        await state.clear()
        await message.delete()
        
        
        
    if data.split(":")[0] == "pending_camp":
        id_campaign = data.split(":")[1]
        
        p_camp = campaign(*PendingCampaign.get_from_id(id_campaign))
        
        msg_answer = message_answer_pending_campaign.format(p_camp.tm_username, p_camp.x_url, p_camp.budget)
        
        mk_b = InlineKeyboardBuilder()
         
        mk_b.button(text="? Validate ?", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"validate_camp:yes:{p_camp.id_campaign}")
        mk_b.button(text="No", callback_data=f"validate_camp:no:{p_camp.id_campaign}")
        
        mk_b.adjust(1, 2)
            
        await message.answer(msg_answer, reply_markup=mk_b.as_markup())
        
    if data.split(":")[0] == "pending_influencer":
        id_influencer = data.split(":")[1]
        
        p_inf = influencer(*PendingInfluencer.get_from_id(id_influencer))
        
        msg_answer = message_answer_pending_influencer.format(p_inf.x_name, p_inf.price, p_inf.tm_name, p_inf.wallet)
        
        mk_b = InlineKeyboardBuilder()
         
        mk_b.button(text="? Validate ?", callback_data="None")
        mk_b.button(text="Yes", callback_data=f"validate_inf:yes:{p_inf.id_influencer}")
        mk_b.button(text="No", callback_data=f"validate_inf:no:{p_inf.id_influencer}")
        
        mk_b.adjust(1, 2)
        
        await message.answer(msg_answer, reply_markup=mk_b.as_markup())
        
    if data.split(":")[0] == "validate_camp":
        id_campaign = data.split(":")[-1]
        
        
        if data.split(":")[1] == "no":
            p_camp = pendingCampaign(*PendingCampaign.get_from_id(id_campaign))
            
            if Checker.is_affiliated(p_camp.id_campaign):
                Affiliation.delete_from_id_campaign(id_campaign)
            
            PendingCampaign.refuse(id_campaign)
            
            await message.delete()
            await message.answer("The campaign has been deleted!")
            
            # Notify the client
            if p_camp.tm_id:
                
                async with Bot(token=token_bot_client) as bot:
                                    
                    image = FSInputFile(path_validated_campaign)
            
                    #await bot.send_message(p_camp.tm_id, "Your campaing hasn't been validated. Please send your wallet")
                    await bot.send_message(p_camp.tm_id, f"Your campaing hasn't been validated. Please click here for starting the refund process: [click](https://t.me/influ_fun_bot?start=refund-{p_camp.id_campaign[0:8]})", parse_mode=ParseMode.MARKDOWN)
                    
        
        elif data.split(":")[1] == "yes":
        
            p_camp = campaign(*PendingCampaign.validate(id_campaign))
            
            msg = channel_msg.format(p_camp.x_url, p_camp.budget)
            
            mk_b = InlineKeyboardBuilder()
            mk_b.button(text='➡ CLICK TO START', url="https://t.me/influfun_bot?start={}".format(id_campaign))   
                 
            
            async with Bot(token=token_bot_campaign) as bot:
            
                image = FSInputFile(path_img_running_campaign)
            
                msg = await bot.send_photo("-1002245377748", photo=image, caption=msg, reply_markup=mk_b.as_markup(), parse_mode=ParseMode.MARKDOWN)
            
            
            Campaign.update_msg_id(id_campaign, msg.message_id)
            
            # Notify the client
            if p_camp.tm_id:
                
                async with Bot(token=token_bot_client) as bot:
                                    
                    image = FSInputFile(path_validated_campaign)
            
                    await bot.send_photo(p_camp.tm_id, photo=image, caption=message_congratulation_campaign, parse_mode=ParseMode.MARKDOWN)
                    
            
            await message.delete()
            await message.answer("The campaign is now available!")
            
    if data.split(":")[0] == "validate_inf":
        id_influencer = data.split(":")[-1]
        
        
        if data.split(":")[1] == "no":
            PendingInfluencer.delete_from_id(id_influencer)
            
            await message.delete()
            await message.answer("The influencer has been deleted!")
        
        elif data.split(":")[1] == "yes":
        
            p_inf = influencer(*PendingInfluencer.validate(id_influencer))
            
            async with Bot(token=token_bot_campaign) as bot:
                chat_invite = await bot.create_chat_invite_link(chat_id="-1002245377748", name="invite", member_limit=1)
            
            async with Bot(token=token_bot_client) as bot:
                                                            
                image = FSInputFile(path_img_influ_accepted)
            
                await bot.send_photo(p_inf.tm_id, photo=image, caption=message_congratulation_influencer.format(chat_invite.invite_link), parse_mode=ParseMode.MARKDOWN)
                    
            
            await message.delete()
            await message.answer("The influencer has been added\n\nHe has been notify and He received an invitation link")
        
        
        

class Form(StatesGroup):
    x_name = State()
    price = State()
    tm_name = State()
    wallet = State()



@form_router.message(Form.x_name)
async def add_influ_name(message: Message, state: FSMContext):
    
    if "@" not in message.text:
        await message.answer("Please provide the name with @")
        return
    
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
    
    if "@" not in message.text:
        await message.answer("Please provide the name with @")
        return
    
    await state.update_data(tm_name=message.text)
    
    data = await state.get_data()
    
    print(data)    
    

    resume = f"""📢 New Influencer 🥳

*X username:* {data["x_name"]}
*Tm username:* {data["tm_name"]}

*Price:* {data["price"]} $
*Wallet:* {data["wallet"]}"""  
    
    mk_b = InlineKeyboardBuilder()
   
    mk_b.button(text="? Validate ?", callback_data="None")
    mk_b.button(text='Yes', callback_data='add_influ_yes')
    mk_b.button(text='No', callback_data='add_influ_no')

    mk_b.adjust(1, 2)
    
    await message.answer(resume, parse_mode=ParseMode.MARKDOWN, reply_markup=mk_b.as_markup())
    
    
@dp.message(Command("admin"))
async def admin_command(message: Message):
    
    print(message.from_user.username == "automate_y")
    
    if (message.from_user.username != "automate_y") and (message.from_user.username != "jasonads24"):
        print("Not allowed")
        return
    
    mk_b = InlineKeyboardBuilder()
    mk_b.button(text='View Pending Influencers', callback_data='view_pending_influencers')
    mk_b.button(text='View Influencers', callback_data='view_influencers')
    mk_b.button(text='View Pending Campaigns', callback_data='view_pending_campaigns')
    mk_b.button(text='View Campaigns', callback_data='view_campaigns')
    mk_b.button(text='View Validated', callback_data='view_validated')
    mk_b.button(text='Add Influencer', callback_data='add_influencer')
    
    
    mk_b.adjust(1,)
    
    await message.answer("Admin panel", reply_markup=mk_b.as_markup())
    
async def add_influencer(message: Message):
    
    await message.answer("Enter the influencer's data")
     
        
    
async def main():

    print("[+] Starting")
    await asyncio.gather(dp.start_polling(bot))#, socket_handler())
    


if __name__ == "__main__":    
    #logging.basicConfig(level=logging.INFO)

    asyncio.get_event_loop().run_until_complete(main())
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

from time import sleep
import json
import requests
import asyncio

from dataclasses import dataclass

from selenium.webdriver.chrome.options import Options

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import FSInputFile, InputMediaPhoto
from aiogram.enums import ParseMode

import asyncio
import json


from sys import path
import os

path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.db import Campaign, PendingCampaign, Influencer, PendingInfluencer, PendingValidation, pending_validation_t, Validation, Checker

from dataclasses import dataclass

from config.token import *
from utils.messages import *
from utils.paths import *
    
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
    

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

driver.get("https://x.com/")

driver.set_script_timeout(60)


cookies = {
    "DSID": "AJSUUb3rBcCRX98VstDsnOPX0125Is89qDzje1EoEQjlKDL6BqOqo5EG2qM9b-7ltAkr3CUgU-BVCkOHJMpNmxMVMEeCNiRmR7v9hWWr6OrE3nvJGixoNYH6VlZymeX6-JlDkcH9sa-TTa4LzxluAIH_N2qY4LXpK2BMjgB8Fmcvhl6J3yIVWOWJ2HZ7nIJ_u9zQtV25SZ3e04dsENdacFm0UYAfRLle7C41VOF1yKeK5IbAoYSbxsbUP3DHM8RL_tkJIusVW19bdGrr1Oq3CUq-rjhBsC4l1Q6tL8EsQP1qpzsz9FDhBmY",
    "auth_token": "7640a80203420b97bf769e13b1b1b408378a65cd"
}

for key, value in cookies.items():
    driver.add_cookie({"name": key, "value": value})
    

sleep(2)

driver.get("https://x.com/")

sleep(3)

js_heigh_section = """return document.querySelector("div[aria-label='Home timeline']").scrollHeight;"""

js_get_usernames = """
div_name = document.querySelectorAll("div[data-testid='User-Name']");

let usernames = [];

for (let i = 0; i < div_name.length; i++) {
    usernames.push(div_name[i].querySelector("a").getAttribute("href").replaceAll("/", "@"));
}

return usernames;
"""

js_show_spam = """
function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

getElementByXpath("//span[text()='Show probable spam']").closest("button").click()

"""

js_show_additional = """
function getElementByXpath(path) {
    return document.evaluate(path, document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
}

getElementByXpath("//span[text()='Show']").closest("button").click()

"""

js_check_rt = """

let articles = document.querySelectorAll("article");

let urls = [];

for (let i = 0; i < articles.length; i++) {{
    
    let article = articles[i];
    
    let ref = article.querySelectorAll("a");
    
    for (let j = 0; j < ref.length; j++) {{
        console.log(ref[j].href);
        
        urls.push(ref[j].href);
        
        /*
        if(ref[j].href == "{}"){{
            return true;
        }}*/
        
    }}
}}

return urls;

"""


async def check_comment(username):
    
    print("[+] Checking comment")
    
    usernames = []
    
    previous_height = 0
    height = driver.execute_script(js_heigh_section)
    
    while previous_height != height:
        
        for i in range(previous_height, height, 100):
            driver.execute_script(f"window.scrollTo(0, {i});")
            sleep(0.2)
                        
            usrs = driver.execute_script(js_get_usernames)
            
            usernames.extend(usrs)
            
            print(usernames)
                        
            try:
                driver.execute_script(js_show_spam)
                sleep(1)
            except:
                pass
                
            try:
                driver.execute_script(js_show_additional)
                sleep(1)
            except:
                pass
            
            usernames = list(map(lambda x: x.lower(), usernames))
            
            if username.lower() in usernames:
                return True
        
        previous_height = height
        height = driver.execute_script(js_heigh_section)
        
        usernames = list(set(usernames))
        
    return False
    
async def check_rt(url):
        
        print("[+] Checking RT")
        snippet = js_check_rt.format(url)
        urls = driver.execute_script(snippet)
        
        print(urls)
        
        urls = list(map(lambda x: x.lower(), urls))
        
        if url.lower() in urls:
            print("[+] IN")
            return True
        else:
            print("[+] NOT IN")
            return False
     
class verification_t:
    like = None
    comment = None
    share = None

async def verification(url, username):
    
    verif = verification_t()
    
    print("[+] Verification started {} - {}".format(url, username))
    
    driver.get(url)
    
    sleep(3)
    
    res = await check_comment(username)
    if res == True:
        print("[+] Username found")
        verif.comment = True
    else:
        print("[-] Username not found")
        verif.comment = False


    user_url = "https://x.com/{}".format(username)
    driver.get(user_url)
    sleep(3)
    
    print("URL to check: {}".format(url.split("?")[0]))
    
    res = await check_rt(url.split("?")[0])
    
    if res == True:
        print("[+] RT found")
        verif.share = True
    else:
        print("[-] RT not found")
        verif.share = False
        
    print("[+] Verification done")
    
    return verif
    #await send_verification_back(chat_id, id_influencer, campaign_id, verif)
    
    


async def notify_influencer_finished_campaign_before_validation(id_influencer, id_campaign):
    inf = influencer(*Influencer.get_from_id(id_influencer))
    
    async with Bot(token=token_bot_campaign) as bot:
                                        
        await bot.send_message(inf.tm_id, "The campaign has been finished before checking validation")
 

async def task_waiting_list():
    
    print("[+] Task starting...")
    
    while True: #:)
        
        p_validation = PendingValidation.get()
        
        if p_validation.is_exist():
            print("[+] Start New Verification")
            
            inf = influencer(*Influencer.get_from_id(p_validation.id_influencer))
            camp = campaign(*Campaign.get_from_id(p_validation.id_campaign))

            # Verification
            res = await verification(camp.x_url, inf.x_name )
                
                
            if res.comment and res.share:
                print("[+] Verification Validated")
                
                PendingValidation.validate(p_validation)
                
                Campaign.update_budget(camp.id_campaign, camp.budget_left - inf.price)    
                camp.budget_left = camp.budget_left - inf.price
                
                # Notify the validation to the influencer
                async with Bot(token=token_bot_campaign) as bot:
                        
                    msg = message_validation.format(inf.wallet)
                    await bot.send_message(inf.tm_id, msg)
                
                
                print("[+] Start Checking the Campaign")
                if not Checker.available_influ_not_validate(camp.id_campaign):
                    print("[+] No Enough Budget Left - End of the Campaign")
                    
                    Campaign.update_finished(camp.id_campaign, 1)
                    
                    # Notify all client + deleting the pending validation
                    ids_influencer = PendingValidation.get_all_influ_from_campaign(camp.id_campaign)
                    
                    for _id in ids_influencer:                    
                        print(f"[+] {inf.tm_username} Stop Validation + Notification")
                        
                        await notify_influencer_finished_campaign_before_validation(_id[0], camp.id_campaign)
                        
                        p_val = pending_validation_t(camp.id_campaign, _id[0])
                        PendingValidation.delete(p_val)
                        
                    print("[+] Update the end campaign message")
                    async with Bot(token=token_bot_campaign) as bot:
                        channel_message_upt = channel_msg_complete.format(camp.x_url) 
                    
                        new_photo = FSInputFile(path_img_end_campaign)
                        media = InputMediaPhoto(media=new_photo, caption=channel_message_upt, parse_mode=ParseMode.MARKDOWN)
                    
                        await bot.edit_message_media(chat_id="-1002245377748", message_id=camp.id_message, media=media)
                                        
                else:
                    print("[+] Update the budget campaign message")
                    
                    channel_message_upt = channel_msg.format(camp.x_url, camp.budget_left)
                        
                    async with Bot(token=token_bot_campaign) as bot:
                        
                        mk_b = InlineKeyboardBuilder()
                        mk_b.button(text='➡ CLICK TO START', url="https://t.me/influfun_bot?start={}".format(camp.id_campaign))  
                        
                        new_photo = FSInputFile(path_img_running_campaign)
                        media = InputMediaPhoto(media=new_photo, caption=channel_message_upt, parse_mode=ParseMode.MARKDOWN)
                                        
                        await bot.edit_message_media(chat_id="-1002245377748", message_id=camp.id_message, media=media, reply_markup=mk_b.as_markup())

                                    
            else:
                print("[+] Refuse the validation")
                PendingValidation.refuse(p_validation)
                
                async with Bot(token=token_bot_campaign) as bot:
                    
                    mk_b = InlineKeyboardBuilder()
                    mk_b.button(text='➡ Verification', callback_data=f'verif:{camp.id_campaign}:{inf.tm_username}')
                
                    await bot.send_message(inf.tm_id, f"Not validated !\n\n🔗 [X Link]({camp.x_url})\n\nPlease retry the verification", reply_markup=mk_b.as_markup())
                    
            print("[+] End of the verification")
                    
        await asyncio.sleep(1)
         
        
async def main():

    await task_waiting_list()


if __name__ == "__main__":
    asyncio.run(main())
    
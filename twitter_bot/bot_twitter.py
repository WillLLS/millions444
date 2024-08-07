from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

from time import sleep
import json
import requests

from dataclasses import dataclass

from selenium.webdriver.chrome.options import Options


chrome_options = Options()
#chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-notifications")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

driver = webdriver.Chrome(options=chrome_options)

driver.get("https://x.com/")

cookies = {
    "DSID": "AJSUUb3rBcCRX98VstDsnOPX0125Is89qDzje1EoEQjlKDL6BqOqo5EG2qM9b-7ltAkr3CUgU-BVCkOHJMpNmxMVMEeCNiRmR7v9hWWr6OrE3nvJGixoNYH6VlZymeX6-JlDkcH9sa-TTa4LzxluAIH_N2qY4LXpK2BMjgB8Fmcvhl6J3yIVWOWJ2HZ7nIJ_u9zQtV25SZ3e04dsENdacFm0UYAfRLle7C41VOF1yKeK5IbAoYSbxsbUP3DHM8RL_tkJIusVW19bdGrr1Oq3CUq-rjhBsC4l1Q6tL8EsQP1qpzsz9FDhBmY",
    "auth_token": "7640a80203420b97bf769e13b1b1b408378a65cd"
}

for key, value in cookies.items():
    driver.add_cookie({"name": key, "value": value})
    

sleep(2)

driver.get("https://x.com/")

sleep(3)

async def verification(url, username):
    
    print("Verification started {} - {}".format(url, username))
    
    driver.get(url)
    
    sleep(3)
    


# Websocket server to receive verification command (data: {url; username})
import asyncio
import websockets
import json

async def handle_connection(websocket, path):
    async for message in websocket:
        try:
            # Parse the JSON message
            data = json.loads(message)
            
            # Extract 'url' and 'username'
            url = data.get('url')
            username = data.get('username')
            
            # Check if both 'url' and 'username' are present
            if url and username:
                print(f"Received command: URL = {url}, Username = {username}")
                response = {"status": "success", "message": "Data received successfully"}
                
                await verification(url, username)
                
                
            else:
                response = {"status": "error", "message": "Missing 'url' or 'username'"}
            
        except json.JSONDecodeError:
            response = {"status": "error", "message": "Invalid JSON"}
        
        # Send response back to the client
        await websocket.send(json.dumps(response))

async def main():
    async with websockets.serve(handle_connection, "localhost", 8766):
        print("WebSocket server started on ws://localhost:8765")
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

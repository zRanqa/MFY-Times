import webbrowser
import urllib.request
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from dotenv import load_dotenv
import os

load_dotenv()

import discord
from discord.utils import get
from random import randint
import asyncio
from _thread import *
import threading

TOKEN = os.getenv("TOKEN")

intents = discord.Intents().all()
client = discord.Client(intents=intents)

MFY_WEBSITE = "https://eops.mcdonalds.com.au/Snap"
ROSTER_WEBSITE = "https://myrestaurant.mcdonalds.com.au/Restaurant/1036/Home"

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

ZRANQA_ID = 663195676330557459


mfa_code = None
waiting_for_mfa = False
ask_for_code = False

def downloadMFY():
    # Create a webdriver and open the EOPS website
    driver = webdriver.Chrome()
    driver.get("https://eops.mcdonalds.com.au/Snap")

    # Maximise to stop the items from not being on the screen
    driver.maximize_window()
    
    # Wait before clicking the "continue" button for selecting language
    wait = WebDriverWait(driver, 10)
    button = wait.until(EC.presence_of_element_located((By.ID, "btnSetPopup")))
    button.click()
    
    # Open the manager login dropdown
    time.sleep(5)
    opener = driver.find_element(By.ID, "managersOpener")
    driver.execute_script("arguments[0].click();", opener)
    
    # Input the username and password
    wait = WebDriverWait(driver, 10)
    username = wait.until(EC.element_to_be_clickable((By.ID, "UsernameInputTxtManagers")))
    username.send_keys(USERNAME)
    password = wait.until(EC.element_to_be_clickable((By.ID, "PasswordInputManagers")))
    password.send_keys(PASSWORD)

    # Click the login button.
    wait = WebDriverWait(driver, 5)
    button = wait.until(EC.presence_of_element_located((By.ID, "btnLoginManagers")))
    button.click()
    
    # MFA Page, wait for a code (might move this up so no timeout)
    global mfa_code
    global waiting_for_mfa
    global ask_for_code
    ask_for_code = True
    print("Waiting for code....")
    waiting_for_mfa = True
    while mfa_code == None:
        continue
    print("Code got!")
    # Input the code into the input box.
    pin_input = wait.until(EC.visibility_of_element_located((By.ID, "pin")))
    pin_input.send_keys(mfa_code)
    mfa_code = None

    # Click continue to log in
    button = wait.until(EC.presence_of_element_located((By.ID, "continueButton")))
    button.click()
    
    # Wait for main page to load
    wait = WebDriverWait(driver, 10)
    time.sleep(10)

    # Grab the start date input box
    start_date = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#app > div.noprinting > div > div.hierarchy-searchbar-wrapper > div.date-select-bar > div:nth-child(2) > div:nth-child(1) > div > div > div.dx-texteditor-input-container > input"
    )))

    date = "12/05/2025" # CHANGE SOON


    # Remove any input already in the box
    start_date.click()
    time.sleep(0.05)
    for i in range(12):
        start_date.send_keys(Keys.BACKSPACE) 
        time.sleep(0.05)
    for i in range(12):
        start_date.send_keys(Keys.DELETE)
        time.sleep(0.05)
    # Type in the selected date
    for char in date:
        start_date.send_keys(char)
        time.sleep(0.05)
    wait = WebDriverWait(driver, 2)
    start_date.send_keys(Keys.ENTER)

    
    wait = WebDriverWait(driver, 5)
    # Grab the end date input box
    end_date = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#app > div.noprinting > div > div.hierarchy-searchbar-wrapper > div.date-select-bar > div:nth-child(2) > div:nth-child(2) > div > div > div.dx-texteditor-input-container > input"
    )))
    
    
    # Remove any input already in the box
    end_date.click()
    end_date.send_keys(Keys.ENTER)
    time.sleep(0.05)
    for i in range(12):
        end_date.send_keys(Keys.BACKSPACE)
        time.sleep(0.05)
    for i in range(12):
        end_date.send_keys(Keys.DELETE)
        time.sleep(0.05)
    # Type in the selected date
    for char in date:
        end_date.send_keys(char)
        time.sleep(0.05)
    end_date.send_keys(Keys.ENTER)

    # Find and click the "go" button
    go_button = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "div[role='button'][aria-label='Go'].dx-button"
    )))
    go_button.click()
    
    # Wait for page to load.
    wait = WebDriverWait(driver, 5)
    time.sleep(5)

    # Save the current window, the next input will open another tab.
    original_window = driver.current_window_handle

    # Click the link for the Advance Drill Thru Info
    day_link = driver.find_element(By.XPATH, "//a[text()='Day']")
    driver.execute_script("arguments[0].click();", day_link)

    # Wait for the second tab to load
    wait = WebDriverWait(driver, 10)
    time.sleep(10)
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))

    # Switch to the new tab
    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            break

    # Expand the information on the page (really only needed for thursday/friday but better to be consistent (im lazy))
    all_button = wait.until(EC.element_to_be_clickable((
        By.XPATH, "//div[@role='button' and contains(@aria-label, 'Items per page') and text()='All']"
    )))
    # all_button.click()

    wait = WebDriverWait(driver, 15)
    time.sleep(15)

    # Open the already coded web scraper
    with open("discord_bot/scrape_utils.js", "r") as file:
        scrape_js = file.read()
    driver.execute_script(scrape_js)

    # Run the scraper script
    driver.execute_script("findMFY();")

    result = driver.execute_script("return window.extractedMFY;")
    print(result)

    time.sleep(100)

    driver.close()

def openRosterWebsite():
    # TODO
    pass

def downloadRoster():
    # TODO
    pass

def main():
    #openMFYWebsite()
    downloadMFY()

def save_last_message_location(message):
    with open("discord_bot/last_message_location.json", "w") as f:
        json.dump({"channel_id": message.channel.id}, f)

def load_last_message_location():
    channel_id = None
    with open("discord_bot/last_message_location.json", "r") as f:
        data = json.load(f)
        channel_id = data["channel_id"]
    return channel_id

def valid_code(message):
    return message.content.startswith(("!!code", "!!other_code"))


async def send_messages():
    while True:
        global ask_for_code
        if ask_for_code:
            ask_for_code = False
            channel_id = load_last_message_location()
            if channel_id is not None:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send(f"<@{ZRANQA_ID}> waiting for code!")
        await asyncio.sleep(2)
        


@client.event
async def on_ready():
    print("{0.user} is online!".format(client))
    client.loop.create_task(send_messages())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    elif message.author.id == ZRANQA_ID:
        if message.content.startswith("!!code"):
            await message.channel.send("Code recieved")

            global waiting_for_mfa
            
            if waiting_for_mfa:
                try:
                    code = str(int(message.content.split(" ")[1]))
                    if len(code) == 6:
                        global mfa_code
                        mfa_code = str(code)
                        await message.channel.send(str(code) + " Is a valid Code")

                    else:
                        await message.channel.send("Not a valid Code")
                except:
                    await message.channel.send("Not a valid Code")
                
            else:
                await message.channel.send("Program does not need code yet.")
        
        save_last_message_location(message)
    elif valid_code(message):
        await message.channel.send("Bro is NOT zRanqa, get lost bozo")

thread = threading.Thread(target=main)
thread.start()

client.run(TOKEN)
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
import datetime

import discord
from discord.utils import get
from random import randint
import asyncio
from _thread import *
import threading

intents = discord.Intents().all()
client = discord.Client(intents=intents)

MFY_WEBSITE = "https://eops.mcdonalds.com.au/Snap"
ROSTER_WEBSITE = "https://myrestaurant.mcdonalds.com.au/Restaurant/1036/Home"

load_dotenv()

TOKEN = os.getenv("TOKEN")
USERNAME = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

ZRANQA_ID = 663195676330557459

mfa_code = None
waiting_for_mfa = False
ask_for_code = False


def write_json(filename: str, week: str, data: list):
    file_path = os.path.join(f"data/{week}", filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def downloadMFY(date: str):
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

    # Right before logging in, wait for the MFA code to avoid timeouts
    global mfa_code
    global waiting_for_mfa
    global ask_for_code
    ask_for_code = True
    print("Waiting for code....")
    waiting_for_mfa = True
    while mfa_code == None:
        continue
    print("Code got!")

    # Click the login button.
    wait = WebDriverWait(driver, 5)
    button = wait.until(EC.presence_of_element_located((By.ID, "btnLoginManagers")))
    button.click()
    
    
    # Input the code into the MFA input box.
    pin_input = wait.until(EC.visibility_of_element_located((By.ID, "pin")))
    pin_input.send_keys(mfa_code)
    mfa_code = None

    # Click continue to log in
    button = wait.until(EC.presence_of_element_located((By.ID, "continueButton")))
    button.click()
    
    # Wait for main page to load
    wait = WebDriverWait(driver, 10)
    time.sleep(10)

    for i in range(6, -1, -1):

        # Grab the start date input box
        start_date = wait.until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, "#app > div.noprinting > div > div.hierarchy-searchbar-wrapper > div.date-select-bar > div:nth-child(2) > div:nth-child(1) > div > div > div.dx-texteditor-input-container > input"
        )))

        new_date = date.split("-")
        new_date = f"{int(new_date[2]) - i}/{new_date[1]}/20{new_date[0]}"


        # Remove any input already in the box
        start_date.click()
        time.sleep(0.05)
        for j in range(12):
            start_date.send_keys(Keys.BACKSPACE) 
            time.sleep(0.05)
        for j in range(12):
            start_date.send_keys(Keys.DELETE)
            time.sleep(0.05)
        # Type in the selected date
        for char in new_date:
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
        for j in range(12):
            end_date.send_keys(Keys.BACKSPACE)
            time.sleep(0.05)
        for j in range(12):
            end_date.send_keys(Keys.DELETE)
            time.sleep(0.05)
        # Type in the selected date
        for char in new_date:
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

        # Scroll to the bottom of the page
        wait = WebDriverWait(driver, 15)
        time.sleep(15)
        driver.execute_script("window.scrollBy(0, 500);")
        wait = WebDriverWait(driver, 2)
        time.sleep(2)

        # Expand the information on the page (really only needed for thursday/friday but better to be consistent (im lazy))
        all_button = wait.until(EC.element_to_be_clickable((
            By.XPATH, "//div[@role='button' and contains(@aria-label, 'Items per page') and text()='All']"
        )))
        all_button.click()

        wait = WebDriverWait(driver, 5)
        time.sleep(5)

        # Open the already coded web scraper
        with open("discord_bot/scrape_utils.js", "r") as file:
            scrape_js = file.read()
        driver.execute_script(scrape_js)

        # Run the scraper script
        driver.execute_script("findMFY();")
        result = driver.execute_script("return window.extractedMFY;")
        print(result)
        # write_mfy(result["date"], "test", result["data"])
        file_name = f"{result["date"]}-MFY.json"
        write_json(file_name, date, result["data"])




        driver.close()
        driver.switch_to.window(original_window)

        wait = WebDriverWait(driver, 10)
        time.sleep(10)

        # END FOR

    # Continue in the same window.
    return driver

def downloadRoster(date: str, driver: webdriver.Chrome):
    driver.get("https://myrestaurant.mcdonalds.com.au/Restaurant/1036/Home")

    # Switch to the new tab
    original_window = driver.current_window_handle
    for handle in driver.window_handles:
        if handle != original_window:
            driver.close()
            driver.switch_to.window(original_window)
            break

    wait = WebDriverWait(driver, 5)
    time.sleep(5)

    reports = driver.find_element(By.XPATH, "//*[@id='reports-menu']/a")
    driver.execute_script("arguments[0].click();", reports)

    wait = WebDriverWait(driver, 5)
    time.sleep(5)

    linebar_reports = driver.find_element(By.XPATH, '//*[@id="content"]/div/section[3]/div/div[2]/div[1]/a')
    driver.execute_script("arguments[0].click();", linebar_reports)
    
    wait = WebDriverWait(driver, 5)
    time.sleep(5)

    
    new_date = date.split("-")
    new_date = f"{new_date[2]}/{new_date[1]}/{new_date[0]}"

    # Week ending date
    week_ending_date = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#date"
    )))
    
    week_ending_date.click()
    week_ending_date.send_keys(Keys.ENTER)
    time.sleep(0.05)
    for i in range(12):
        week_ending_date.send_keys(Keys.BACKSPACE)
        time.sleep(0.05)
    for i in range(12):
        week_ending_date.send_keys(Keys.DELETE)
        time.sleep(0.05)
    # Type in the selected date
    for char in new_date:
        week_ending_date.send_keys(char)
        time.sleep(0.05)
        
    header = driver.find_element(By.ID, "main-menu")
    header.click()
    
    week_ending_date.send_keys(Keys.ENTER)
    # week_ending_date.send_keys(Keys.ENTER)

    table = driver.find_element(By.CLASS_NAME, "ui-datepicker-calendar")
    day_to_find = date.split('-')[2]
    clickable_dates = table.find_elements(By.CSS_SELECTOR, 'td a.ui-state-default')

    # Loop through and click the one with the same day
    for day in clickable_dates:
        if day.text.strip() == day_to_find:
            day.click()
            break

    wait = WebDriverWait(driver, 5)
    time.sleep(5)

    show_report = driver.find_element(By.XPATH, '//*[@id="roster-linebars-report-options"]/div[1]/button')
    show_report.click()
    
    wait = WebDriverWait(driver, 10)
    time.sleep(10)

    with open("discord_bot/scrape_utils.js", "r") as file:
        scrape_js = file.read()
    driver.execute_script(scrape_js)

    # Run the scraper script
    driver.execute_script("findRosters();")
    result = driver.execute_script("return window.extractedRoster;")
    print(result)
    
    write_json("roster.json", date, result)

    driver.close()
    

def find_last_folder_date(day: int, month: int, year: int):
    year = int(str(datetime.date.today().year)[-2:])
    day = f"{datetime.date.today().day:02}"
    month = f"{datetime.date.today().month:02}"

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_difference = 0

    last_folder_date = os.listdir('data')[-1]
    current_folder_date = f"{year}-{month}-{day}"

    print(last_folder_date)

    while last_folder_date != current_folder_date and day_difference <= 14:
        date = current_folder_date.split("-")
        day = int(date[2])
        month = int(date[1])
        year = int(date[0])
        day -= 1
        if day <= 0:
            month -= 1
            if month <= 0:
                year -= 1
                month = 12
            day = days_in_month[month-1]

        day = f"{day:02}"
        month = f"{month:02}"

        current_folder_date = f"{year}-{month}-{day}"
        day_difference += 1


    return last_folder_date, day_difference

def get_next_date(last_date: str) -> str:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    [year, month, day] = last_date.split('-')
    year, month, day = int(year), int(month), int(day)
    day += 7
    if day > days_in_month[month-1]:
        day -= days_in_month[month-1]
        month += 1
    if month > 12:
        month = 1
        year += 1
    return f"{year:02}-{month:02}-{day:02}"

def main():

    date, day_difference = find_last_folder_date(datetime.date.today().day, datetime.date.today().month, datetime.date.today().year)

    if day_difference > 7:
        os.makedirs(f"data/{get_next_date(date)}")
        date = os.listdir('data')[-1]
        driver = downloadMFY(date)
        downloadRoster(date, driver)
    else:
        print("not enough days between last day and current day")
        print(day_difference)

    print("CALUCLATE NOW!!")
    print("COMMIT THE DATA TO REPOSITORY")

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
                    await channel.send(f"<@{ZRANQA_ID}> waiting for code! **Please make sure it is a NEW code**")
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
                    int(message.content.split(" ")[1])
                    code = message.content.split(" ")[1]
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
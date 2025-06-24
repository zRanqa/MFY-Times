from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import subprocess
from dotenv import load_dotenv
import os
import datetime

import discord
from discord.utils import get
from random import randint
import asyncio
from _thread import *
import threading

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'manual')))
import make_folders
import manual_calculation



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

total_mfy_data = None
send_last_mfy = False

send_message = []

driver = None


def write_json(filename: str, week: str, data: list):
    file_path = os.path.join(f"data/{week}", filename)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)

def downloadMFYDay(date: str, i: int):
    global driver
    wait = WebDriverWait(driver, 1)

    # Grab the start date input box
    start_date = wait.until(EC.element_to_be_clickable((
        By.CSS_SELECTOR, "#app > div.noprinting > div > div.hierarchy-searchbar-wrapper > div.date-select-bar > div:nth-child(2) > div:nth-child(1) > div > div > div.dx-texteditor-input-container > input"
    )))

    incremented_date = increment_date(date, -i).split("-")
    new_date = f"{incremented_date[2]}/{incremented_date[1]}/20{incremented_date[0]}"

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

    wait = WebDriverWait(driver, 20)
    time.sleep(20)

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
    
    # Download JSON
    file_name = f"{int(result["date"]):02}-MFY.json"
    write_json(file_name, date, result["data"])

    send_message.append(f"Downloaded: {file_name}")

    driver.close()
    driver.switch_to.window(original_window)

    wait = WebDriverWait(driver, 5)
    time.sleep(5)

def downloadMFY(date: str, day_or_week: str):
    global driver
    try:
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

        if day_or_week == "week":
            for i in range(6, -1, -1):
                downloadMFYDay(date, i)
        elif day_or_week == "day":
                print(date)
                downloadMFYDay(date, 0)
                for window in driver.window_handles:
                    driver.switch_to.window(window)
                    driver.close()

                send_message.append(push_data_to_github())
        return True
    except:
        for window in driver.window_handles:
            driver.switch_to.window(window)
            driver.close()
        return False

def downloadRoster(date: str):
    global driver
    try:
        needs_to_log_in = False
        if driver is None:
            driver = webdriver.Chrome()
            needs_to_log_in = True
        driver.get("https://myrestaurant.mcdonalds.com.au/Restaurant/1036/Home")

        if not needs_to_log_in:
            # Switch to the new tab
            original_window = driver.current_window_handle
            for handle in driver.window_handles:
                if handle != original_window:
                    driver.close()
                    driver.switch_to.window(original_window)
                    break

        else:
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
        send_message.append(f"Downloaded: Roster")
        send_message.append(push_data_to_github())
        driver = None
        return True
    except:
        for window in driver.window_handles:
            driver.switch_to.window(window)
            driver.close()
        driver = None
        return False

def find_last_folder_date(day: int, month: int, year: int):
    year = int(str(datetime.date.today().year)[-2:])
    day = f"{datetime.date.today().day:02}"
    month = f"{datetime.date.today().month:02}"

    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day_difference = 0

    last_folder_date = sort_dates(os.listdir('data'))[-1]
    current_folder_date = f"{year}-{month}-{day}"

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

def increment_date(last_date: str, increment_by: int) -> str:
    days_in_month = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    [year, month, day] = last_date.split('-')
    year, month, day = int(year), int(month), int(day)
    day += increment_by
    if day > days_in_month[month-1]:
        day -= days_in_month[month-1]
        month += 1
    if month > 12:
        month = 1
        year += 1
    if day <= 0:
        month -= 1
        day = days_in_month[month-1] + day
    if month <= 0:
        month = 12
        year -= 1
    return f"{year:02}-{month:02}-{day:02}"

def delete_folder(path):
    if path != "data":
        if os.path.exists(path):
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    delete_folder(item_path)
                else:
                    os.remove(item_path)
            os.rmdir(path)
        else:
            print("Path does not exist")
    else:
        print("Cannot delete data folder")

def main():

    while True:
        date, day_difference = find_last_folder_date(datetime.date.today().day, datetime.date.today().month, datetime.date.today().year)
        global total_mfy_data
        # print(f"Testing date difference: {day_difference}")

        if day_difference > 7:

            os.makedirs(f"data/{make_folders.increment_date(date, 7)}")
            date = sort_dates(os.listdir('data'))[-1]
            mfy_worked = downloadMFY(date, "week")
            roster_worked = downloadRoster(date)

            global send_message
            
            if mfy_worked and roster_worked:
                send_message.append(push_data_to_github())
                passed, fail_message, total_mfy_data = manual_calculation.calculate_data(date)
                if passed:
                    manual_calculation.print_data(total_mfy_data)
                else:
                    send_message.append(fail_message)
            else:
                if not mfy_worked:
                    send_message.append("mfy")
                if not roster_worked:
                    send_message.append("roster")
                delete_folder(f"data/{date}")

        time.sleep(5)



def sort_dates(dateList):
    for i in range(len(dateList) - 1):
        smallest = i
        for j in range(i + 1, len(dateList)):
            if dateList[j] < dateList[smallest]:
                smallest = j
        temp = dateList[i]
        dateList[i] = dateList[smallest]
        dateList[smallest] = temp
    return dateList

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

def compare_date_to_data(date):
    data = sort_dates(os.listdir('data'))
    found = False
    for i in data:
        if i == date:
            found = True
            break
    return found

def is_valid_date(date):
    if len(date) != 8:
        return False, "Date is not 8 characters"
    for i in range(len(date)):
        if i == 2 or i == 5:
            if date[i] != "-":
                return False, "Date is not formatted correctly, [YY-MM-DD]"
        else:
            try:
                int(date[i])
            except:
                return False, "Date contains a Non-Number"
    
    return True, ""

def push_data_to_github():
    try:
        subprocess.run(["git", "add", "data/"], check=True)
        commit_msg = f"Bot data update: {datetime.date.today().isoformat()}"
        subprocess.run(["git", "commit", "-m", commit_msg], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        return "Data pushed to GitHub successfully."
    except subprocess.CalledProcessError as e:
        return f"Git error: {e}"



async def send_messages():
    while True:
        channel_id = load_last_message_location()
        global ask_for_code
        if ask_for_code:
            ask_for_code = False
            if channel_id is not None:
                channel = client.get_channel(channel_id)
                if channel:
                    await channel.send(f"<@{ZRANQA_ID}> waiting for code! **Please make sure it is a NEW code**")

        global send_last_mfy
        global total_mfy_data
        if send_last_mfy:
            send_last_mfy = False
            if channel_id is not None:
                channel = client.get_channel(channel_id)
                if channel:
                    mfy_message = "```Rankings:\n\n"
                    for i in range(0, len(total_mfy_data)):
                        mfy_message += f"{i+1}.\t{total_mfy_data[i]["name"]}: {total_mfy_data[i]["mfy_average"]}\n"
                    mfy_message += "```"
                    await channel.send(mfy_message)

        global send_message
        if len(send_message) > 0:
            if channel_id is not None:
                channel = client.get_channel(channel_id)
                if channel:
                    for message in send_message:
                        if message == "mfy":
                            await channel.send("ERROR: MFY function crashed unexpectedly")
                        elif message == "roster":
                            await channel.send("ERROR: Roster function crashed unexpectedly")
                        elif message == "mfy_calc":
                            await channel.send("ERROR: MFY data_grabber function crashed unexpectedly")
                        elif message == "roster_calc":
                            await channel.send("ERROR: Roster Calculation function crashed unexpectedly")
                        elif message == "workersinhour":
                            await channel.send("ERROR: Worker In Hour Calculation function crashed unexpectedly")
                        elif message == "calculation":
                            await channel.send("ERROR: Total MFY Data Calculation function crashed unexpectedly")
                        else:
                            await channel.send(message)

                    send_message = []
            
        await asyncio.sleep(1)


@client.event
async def on_ready():
    print("{0.user} is online!".format(client))
    client.loop.create_task(send_messages())

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    if message.author.id == ZRANQA_ID: # If jonno sent message
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
        
        elif message.content.startswith("!!get"):
            message_input = message.content.split(" ")
            if len(message_input) <= 2:
                await message.channel.send("Incorrect Syntax: !!get [mfy/roster] [date] [y]")
                return
            
            date = message_input[2]
            
            valid_date, valid_message = is_valid_date(date)
            if not valid_date:
                await message.channel.send(f"Error with date: {valid_message}")
                return
            
            if message_input[1] == "mfy":
                count = 1
                week_ending_date = date
                is_date_found = compare_date_to_data(week_ending_date)
                while not is_date_found and count < 7:
                    week_ending_date = increment_date(week_ending_date, 1)
                    is_date_found = compare_date_to_data(week_ending_date)
                    count += 1
                if not is_date_found:
                    await message.channel.send(f"ERROR: Date not found")
                    return
                if is_date_found:
                    folder = os.listdir(f'data/{week_ending_date}')
                    format_mfy_date = f"{message_input[2].split("-")[2]}-MFY.json"
                    copied_mfy_date = format_mfy_date
                    print(format_mfy_date)
                    found = False
                    for i in folder:
                        if copied_mfy_date == i:
                            found = True
                            break
                    if found:
                        if len(message_input) > 3 and (message_input[3] == "yes" or message_input[3] == "y"):
                            await message.channel.send(f"Deleting date in folder and downloading new data")
                            os.remove(f'data/{week_ending_date}/{format_mfy_date}')
                            thread = threading.Thread(target=downloadMFY, args=(message_input[2], "day"))
                            thread.start()
                        else:
                            await message.channel.send(f"ERROR: MFY Date already exists. Type 'y' at the end of the command to force delete the current data")
                    else:
                        await message.channel.send(f"Getting new MFY Data")
                        thread = threading.Thread(target=downloadMFY, args=(message_input[2], "day"))
                        thread.start()
            elif message_input[1] == "roster":
                folder = os.listdir(f'data')
                found_folder = False
                for i in folder:
                    if i == date:
                        found_folder = True
                        found_roster = False
                        for j in os.listdir(f"data/{date}"):
                            if j == "roster.json":
                                found_roster = True
                        if found_roster:
                            if len(message_input) > 3 and (message_input[3] == "yes" or message_input[3] == "y"):
                                await message.channel.send(f"Deleting roster in folder and downloading new data")
                                os.remove(f'data/{date}/roster.json')
                                thread = threading.Thread(target=downloadRoster, args=(message_input[2],))
                                thread.start()
                            else:
                                await message.channel.send(f"ERROR: Roster already exists. Type 'y' at the end of the command to force delete the current data")
                        else:
                            await message.channel.send(f"Getting new Roster Data")
                            thread = threading.Thread(target=downloadRoster, args=(message_input[2],))
                            thread.start()
                        break
                if not found_folder:
                    await message.channel.send(f"ERROR: date not found in data")
            else:
                await message.channel.send(f"ERROR: second parameter should be either 'mfy' or 'roster'")

        elif message.content.startswith("!!push"):
            await message.channel.send(push_data_to_github())


    if message.content.startswith("!!help"):
        message_to_send = f"""```Welcome to MFY Bot! Here are a list of commands:\n
For Jonno Only:
!!code [code] -> Sends the MFA code to the discord bot.
!!get [mfy/roster] [date] [y] -> Downloads a specific MFY Day or roster week, the 'Y' is a force re-download.
!!push -> Pushes the data folder to the main repository.\n
For Everyone:
!!help -> Prints out this lovely message :D
!!calculate OR !!cal [YY-MM-DD] -> Calculates the scores for the given weeks
!!data -> Outputs all of the current weekly data
!!say -> Stupid command jonno 'had' to make.```"""
        await message.channel.send(message_to_send)

    elif message.content.startswith("!!calculate") or message.content.startswith("!!cal") :
        message_input = message.content.split(" ")
        if len(message_input) > 1:
            if len(message_input[1]) == 8:
                try:
                    input_date = message_input[1].replace("/", "-")
                    date_list = sort_dates(os.listdir('data'))
                    found_date = False
                    for i in date_list:
                        if i == input_date:
                            global total_mfy_data
                            global send_last_mfy
                            passed, fail_message, total_mfy_data = manual_calculation.calculate_data(input_date)
                            if passed:
                                send_last_mfy = True
                            else:
                                send_message.append(fail_message)

                            found_date = True
                            break
                    if not found_date:
                        await message.channel.send("Date not found (try !!data).")
                except:
                    pass
            else:
                await message.channel.send("Incorrect input, must be in format (or try !!data): [YY-MM-DD].")
        else:
            await message.channel.send("Incorrect input, a date [YY-MM-DD] is required.")
        
    elif message.content.startswith("!!data"):
        message_input = message.content.split(" ")
        date_list = sort_dates(os.listdir('data'))
        if len(message_input) == 1:
            date_message = "```Weeks:\n\n"
            for i in date_list:
                date_message += f"{i}\n"
            date_message += "```"
            await message.channel.send(date_message)
        else:
            if len(message_input[1]) == 8:
                input_date = message_input[1].replace("/", "-")
                date_message = f"```Files in {input_date}:\n\n"
                for date in date_list:
                    if date == input_date:
                        for file in os.listdir(f'data/{input_date}'):
                            date_message += f"{file}\n"
                date_message += "```"
                await message.channel.send(date_message)


    elif message.content.startswith("!!say"):
        if len(message.content) > len("!!say "):
            await message.channel.send(message.content[len("!!say "):])

    elif not message.author.id == ZRANQA_ID and (message.content.startswith("!!code") or  message.content.startswith("!!get") or message.content.startswith("!!push")):
        await message.channel.send("Sorry broskiwilliams, these commands are for jonno only")


    if message.author.id == ZRANQA_ID:
        save_last_message_location(message)

thread = threading.Thread(target=main)
thread.start()

client.run(TOKEN)
# System libs
import time
import random
import datetime
import json
import os

from helper import jump_url
from helper import get_followers
from helper import get_following

## wait用
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC



def dm_init(driver):
    jump_url(driver, "https://www.instagram.com/direct/inbox/")


    # お知らせ通知等のポップアップに対応する
    for _ in range(5):
        try:    # ログイン情報、お知らせがあればキャンセル
            elem = driver.find_element(By.CSS_SELECTOR, ".aOOlW.HoLwm")
            try:
                driver.execute_script('arguments[0].click();', elem)
            except:
                elem.click()
            time.sleep(random.randint(1,2))
        except Exception:
            break

def save_followers(followers, file_path='followers_list.json'):
    """
    Saves the list of current followers to a JSON file.
    """
    with open(file_path, 'w') as file:
        json.dump(followers, file)
        print("Followers list has been saved.")

def load_previous_followers(file_path='followers_list.json'):
    """
    Loads the list of previous followers from a JSON file.
    If the file doesn't exist, returns an empty list.
    """
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                print("Error decoding JSON. Returning an empty list.")
                return []
    else:
        print("No previous followers file found. Starting fresh.")
        return []

def thank_you_dm(driver=None, max_tnk_dm=20, myname=None , message=None):
    print('---- Sending DMs to both new and mutual followers ----')
    now = datetime.datetime.now()
    print('Start Time: ' + "{}-{}-{} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    profile_url = f"https://www.instagram.com/{myname}/"
    # Get the list of followers and following
    followers = get_followers(driver, profile_url)
    following = get_following(driver, profile_url)
    
    # Identify new followers
    # Assuming you already have a stored list of followers from a previous time
    previous_followers = load_previous_followers()  # Load from a saved file or database
    new_followers = list(set(followers) - set(previous_followers))

    # Identify mutual followers (those who follow you back)
    mutual_followers = list(set(followers) & set(following))

    mutual_new_followers = list(set(new_followers).intersection(mutual_followers))
    # Combine new and mutual followers into one list
    all_followers_to_dm = [follower for follower in mutual_new_followers if follower not in previous_followers]

    # Initialize DM environment
    dm_init(driver)

    dm_count = 0
    for username in all_followers_to_dm:
        try:
        # Open new message interface
            new_message_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "svg[aria-label='新規メッセージ']"))
            )
            new_message_button.click()
            time.sleep(random.randint(1, 2))

            # Search and select the user
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='検索...']"))
            )
            search_box.send_keys(username)
            time.sleep(2)
            first_result = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/div[6]/div[1]/div/div[2]/div/div/div/div/div/div/div[1]/div/div[3]/div/div[1]/div[1]/div/div"))
            )
            first_result.click()
            time.sleep(2)

            # Confirm chat
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'チャット')]"))
            )
            next_button.click()
            time.sleep(2)

            # Send the DM
            message_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//div[@role='textbox']"))
            )
            message_box.send_keys(message)
            time.sleep(1)

            send_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'x1i10hfl') and contains(text(), '送信')]"))
            )
            send_button.click()
            dm_count += 1
            print(f"DM sent to @{username}")

        except Exception as e:
            print(f"Error while sending DM to @{username}")

        # Exit if max DM count is reached
        if dm_count >= max_tnk_dm:
            print(f"Max DM count ({max_tnk_dm}) reached. Stopping.")
            break

        # Wait before sending the next DM
        time.sleep(random.randint(10, 20))
    
    save_followers(followers)
    now = datetime.datetime.now()
    print('End Time: ' + "{}-{}-{} {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- Completed sending DMs ----')
import datetime
import time
import json

## wait用
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Numerical libs

from helper import get_followers

def auto_follow(driver: WebDriver , myname , max_follow_limit, dm_flag):
    print("---- Automatically Following Users ----")
    now = datetime.datetime.now()
    print(f"Start Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")

    # Text constants
    text_follow = "フォローバック"  # "Follow"
    text_following = "フォロー中"  # "Following"
    text_requested = "リクエスト済み"  # "Requested"
    text_private = "このアカウントは非公開です"  # "This account is private" Note do not change any of these ids if you did then code wont target the element it is supposed to target so keep that in mind

    # XPaths
    xpath_post_count = "//ul/li/div/span/span[contains(@class, 'html-span')]"  # Update based on region
    xpath_button_follow = f"//button//*[text()='{text_follow}']"
    xpath_button_followed = f"//button[@type='button']/div/div[text()='{text_following}']"
    xpath_private_text = f"//*[contains(text(), '{text_private}')]"  # Adjust for language/region
    
    wait = WebDriverWait(driver, 60)

    def get_top_users(users, max_follow_limit):
        return sorted(users.keys(), key=lambda x: users[x], reverse=True)[:max_follow_limit]

    if dm_flag == 0:  
        fetched_followers = get_followers(driver, f"https://www.instagram.com/{myname}")
        users = {user: 0 for user in fetched_followers}  # Initialize as a dictionary with weight 0
        top_users = get_top_users(users, max_follow_limit)
    else: 
        with open('followers_list.json', "r") as f:
            # Convert the list of users into a dictionary with weight 0
            fetched_followers = json.load(f)
            users = {user: 0 for user in fetched_followers}  # Initialize as a dictionary with weight 0
        top_users = get_top_users(users, max_follow_limit)

    print(f"Users to be followed: {len(top_users)}")

    for user in top_users:  # Since it has already sent DM, it won't send it again
        try:
            driver.get(f"https://www.instagram.com/{user}")
            wait.until(EC.presence_of_element_located((By.XPATH, f"{xpath_button_follow} | {xpath_button_followed}")))

            # Skip private accounts
            try:
                if driver.find_elements(By.XPATH, xpath_private_text):
                    print(f"Skipping: `@{user}` is a private account.")
                    continue
            except:
                private_account = False
            
            # Check post count
            try:
                post_count_element = driver.find_element(By.XPATH, xpath_post_count)
                post_count = int(post_count_element.text.strip().replace(",", ""))  # Handle comma-separated numbers
            except Exception:
                post_count = 0

            if post_count == 0:
                print(f"Skipping: `@{user}` has no posts.")
                continue
            try:
                if driver.find_element(By.XPATH, xpath_button_followed):
                    print(f"Skipping: `@{user}` has already followed.")
                    continue
            except:
                followed_button = False

            # Follow the user
            driver.find_element(By.XPATH, xpath_button_follow).click()
            time.sleep(5)
            print(f"Followed: `@{user}`")
        except Exception as e:
            print(f"Failed to follow `@{user}`")

    now = datetime.datetime.now()
    print(f"\nEnd Time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("---- Auto-follow process completed ----")

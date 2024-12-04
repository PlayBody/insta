# System libs
import urllib
import time
import sys
import datetime
import json
import codecs


from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# Numerical libs
import numpy as np



def jump_url(driver, url):
    # たまに読み込めないことがあるので10回はトライする
    for _ in range(0,10):
        try:
            driver.get(url)
            # ページ読み込みまで待機
            WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located)
            driver.implicitly_wait(2)
            driver.find_element(By.ID, "main-frame-error")
            driver.implicitly_wait(10)
            print("エラーページが表示されました (An error page was displayed)")
        except:
            break

def get_now_time():
    url = 'https://script.google.com/macros/s/AKfycbyd5AcbAnWi2Yn0xhFRbyzS4qMq1VucMVgVvhul5XqS9HkAyJY/exec?tz=Asia/Tokyo'
    response = urllib.request.urlopen(url=url)
    x = json.loads(response.read().decode('utf8'))
    now = "{YEAR}-{MONTH}-{DAY}T{HOUR}:{MINUTE}:{SECOND}.{MILISEC}000+09:00".format(
        YEAR=x['year'],
        MONTH="{:02}".format(int(x['month'])),
        DAY="{:02}".format(int(x['day'])),
        HOUR="{:02}".format(int(x['hours'])),
        MINUTE="{:02}".format(int(x['minutes'])),
        SECOND="{:02}".format(int(x['seconds'])),
        MILISEC="{:03}".format(int(x['millis']))
    )
    # datetime形式も用意
    now_dt = datetime.datetime.fromisoformat(now)
    return now, now_dt


def time_management(countermax=3, interval=60):
    # 平均1.1, 標準偏差0.05の正規分布を作成
    nrm = np.random.normal(1.1, 0.05, countermax)

    # 1を超えるもののみを使用
    nrm = np.array([x for x in nrm if x >= 1.0])

    # 設定した最低値になるように乗算
    nrm = nrm * interval

    # 設定したサイズになるように調整
    nrm = np.append(nrm,nrm[0:countermax-len(nrm)])
 
    return nrm


def get_followers(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)  # Wait for the page to load

    # Fetch the total number of followers
    try:
        followers_count_element = driver.find_element(By.XPATH, "//a[contains(@href, '/followers/')]/span")
        followers_count = int(followers_count_element.get_attribute("title").replace(",", "").replace(".", ""))
        print(f"Total Followers: {followers_count}")
    except Exception as e:
        print(f"Error: Unable to fetch followers count. {e}")
        return []

    # Open the followers dialog
    followers_link = driver.find_element(By.CSS_SELECTOR, "a[href$='/followers/']")
    followers_link.click()
    time.sleep(5)  # Wait for the followers modal to load

    followers_list = set()  # Use a set to avoid duplicates
    dialog = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[3]")

    # Scroll until all followers are loaded or count matches
    last_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
    while len(followers_list) < followers_count:
        # Fetch the currently visible followers
        followers = driver.find_elements(By.XPATH, "//div[@role='dialog']//a/div/div/span")
        for follower in followers:
            username = follower.text.strip()
            if username and username not in followers_list:
                followers_list.add(username)
                print(f"Fetched follower: {username}")
                if len(followers_list) == followers_count:  # Stop when count matches
                    break

        if len(followers_list) == followers_count:
            print("Fetched all followers.")
            break

        # Scroll down the dialog
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
        time.sleep(2)  # Allow time for Instagram to load more followers

        # Check if we've reached the bottom of the list
        new_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
        if new_height == last_height:
            print("Reached the bottom of the followers list.")
            break
        last_height = new_height

    print(f"Total followers fetched: {len(followers_list)}")
    return list(followers_list)


def get_following(driver, profile_url):
    driver.get(profile_url)
    time.sleep(5)  # Wait for the page to load

    # Fetch the total number of following
    try:
        following_count_element = driver.find_element(By.XPATH, "//a[contains(@href, '/following/')]/span/span")
        following_count = int(following_count_element.text.strip())
        print(f"Total Following: {following_count}")
    except Exception as e:
        print(f"Error: Unable to fetch following count. {e}")
        return []

    # Open the following dialog
    following_link = driver.find_element(By.CSS_SELECTOR, "a[href$='/following/']")
    following_link.click()
    time.sleep(5)  # Wait for the following modal to load

    following_list = set()  # Use a set to avoid duplicates
    dialog = driver.find_element(By.XPATH, "/html/body/div[5]/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div/div[4]")

    # Scroll until all following are loaded or count matches
    last_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
    while len(following_list) < following_count:
        # Fetch the currently visible following
        following = driver.find_elements(By.XPATH, "//div[@role='dialog']//a/div/div/span")
        for follow in following:
            username = follow.text.strip()
            if username and username not in following_list:
                following_list.add(username)
                print(f"Fetched following: {username}")
                if len(following_list) == following_count:  # Stop when count matches
                    break

        if len(following_list) == following_count:
            print("Fetched all following.")
            break

        # Scroll down the dialog
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", dialog)
        time.sleep(2)  # Allow time for Instagram to load more following

        # Check if we've reached the bottom of the list
        new_height = driver.execute_script("return arguments[0].scrollHeight", dialog)
        if new_height == last_height:
            print("Reached the bottom of the following list.")
            break
        last_height = new_height

    print(f"Total following fetched: {len(following_list)}")
    return list(following_list)



def convert_time_to_unit(hour: int):
    try:
        hour = int(hour)
        text = ""
        if hour // 8760 > 0:
            text += f"{hour // 8760}年"
            hour = hour % 8760
        if hour // 720 > 0:
            text += f"{hour // 720}ヶ月"
            hour = hour % 720
        if hour // 168 > 0:
            text += f"{hour // 168}週間"
            hour = hour % 168
        if hour // 24 > 0:
            text += f"{hour // 24}日"
            hour = hour % 24
        if hour > 0:
            text += f"{hour}時間"
        return text
    except:
        return "不明"
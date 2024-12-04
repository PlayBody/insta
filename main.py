import time
import sys
import random
import traceback
import json
import sys
import codecs

# Set the default encoding to UTF-8
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from gui import get_setting
from helper import time_management
from insta_login import insta_login
from send_dm import thank_you_dm
from auto_follow import auto_follow

from selen import get_webdriver
## wait用
from selenium.webdriver.common.by import By


DM_COND_JAPANESE = "japanese"
DM_COND_FOREIGNER = "foreigner"

get_setting()
# Load settings from insta2.json
def load_settings_from_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            settings = json.load(file)
        print(f"Settings successfully loaded from {file_path}")
        return settings
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON from {file_path}.")
        return {}
# File path for the settings file
settings_file_path = "insta2.json"

# Load settings
SETTING = load_settings_from_file(settings_file_path)

if not SETTING:
    print("Failed to load settings. Exiting.")
    exit()

# Assign settings to variables
myname = SETTING.get("myname", "")
password = SETTING.get("password", "")
interval = SETTING.get("interval", 0)
max_like_fol = SETTING.get("max_like_fol", 0)
max_remove = SETTING.get("max_remove", 0)
max_follower = SETTING.get("max_follower", 0)
max_follow_limit = SETTING.get("auto_follow", {}).get("max_follow_limit", 0)
max_tnk_dm = SETTING.get("max_tnk_dm", 0)
message = SETTING.get("message", "")
wait_hour = SETTING.get("wait_hour", 0.0)
dm_interval = SETTING.get("dm_interval", 0)

# Flags
flag = {
    "dm": SETTING.get("DMONOFF", 0),
    "rm": SETTING.get("RMONOFF", 0),
    "lf": SETTING.get("LFONOFF", 0),
    "ml": 0,  # SETTING.get("MLONOFF", 0) # Optional
    "ri": SETTING.get("RIONOFF", 0),
}

dm_condition = SETTING.get("dm_condition", [])
taglist = [
    SETTING.get("tag1", ""),
    SETTING.get("tag2", ""),
    SETTING.get("tag3", "")
]

auto_follow_settings = SETTING.get("auto_follow", {"enabled": False})

print(f"Loaded settings: {SETTING}")



if __name__ == '__main__':
    print("version 1.3")
    # webdriverを取得
    # stealth_mode=1 でステルスモードオン
    # driver = get_webdriver(stealth_mode=1, ostype="mac", use_profile=1)
    driver = get_webdriver(stealth_mode=1, ostype="win", use_profile=1)

    # 指定時間内にCounter_Maxの数だけランダム時間を生成
    wait_time = time_management(max_like_fol+400, interval)    

    # 何回目のログインか This code means that it is already followed since i have already followed all of then due to this code so i am getting this error which means already followed. You can change text if you want.
    global n_login
    n_login = 0

    # instagramへログイン
    insta_login(driver, myname, password, n_login)

    # マウスオーバー用の変数
    global over_count
    over_count = 0

    # action数の初期化
    p_count = 0
    ac_count = 0
    while True: # because it is true meaning it will continue to run till infinity
        if ac_count > max_like_fol:
            ac_count = 0
        try:
            if p_count == 0:
                p_count += 1
                if flag["dm"] == 1:
                    # フォローしてくれた人にDM
                    thank_you_dm(driver=driver, max_tnk_dm=max_tnk_dm, myname=myname , message=message) # called after entering you id

            if p_count == 1:
                p_count +=1
                if SETTING["auto_follow"]["enabled"]:
                    auto_follow(driver=driver, myname=myname, max_follow_limit=max_follow_limit, dm_flag= flag["dm"]) # will run
            
            p_count = 0 #counter resets and restarts the whole process

            # 避難用ブランクダブを開く
            driver.execute_script('window.open()')

            time.sleep(3)
            # インスタの画面を表示させておくとスコアが下がる説
            driver.close()

            # ブランクタブが０になるのでそれに切り替え
            driver.switch_to.window(driver.window_handles[0])

            # n時間待つ
            wait_minute = int(wait_hour * 60)
            for i in range(0,int(wait_minute)):
                if (int(wait_minute)-i) % 60 == 0:
                    print(f"待機時間残り (Standby time remaining) {(int(wait_minute)-i) // 60}時間です。")
                time.sleep(60)
            
            n_login += 1
            
            # instagramへログイン
            insta_login(driver, myname, password, n_login)
        except:
            traceback.print_exc()

            html = driver.page_source
            with open('./error.html', 'w', encoding='utf-8') as f:
                f.write(html)
            driver.save_screenshot('./error.png')

            # ポップアップが出た場合
            try:
                text = driver.find_element(By.CSS_SELECTOR, '.aOOlW.bIiDR').text
                # Report an issue
                if "問題を報告" in text:
                    print("アクティビティが制限されている可能性があります。終了するにはなにかのキーを押してください。 (Your activity may be restricted, press any key to exit.)")
                    print("※制限されている場合、設定を緩める必要があります。 (*If restrictions are in place, you will need to loosen the settings.)")
                    val = input()
                    sys.exit()
                # OKをクリック
                elem = driver.find_element(By.CSS_SELECTOR, '.aOOlW.HoLwm')
                try:
                    driver.execute_script('arguments[0].click();', elem)
                except:
                    elem.click()
                time.sleep(random.randint(1,2))
            except:
                pass

            lgin_flag = 0
            for _ in range(0,3):
                print(f"問題が発生したため再起動します。3分待ちます。 (A problem occurred and we'll restart it for you. Please wait 1 minutes.) (process_id = {p_count})")
                time.sleep(60*1)
                # タブすべてを閉じる
                driver.quit()
                driver = get_webdriver(stealth_mode=1, ostype="mac", use_profile=1)
                try:
                    insta_login(driver, myname, password,n_login)
                    lgin_flag = 1 # ログイン成功
                except: # ログインに失敗した場合
                    with open('./relogin_error.html', 'w', encoding='utf-8') as f:
                        f.write(html)
                    driver.save_screenshot('./relogin_error.png')
                    continue

            # ログイン成功しなかったら
            if not lgin_flag == 1:
                print("ログインに3回失敗したため停止します。終了するにはなにかのキーを押してください。 (Stopping after 3 failed login attempts. Press any key to exit.)")
                val = input()
                sys.exit() # unless any of these conditions are fulfilled which are not in this case.
                # thats all. This is the change that you asked for. You can change it according to your liking just remove or change the condition. I have just completed the code you specified so i didnot removed enything so rest is up to you.
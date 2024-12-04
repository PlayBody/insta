# System libs
import time
import sys
import random

from helper import jump_url

# third party libs
from selenium.webdriver.common.keys import Keys
## wait用
from selenium.webdriver.common.by import By



def insta_login(driver, myname, password,n_login):

    """お知らせオンにするのアラートを閉じる"""
    def close_oshirase():
        for _ in range(5):
            try:    # ログイン情報、お知らせがあればキャンセル。「後で」をクリック
                elem = driver.find_element(By.XPATH, btn_later)
                try:
                    driver.execute_script('arguments[0].click();', elem)
                except:
                    elem.click()
                time.sleep(random.randint(1,2))
            except Exception:
                break

    # ログイン用のxpath
    # input_username = "//input[@aria-label='電話番号、ユーザーネーム、またはメールアドレス']"
    input_username = "username"
    # input_pw = "//input[@aria-label='パスワード']"
    input_pw = "password"
    btn_submit = "//button[@type='submit']"
    login_error = "//p[contains(text(),'入力されたユーザーネームはアカウントと一致しません') or contains(text(),'パスワードが間違っています')]"
 
    btn_later = "//button[text()='後で']"

    setting_icon = "//*[@aria-label='設定']"
    logout_btn = "//*[contains(text(),'ログアウト')]"

    # instagramへログイン
    insta_url = "https://www.instagram.com/"

    jump_url(driver, insta_url)

    # loginしていた場合はログアウトしてから再起動するように促す
    # 該当のアカウントか判別するのは、できなくはないが、仕様変更するたびにコードを書き換えるのは現実的ではない
    driver.implicitly_wait(5)
    logout_flag = False
    if n_login == 0:
        try:
            # 写真のクラス。クラスがあればログアウトを促す
            elm = driver.find_element(By.CLASS_NAME, "_aagw")
            logout_flag = True
        except:
            pass
    driver.implicitly_wait(10)

    if logout_flag:
        try:
            # お知らせ等を閉じる
            close_oshirase()
            # ログアウト
            driver.find_element(By.XPATH, setting_icon).click()
            time.sleep(1)
            driver.find_element(By.XPATH, logout_btn).click()
        except Exception:
            print("ログアウトに失敗しました。プログラムを停止します。")
            sys.exit()
    
    if n_login != 0:
        return
    
    time.sleep(3)
# additional code for input error while reloading
    try:
        # Locate username field
        time.sleep(2)
        user_field = driver.find_element(By.NAME, input_username)
        user_field.click()  # Ensure the field is focused
        user_field.send_keys(Keys.CONTROL + "a")  # Select all text
        user_field.send_keys(Keys.DELETE)  # Clear selected text
        user_field.send_keys(myname)  # Input the username
    except:
        # Fallback to another selector if the first fails
        user_field = driver.find_elements(By.CSS_SELECTOR, "._2hvTZ.pexuQ.zyHYP")[0]
        user_field.click()
        user_field.send_keys(Keys.CONTROL + "a")
        user_field.send_keys(Keys.DELETE)
        user_field.send_keys(myname)
    time.sleep(2)

    try:
        # Locate password field
        pass_field = driver.find_element(By.NAME, input_pw)
        pass_field.click()
        pass_field.send_keys(Keys.CONTROL + "a")
        pass_field.send_keys(Keys.DELETE)
        pass_field.send_keys(password)
    except:
        # Fallback to another selector if the first fails
        pass_field = driver.find_elements(By.CSS_SELECTOR, "._2hvTZ.pexuQ.zyHYP")[1]
        pass_field.click()
        pass_field.send_keys(Keys.CONTROL + "a")
        pass_field.send_keys(Keys.DELETE)
        pass_field.send_keys(password)
    time.sleep(2)

    driver.find_element(By.XPATH, btn_submit).click()  # Submit the form
    time.sleep(random.randint(4, 6))

 
    driver.implicitly_wait(2)
    try:    # ログイン時のエラー確認
        driver.find_element(By.XPATH, login_error)
        print("ユーザー名、パスワード入力時にエラーが発生しました。プログラムを停止します。")
        sys.exit()
    except Exception:
        pass
 
    close_oshirase()
    driver.implicitly_wait(10)
# System libs
import urllib
import time
import sys
import random
import traceback
import datetime
import json

from gui import get_setting

# third party libs
import pandas as pd
from selen import get_webdriver
from selenium.webdriver.common.keys import Keys
## wait用
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException
# Numerical libs
import numpy as np


DM_COND_JAPANESE = "japanese"
DM_COND_FOREIGNER = "foreigner"


SETTING = get_setting()
myname = SETTING["myname"]
password = SETTING["password"]
interval = SETTING["interval"]
max_like_fol = SETTING["max_like_fol"]
max_remove = SETTING["max_remove"]
max_follower = SETTING["max_follower"]
iine_return_ninnzuu = SETTING["iine_return_ninnzuu"]
max_tnk_dm = SETTING["max_tnk_dm"]
message = SETTING["message"]
wait_hour = SETTING["wait_hour"]
dm_interval = SETTING["dm_interval"]
rm_interval = SETTING["rm_interval"]
flag = {}
flag["dm"] = SETTING["DMONOFF"]
flag["rm"] = SETTING["RMONOFF"]
flag["lf"] = SETTING["LFONOFF"]
flag["ml"] = 0# SETTING["MLONOFF"]
flag["ri"] = SETTING["RIONOFF"]
taglist = [SETTING["tag1"], SETTING["tag2"], SETTING["tag3"]]
dm_condition = SETTING["dm_condition"]


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


# いいねしてくれた人に対していいねを返す
def reply_like(driver, iine_return_ninnzuu=100, ac_count=0):
    # 一人当たりのいいねの回数をランダムに設定(左側の数字が最小、右側の数字が最大)
    iine_return_kaisuu = random.randint(1,3)
    # アクティビティフィードを開く
    jump_url(driver, 'https://www.instagram.com/accounts/activity/')
    time.sleep(random.randint(1,3))

    # いいねの人数・回数をリセット
    iine_ninnzuu_num = 0
    iine_kaisuu_num = 0

    print('---- いいね返しをします ----')
    print(f'いいね返しを行う人数（予定） (Number of people who will like back (planned)): {str(iine_return_ninnzuu)}人')
    print(f'1人あたりのいいね数 (Likes per person){str(iine_return_kaisuu)}')
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    # 〇〇がいいねしました＋アイコン＋いいねされた写真の行
    # 〇〇 liked + icon + liked photo row
    table_class = ".x6s0dn4.x1q4h3jn.x78zum5.x1y1aw1k.xxbr6pl.xwib8y2.xbbxn1n.x87ps6o.x1wq6e7o.x1di1pr7.x1h4gsww.xux34ky.x1ypdohk.x1l895ks"

    for i in range(iine_return_ninnzuu):
        print('--- ' + str(i+1) + '人目')

        # usernameを取得
        try:
            table = driver.find_elements(By.CSS_SELECTOR, table_class)
        except:
            print("通知はありませんでした (There was no notification)")
            break

        # 全ての通知を検査したらbreak
        try:
            # 複数のユーザーネームが表示されるようになった。
            # そのうちの一番目の人をとってくる
            user_name = table[i].find_elements(By.XPATH, ".//div/span/a/span")[0]
            # 取れなかったらブレイク
            user_name.text
        except:
            print("全ての通知を検査しました (Checked all notifications)")
            break

        # スクロール処理をさせる
        try:
            driver.execute_script("document.querySelectorAll('.x6s0dn4, .x1q4h3jn, .x78zum5, .x1y1aw1k, .xxbr6pl, .xwib8y2, .xbbxn1n, .x87ps6o, .x1wq6e7o, .x1di1pr7, .x1h4gsww, .xux34ky, .x1ypdohk, .x1l895ks')["+str(i+1)+"].scrollIntoView({behavior:'smooth',block:'end'})")
        except:
            pass

        if i > 0:
            # 1つ上の通知と今回の通知のuser_nameを取得
            
            user_name_zenkai = table[i-1].find_element(By.XPATH, ".//div/span/a/span")

            # 同じ人ならスキップ
            if user_name_zenkai.text == user_name.text:
                print('1つ上の通知と同じ人なのでスキップします。 (This is the same person as in the previous notification, so skip it.)')
                continue

        # 通知内容を取得
        tuuchi_text = table[i].find_elements(By.XPATH, ".//div/span")[-1]

        # 「いいねしました」ではないならスキップ
        if ('いいね！' in tuuchi_text.text and 'しました' in tuuchi_text.text) or ('liked' in tuuchi_text.text and 'your' in tuuchi_text.text)  :
            print(user_name.text + tuuchi_text.text)
            print('いいね返しします。 (I ll like it back.)')
            # 現在開いてるタブの取得
            handle_array = driver.window_handles

            href = f"https://www.instagram.com/{user_name.text}/"
            
            # 新しいブランクタブを開く
            driver.execute_script('window.open()')
            # 結構待たないとかも
            time.sleep(random.randint(2,3))

            # 新しく開いたタブに切り替える
            driver.switch_to.window(driver.window_handles[1])
            # 無題タブができて止まること多い
            jump_url(driver, href)
            
            try:
                # 1つ目の投稿をクリックさせる。写真を投稿していない場合もあるのでtryで。
                elem = driver.find_element(By.CLASS_NAME, '_aagv')
                try:
                    driver.execute_script('arguments[0].click();', elem)
                except:
                    traceback.print_exc()
                    elem.click()
                time.sleep(random.randint(1,2))

                for j in range(iine_return_kaisuu):
                    btn_liked = "//span[@class='_aamw']/button"

                    # いいねずみだとdivは二つない
                    btn_liked_name = "//span[@class='_aamw']/button/div[2]/span/*[name()='svg']"
                    try: # いいねずみだとdivは二つない
                        like = driver.find_element(By.XPATH, btn_liked_name).get_attribute('aria-label')
                        # いいね済か判定
                        if like == 'いいね！':
                            try:
                                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, btn_liked))))
                            except:
                                elem = driver.find_element(By.XPATH, btn_liked)
                                elem.click()
                            print(str(j+1) + 'つ目の投稿のいいね終了')
                            iine_kaisuu_num += 1
                            time.sleep(random.randint(4,8))
                        elif like == '「いいね！」を取り消す':
                            print(str(j+1) + 'つ目の投稿はいいね済みなのでスキップします')
                            time.sleep(random.randint(1,2))
                    except:
                        print(str(j+1) + 'つ目の投稿はいいね済みなのでスキップします')
                        time.sleep(random.randint(1,2))

                    # 次の投稿の「＞」ボタンをクリックさせる。写真を一枚しか投稿していない場合があるのでtryで。
                    xpath = "//button/div/span/*[name()='svg' and starts-with(@aria-label, '次へ')]/../../.."
                    elem = driver.find_element(By.XPATH, xpath)
                    try:
                        try:
                            driver.execute_script('arguments[0].click();', elem)
                        except:
                            #traceback.print_exc()
                            elem.click()
                    except:
                        print("次の投稿がありませんでした。")
                        break
                    wait_time[ac_count]

            except:
                traceback.print_exc()
                print('→アカウントが非公開なのでスキップします')

            driver.close()
            iine_ninnzuu_num += 1
            ac_count += 1
            wait_time[ac_count]

            # 現在開いてるタブの取得
            handle_array = driver.window_handles

            # 今まで開いていたタブに切り替える
            driver.switch_to.window(handle_array[0])

        # 「いいねしました」ではないならスキップ
        else:
            print('→いいねではなかったのでスキップします')


    print('いいねした人数：' + str(iine_ninnzuu_num) + '人')
    print('いいねを押した数：' + str(iine_kaisuu_num) + '回')
    now = datetime.datetime.now()
    print('完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- いいね返しが終了しました ----')

    return ac_count

def check_follower(driver, href, max_follower=5000, base_url=None):

    # 新しいブランクタブを開く
    driver.execute_script('window.open()')

    # 新しいタブへ移動して開く
    driver.switch_to.window(driver.window_handles[1])
    jump_url(driver, href)

    # フォロワー数を取得
    # たまにユーザーページに飛べない場合があるのでそれ用にtry
    try:
        follower_num_check = driver.find_elements(By.CLASS_NAME, "_ac2a")[1]
        # 一部文字を置換する
        follower_num = follower_num_check.text.replace("万","000").replace(".","").replace('NaN',"0").replace(' ', '')
    except:
        follower_num = 0

    #開いたタブを閉じる
    driver.close()

    # ちょっと待つ
    time.sleep(1)

    # 現在開いてるタブの取得
    handle_array = driver.window_handles

    # 今まで開いていたタブに切り替える
    driver.switch_to.window(handle_array[0])
    
    time.sleep(1.5)
            

    if int(follower_num) < max_follower:
        return True

    elif int(follower_num) >= max_follower:
        return False

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

def insta_login(driver, myname, password):

    """お知らせオンにするのアラートを閉じる"""
    def close_oshirase():
        for _ in range(5):
            try:    # ログイン情報、お知らせがあればキャンセル。「後で」をクリック // Close notifications, etc. Login information, cancel any notifications. Click "Later"
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

    try:
        driver.implicitly_wait(2)
        driver.find_element(By.XPATH, setting_icon)
        return
    except TimeoutException:
        pass

    # loginしていた場合はログアウトしてから再起動するように促す
    # 該当のアカウントか判別するのは、できなくはないが、仕様変更するたびにコードを書き換えるのは現実的ではない
    driver.implicitly_wait(2)
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
    
 
    try:
        driver.find_element(By.NAME, input_username).send_keys(myname)
    except:
        driver.find_elements(By.CSS_SELECTOR, "._2hvTZ.pexuQ.zyHYP")[0].send_keys(myname)
    time.sleep(2)
    
    try:
        driver.find_element(By.NAME, input_pw).send_keys(password)
    except:
        driver.find_elements(By.CSS_SELECTOR, "._2hvTZ.pexuQ.zyHYP")[1].send_keys(password)
    time.sleep(2)
 
    driver.find_element(By.XPATH, btn_submit).submit()
    time.sleep(random.randint(4,6))
 
    driver.implicitly_wait(2)
    try:    # ログイン時のエラー確認
        driver.find_element(By.XPATH, login_error)
        print("ユーザー名、パスワード入力時にエラーが発生しました。プログラムを停止します。")
        sys.exit()
    except Exception:
        pass
 
    close_oshirase()
    driver.implicitly_wait(10)


def tagsearch(driver, tag):
    tag_url = "https://www.instagram.com/explore/tags/{}"
    encodedTag = urllib.parse.quote(tag)    # URLエンコード(日本語、スペース等）
    tag_url = tag_url.format(encodedTag)    # {}を.formatを用いてencodeTagへ置換
    
    jump_url(driver, tag_url)    # エンコードしたタグURLを読み込み


def clicknice(counter):
    # いいね！用のxpathを定義
    btn_liked = "//span[@class='_aamw']/button"
    btn_liked_name = "//span[@class='_aamw']/button/div/span/*[name()='svg' and starts-with(@class, 'x1lliihq x1n2onr6')]"
    try:
        like = driver.find_element(By.XPATH, btn_liked_name).get_attribute('aria-label')
        if like == 'いいね！':
            try:
                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, btn_liked))))
            except:
                elem = driver.find_element(By.XPATH, btn_liked)
                elem.click()
            counter += 1
            print("いいね！回数：{}".format(counter))
            time.sleep(random.randint(1,2))
        elif like == '「いいね！」を取り消す':
            print("既にいいねをしています。")
            pass
        else:
            pass
    except Exception:    # 読み込みエラー等でいいね！を押せない場合
        elem = driver.find_element(By.CSS_SELECTOR, "._aahi")
        try:
            driver.execute_script('arguments[0].click();', elem)
        except:
            elem.click()
        time.sleep(random.randint(1,2))
        print("読み込めないのでスキップします。")
        
    time.sleep(random.randint(1,3))
    return counter


def clickforrow(counter):
    # フォローボタンのxpathを定義
    div_forrow = "//button/div/div[@class='_aacl _aaco _aacw _aad6 _aade']"
    btn_forrow = "//button/div/div[@class='_aacl _aaco _aacw _aad6 _aade']/../.."

    # 〇〇と××みたいになってフォローボタンがない場合がある
    try:
        forrow = driver.find_element(By.XPATH, div_forrow).text
    except:
        return counter

    if forrow == 'フォローする':
        elem = driver.find_element(By.XPATH, btn_forrow)
        try:
            driver.execute_script('arguments[0].click();', elem)
        except:
            elem.click()
        time.sleep(random.randint(1,2))
        counter += 1
        print("フォロー回数：{}".format(counter))
    elif forrow == 'フォロー中':
        print("既にフォローしています。")
        pass
    else:
        pass
    time.sleep(random.randint(1,3))
    return counter


def tag_action(driver=None, ac_count=0, max_follower=5000, wait_time=None):

    print('---- tag検索からフォローといいねを行います ----')
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    
    # 各カウンタの初期値
    likedCounter = 0
    forrowCounter = 0
    tagsearch(driver, random.choice(taglist))    # taglistからタグを選定し検索

    # 写真のXPATH
    tag_picture = "//div[@class='_aagu']"
    try:
        driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, tag_picture))))
    except:
        traceback.print_exc()
        # 10番目からが「最新」の写真
        elem = driver.find_elements(By.XPATH, tag_picture)[9]
        elem.click()
    
    time.sleep(random.randint(1,2))

    base_url = driver.current_url

    while likedCounter < max_like_fol:
        # continue用flag
        flag = 0
        
        # 写真ページが開かれたかどうか
        # たまに読み込まれないので最大10回トライする
        for i in range(0,10):
            try:
                # 写真開いたページのユーザーネームのあたりのクラスが_aaqt
                # aはユーザーネームのhrefとかがある要素（位置が変わったので消去）
                xpath = "//div[@class='_aaqt']"
                elem = driver.find_element(By.XPATH, xpath)
                break
            except:
                traceback.print_exc()
                # 写真ページが開いていなかったらもう一度トライ
                tagsearch(driver, random.choice(taglist))    # taglistからタグを選定し検索
                time.sleep(6)
                # 写真のXPATH
                tag_picture = "//div[@class='_aagu']"
                try:
                    driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, tag_picture))))
                except:
                    traceback.print_exc()
                    elem = driver.find_element(By.XPATH, tag_picture)
                    elem.click()
                time.sleep(random.randint(1,2))
                if i == 9:
                    print("プロフィールがクリックできませんでした。アクションを行わず次へ進みます。")
                    #flag = 1
                    break

        # プロフの要素を取得
        prof_class = ".x1i10hfl.xjqpnuy.xa49m3k.xqeqjp1.x2hbi6w.xdl72j9.x2lah0s.xe8uvvx.xdj266r.x11i5rnm.xat24cr.x1mh8g0r.x2lwn1j.xeuugli.x1hl2dhg.xggy1nq.x1ja2u2z.x1t137rt.x1q0g3np.x1lku1pv.x1a2a7pz.x6s0dn4.xjyslct.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x9f619.x1ypdohk.x1i0vuye.xwhw2v2.xl56j7k.x17ydfre.x1f6kntn.x2b8uid.xlyipyv.x87ps6o.x14atkfc.x1d5wrs8.x972fbf.xcfux6l.x1qhh985.xm0m39n.xm3z3ea.x1x8b98j.x131883w.x16mih1h.xt7dq6l.xexx8yu.x4uap5.x18d9i69.xkhd6sd.x1n2onr6.xjbqb8w.x1n5bzlp.xqnirrm.xj34u2y.x568u83.x3nfvp2"
        # フォロワー数を見に行くのに必要
        elem = driver.find_element(By.CSS_SELECTOR, prof_class)
        href = elem.get_attribute("href")

        if check_follower(driver, href, max_follower, base_url):
            likedCounter = clicknice(likedCounter)    # 自動いいね！
            forrowCounter = clickforrow(forrowCounter)    # 自動フォロー
        else:
            likedCounter = clicknice(likedCounter)    # 自動いいね！
            print(f"フォロワー数が{max_follower}以上のためフォローを行いませんでした。")

        print("{}秒待機します。".format(wait_time[ac_count]))
        if not likedCounter == 0:
            time.sleep(wait_time[ac_count]) # ランダム時間待機後いいね！
        else:
            time.sleep(random.randint(2,3)) # 最初は2,3秒待つ

        ac_count += 1
        if ac_count == max_like_fol - 1:    # 指定回数終了でbreak
            break
        try:    # 次のページへ進む
            xpath = "//button/div/span/*[name()='svg' and starts-with(@aria-label, '次へ')]/../../.."
            try:
                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath))))
            except:
                elem = driver.find_element(By.XPATH, xpath)
                elem.click()
            time.sleep(random.randint(1,2))
        except:    # 次のページへ進めなくなったら、ループを抜ける
            print("次に進めなくなりました")
            break

    print(f"{likedCounter}回いいね,{forrowCounter}人フォローをしました。")
    now = datetime.datetime.now()
    print('完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- tag検索からのフォローといいねを終了します ----')

def dm_init(driver):
    jump_url(driver, "https://www.instagram.com/direct/inbox/")


    # お知らせ通知等のポップアップに対応する // Supports pop-up notifications etc.
    for _ in range(5):
        try:    # ログイン情報、お知らせがあればキャンセル // Login information for pop-up notifications, etc., and cancellation if there is a notification
            elem = driver.find_element(By.CSS_SELECTOR, ".aOOlW.HoLwm")
            try:
                driver.execute_script('arguments[0].click();', elem)
            except:
                elem.click()
            time.sleep(random.randint(1,2))
        except Exception:
            break

# 新しくフォローしてくれた人に対してDMする
def thank_you_dm(driver=None, max_tnk_dm=20, myname=None):

    print('---- 新規フォロワーに対してDMします ----')
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    diff_list = get_follower_from_notice(driver)
    dm_init(driver)

    dm_count = 0
    for i in range(0, len(diff_list)):

        xpath = "//div/*[name()='svg' and starts-with(@aria-label, '新規メッセージ')]/../.."
        try:
            driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, xpath))))
        except:
            traceback.print_exc()
            elem = driver.find_element(By.XPATH, xpath)
            elem.click()
        time.sleep(random.randint(1,2))

        # リストからユーザーネームを打ち込む
        driver.find_element(By.XPATH, "//input[contains(@placeholder, '検索')]").send_keys(diff_list[i])
        WebDriverWait(driver, 60).until(EC.presence_of_element_located((By.XPATH, "//span[text()='" + diff_list[i] + "']/ancestor::*[@role='button']")))
        time.sleep(random.randint(1,2))
        try:
            # 指定のユーザーを探す
            elm_tar_user = driver.find_element(By.XPATH, "//span[text()='" + diff_list[i] + "']/ancestor::*[@role='button']")
            # 選択ボタンの◯をクリック
            elm_tar_btn = elm_tar_user.find_element(By.XPATH, ".//input[starts-with(@aria-label, 'オン・オフを切り替え')]")
            try:
                driver.execute_script('arguments[0].click();', WebDriverWait(driver, 5).until(EC.element_to_be_clickable(elm_tar_btn)))
            except:
                traceback.print_exc()
                elm_tar_btn.click()
        except:
            traceback.print_exc()
            try:
                xpath = "//div[contains(text(),'アカウントが見つかりません。')]"
                driver.find_element(By.XPATH, xpath)
                print(f"{diff_list[i]}のアカウントが見つかりません。")
                continue
            except:
                traceback.print_exc()
                dm_init(driver)
                continue

        time.sleep(random.randint(1,2))

        # チャットをクリック
        xpath = "//div[text()='チャット']"
        elem = driver.find_element(By.XPATH, xpath)
        try:
            try:
                driver.execute_script('arguments[0].click();', elem)
            except:
                traceback.print_exc()
                elem.click()
        except:
            traceback.print_exc()
            dm_init(driver)
            continue

        # 送信先のプロフィールを別タブで表示する
        is_open_profile = False
        try:
            main_window_handle = driver.current_window_handle
            driver.execute_script("window.open('https://www.instagram.com/" + diff_list[i] + "');")
            profile_window_handle = [handle for handle in driver.window_handles if handle != main_window_handle][0]
            is_open_profile = True
            driver.switch_to.window(profile_window_handle)
        except:
            if is_open_profile:
                driver.switch_to.window(profile_window_handle)
                driver.close()
            traceback.print_exc()
            dm_init(driver)
            continue

        time.sleep(random.randint(3,4))

        # 別タブのプロフィールを元に国籍を判定する
        def get_nationality(profile_text):
            # 日本語の文字セットの範囲
            ranges = [
                {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},  # ひらがな
                {'from': ord(u'\u30a0'), 'to': ord(u'\u30ff')},  # カタカナ
            ]
            
            for character in profile_text:
                if any([range['from'] <= ord(character) <= range['to'] for range in ranges]):
                    return "japanese"  # 日本語の文字が見つかった場合
            return "foreigner"  # 日本語の文字が見つからない場合
        try:
            profile = ""
            try:
                for t in driver.find_elements(By.TAG_NAME, "h1"):
                    profile += t.text
            except:
                profile = ""
            nationality = get_nationality(profile)
        except:
            if is_open_profile:
                driver.switch_to.window(profile_window_handle)
                driver.close()
            traceback.print_exc()
            dm_init(driver)
            continue
        if is_open_profile:
            driver.switch_to.window(profile_window_handle)
            driver.close()
        driver.switch_to.window(main_window_handle)

        # 次の人読み込むまで待たないと、同じ人に２回DM送ってしまう。
        time.sleep(random.randint(3,5))

        # 相手からのメッセージリクエストが認証待ちの場合は「認証」を押したいが、デバックが面倒なのでスキップする
        # 他にも相手を制限していると"._ac6v"の要素が出てくる
        if len(driver.find_elements(By.CSS_SELECTOR, "._ac6v")) > 1:
            dm_init(driver)
            continue
        time.sleep(random.randint(1,2))

        # すでにメッセージしていたらcontinue
        driver.implicitly_wait(2)
        try:
            xpath = "//*[@aria-label='Double tap to like']"
            driver.find_element(By.XPATH, xpath) # 吹き出しをチェックして自分から1件でもメッセージを送っていたら中断する
            print(f"@{diff_list[i]}へDM送信済みなので中断")
            continue
        except:
            pass
        driver.implicitly_wait(10)

        # ここエラー起きやすいから10回トライしたら諦める
        try:
            for j in range(0,10):
                # DM送信条件を考慮してメッセージを取得する
                cond_message = None
                for cond in dm_condition:
                    cond_nationality = cond.get("nationality")
                    if nationality == cond_nationality:
                        cond_message = cond.get("message")
                        break
                if cond_message is None:
                    # メッセージが取得できなかった場合は送信を中断
                    print(f"@{diff_list[i]}は条件を満たさないのでDM送信しない")
                    raise Exception("DM送信しない")
                # テキストエリアにメッセージを打ち込む
                xpath = "//div/*[starts-with(@aria-label, 'メッセージ')]"
                lines = cond_message.splitlines()
                for index, line in enumerate(lines):
                    driver.find_element(By.XPATH, xpath).send_keys(line)
                    time.sleep(0.2)
                    if index < len(lines) - 1:
                        actions = ActionChains(driver)
                        actions.key_down(Keys.SHIFT).send_keys(Keys.ENTER).key_up(Keys.SHIFT).perform()
                    time.sleep(0.2)
                time.sleep(random.randint(1,2))
                # 送信ボタン押す
                xpath = "//div[contains(text(),'送信')]"
                elem = driver.find_elements(By.XPATH, xpath)[-1]
                try:
                    driver.execute_script('arguments[0].click();', elem)
                except:
                    elem.click()
                break
        except:
            dm_init(driver)
            continue

        dm_count += 1
        if not i == len(diff_list)-1:
            wit = random.randint(dm_interval,int(dm_interval*1.2))
        else:
            wit = 0

        if dm_count == max_tnk_dm:
            print(f"DMを送った人数：{dm_count} | {wit}秒待機します。")
            time.sleep(wit)
            break
        else:
            print(f"DMを送った人数：{dm_count} | {wit}秒待機します。", end="\r")
            time.sleep(wit)

    time.sleep(random.randint(3,5))

    now = datetime.datetime.now()
    print('完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- 新規フォロワーに対してのDMを終了します。 ----')


def get_follower_from_notice(driver):
    """
    お知らせからフォロワーIDのリストを取得する。
    ただし、過去取得済みのフォロワーは除く
    """
    FILE_NAME = "messaged_followers.txt"
    # FOLLOW_TEXT= "があなたをフォローしました。"
    FOLLOW_TEXT = "フォローリクエスト"
    APPROVE_TEXT = "承認する"

    print('---- お知らせからフォロワーのIDを取得します。 ----')
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    wait = WebDriverWait(driver, 60)

    # お知らせボタンをクリックする
    wait.until(EC.presence_of_element_located((By.XPATH, "//*[@aria-label='お知らせ']")))
    elm_notice = driver.find_element(By.XPATH, "//*[@aria-label='お知らせ']")
    try:
        elm_notice.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-pressable-container]")))
    except TimeoutException:
        elm_notice.click()
        wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-pressable-container]")))
    time.sleep(random.randint(3,5))

    try:
        element = wait.until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'フォローリクエスト')]")))
    except TimeoutException:
        return []


    # Traverse up to the parent element with role="button"
    parent = element
    while parent is not None:
        # Check if the parent has the attribute role='button'
        if parent.get_attribute('role') == 'button':
            parent.click()  # Click the button
            break
        # Move to the parent element
        parent = parent.find_element(By.XPATH, '..')  # Go to the parent

    # 過去取得済みのフォロワーのリストを取得
    try:
        with open(FILE_NAME, 'r') as file:
            saved_followers = [line.rstrip() for line in file]
    except:
        saved_followers = []

    # フォローしてくれた人の一覧を取得
    followers = []
    while True:
        try:
            # Find the div element that contains the APPROVE_TEXT and has role='button'
            element = wait.until(EC.presence_of_element_located((By.XPATH, f"//div[contains(text(), '{APPROVE_TEXT}') and @role='button']")))
            pp_element = element.find_element(By.XPATH, '..').find_element(By.XPATH, '..').find_element(By.XPATH, '..')
            temp_element = pp_element.find_element(By.XPATH, "//*[@class='x7a106z x78zum5 xdt5ytf x1iyjqo2']").find_element(By.XPATH, ".//*")
            text_element = temp_element.find_element(By.XPATH, ".//*")
            follower = text_element.text.strip()
            
            if follower not in saved_followers:
                followers.append(follower)
                print("@" + follower)
            
            # Click the found element
            element.click()
            
            # Optionally, wait a moment to allow for any changes on the page
            wait.until(EC.staleness_of(element))  # Wait until the element is no longer attached to the DOM
            time.sleep(random.randint(1,2))

        except Exception as e:
            # Break the loop if no such element is found
            print("No more elements found to click or an error occurred:", e)
            break

    # フォローしてくれた人の一覧を取得
    # followers = []
    # elm_followers = driver.find_elements(By.XPATH, f"//span[contains(text(), '{APPROVE_TEXT}')]")
    # for e in elm_followers:
    #     i = e.text.find(FOLLOW_TEXT)
    #     if i == -1:
    #         continue
    #     follower = e.text[:i].strip()
    #     if follower not in saved_followers:
    #         followers.append(follower)
    #         print("@" + follower)

    # 今回出力されるフォロワーのリストを保存する
    with open(FILE_NAME, 'a') as file:
        for f in followers:
            file.write(f + "\n")

    now = datetime.datetime.now()
    print('完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- フォロワーの取得を終了します。 ----')

    return followers
    

# ポップアップリストを表示する
def dsp_pup_list(driver, myname, moji="フォロー中"):
    jump_url(driver, f"https://www.instagram.com/{myname}")

    # リスト数の取得
    try:
        xpath = f"//div[contains(text(),'{moji}')]/span"
        elem = driver.find_element(By.XPATH, xpath)
    except:
        print("（デバッグ用）'//div[contains(text(),'{moji}')]/span'失敗")
        try:
            xpath = f"//a[contains(text(),'{moji}')]/span"
            elem = driver.find_element(By.XPATH, xpath)
        except:
            print("（デバッグ用）'//a[contains(text(),'{moji}')]/span'失敗")
            xpath = f"//span[contains(text(),'{moji}')]/span"
            elem = driver.find_element(By.XPATH, xpath)
    
    num = elem.text.replace('NaN',"0")

    xpath = "//div[@role='dialog']"


    for i in range(0,10):
        try:
            try:
                driver.execute_script('arguments[0].click();', elem)
                time.sleep(0.5)
                driver.find_element(By.XPATH, xpath)
            except:
                traceback.print_exc()
                print(f"{moji}driver.execute_script('arguments[0].click();', elem)失敗")
                try:
                    elem.click()
                    time.sleep(0.5)
                    driver.find_element(By.XPATH, xpath)
                except:
                    traceback.print_exc()
                    try:
                        print(f"{moji}.click失敗")
                        time.sleep(0.5)
                        elem.send_keys(Keys.ENTER)
                        driver.find_element(By.XPATH, xpath)
                    except:
                        traceback.print_exc()
                        print("enter不可")
                        try:
                            driver.execute_script("document.getElementByClassName('_7UhW9   xLCgt      MMzan    _0PwGv         uL8Hv     l4b0S   T0kll ').click();")
                            time.sleep(0.5)
                            driver.find_element(By.XPATH, xpath)
                        except:
                            print("driver.execute_script('document.getElementByClassName('_7UhW9   xLCgt      MMzan    _0PwGv         uL8Hv     l4b0S   T0kll ').click();')不可")
                            time.sleep(0.5)
                            driver.execute_script("document.getElementByClassName('_7UhW9    vy6Bb     MMzan   KV-D4          uL8Hv        T0kll ').click();")

                        
            time.sleep(0.5)
            driver.find_element(By.XPATH, xpath)
            break
        except:
            print(f"{moji}ポップアップの表示に{i+1}回失敗しました")
            pass
    
    return num

# ポップアップリストのi番目のデータを取ってくる（ポップアップが開いていること前提）
# もしrmnameと同じならリムる
def get_pup_info(driver, i, rm_list=None, prev_list=None, moji=None):
    global iscr
    try:
        iscr
    except:
        iscr = 1
    username_and_name = "._ab8w, ._ab94, ._ab99, ._ab9h, ._ab9m, ._ab9o, ._abcm"
    id_class = ".x1a2a7pz, .notranslate"
    username_class = "._ab8y._ab94._ab97._ab9f._ab9k._ab9p._abcm"
    username_path = '//a[contains(@class,"notranslate")]/span/div'
    try: # フォロー中の場合
        # 続きを読み込むためにちゃんとスクロールする
        # mojiがフォロワーの場合、最初はこのクラスがない。ので、エラーがどうして出てしまう。
        driver.execute_script(f"document.querySelectorAll('.x1a2a7pz, .notranslate')["+str(int(iscr))+"].scrollIntoView({alignToTop:'True'})")
    except:
        # どうしてもエラーが出るのでコメントアウト
        #traceback.print_exc()
        pass
    time.sleep(0.8 * random.randint(1,2))

    driver.implicitly_wait(1)
    for _ in range(0,15):
        try:
            # くるくるの要素
            xpath = "//div/*[name()='svg' and starts-with(@aria-label, '読み込み中')]"
            driver.find_element(By.XPATH, xpath)
        except:
            break
    driver.implicitly_wait(10)

    username = ""
    # mojiがフォロワーの場合、スクロール処理がないとポップアップがアクティブにならない
    for _ in range(100):
        try:
            #username = driver.find_elements(By.XPATH, username_path)[i].text

            """
            # テーブル
            elm = driver.find_elements(By.CSS_SELECTOR, username_and_name)[i]
            # ↓うまくいかない１
            elmm = elm.find_elements(By.XPATH, ".//span/a/span/div")
            """
            # テーブル
            # elm = driver.find_elements(By.CSS_SELECTOR, username_and_name)[i+1]
            elms = driver.find_elements(By.XPATH, ".//a[contains(@class,'notranslate')]/span/div")
            elmm = elms[i]
            #for el in elmm:
            #    print(el.text)
            username = elmm.text
            #username = driver.find_elements(By.XPATH, ".//div[contains(@class,' _ab8y  _ab94 _ab97 _ab9f _ab9k _ab9p _abcm')]")[i].text
            # username = elem.find_element(By.XPATH, ".//span/div").text
            # username = elem.text
        except IndexError:
            # これエラー表示されちゃって見栄え悪い
            #traceback.print_exc()
            # 続きを読み込むためにちゃんとスクロールする
            # 単なるiじゃ制御できない。諦め。原因不明
            try:
                driver.execute_script(f"document.querySelectorAll('.x1a2a7pz, .notranslate')["+str(iscr)+"].scrollIntoView({alignToTop:'True'})")
            except:
                pass
            iscr += 1
            time.sleep(0.1)
            continue
        else:
            # なぜかこれが出力される（１．３）NoneType: None
            # traceback.print_exc()
            break
    
    #if len(username) == 0:
    #    print("0!")
    driver.implicitly_wait(1)
    
    # ユーザーidではない方のユーザーネーム。idの下に表示されているが、表示されていない人もいる。すると、インデックスiがずれてしまうのでかなり難しい。この機能は凍結
    name = ""
    driver.implicitly_wait(10)

    if not prev_list is None:
        if username in list(prev_list):
            return None, None
        
    rmflag = 0
    if not rm_list is None:
        if username in list(rm_list):
            for _ in range(0,5):
                # フォロー中のボタンを押す
                driver.implicitly_wait(1)
                xpath = "//div/button[@class='_acan _acap _acat']/div/.."
                elem = driver.find_elements(By.XPATH, xpath)[i]
                try:
                    driver.execute_script('arguments[0].click();', elem)
                except:
                    elem.click()

                driver.implicitly_wait(10)

                # ポップアップを一瞬待つ
                time.sleep(random.randint(1,2))
                try:
                    elem = driver.find_element(By.CSS_SELECTOR, '._a9--._a9-_')
                    try:
                        driver.execute_script('arguments[0].click();', elem)
                    except:
                        elem.click()
                    time.sleep(random.randint(1,2))
                    break
                except:
                    print(f"「フォロー中」のクリックに{_+1}回失敗しました。")
                    time.sleep(0.5)
                    pass
            wit = random.randint(rm_interval,int(rm_interval*1.2))
            rmflag = 1
            print(f"\n{username}をリムーブしたので{wit}秒待機します。")
            time.sleep(wit)
        return username, rmflag

    # 取得に失敗したら0にしておく
    toko = 0
    foler = 0
    fol = 0

    global over_count

    # list作成の需要がない場合はスキップ
    if flag["ml"] == 1:
        driver.implicitly_wait(1)
        # 10回連続でマウスオーバーに失敗したら二度とマウスオーバーを行わない。
        if not over_count > 10:
            for _ in range(0,3):
                try:
                    elm = driver.find_elements(By.XPATH, username_path)[i]
                    hover = ActionChains(driver).move_to_element(elm)
                    hover.perform()
                    xpath = "//div/div[@class='_aacl _aaco _aacu _aacy _aad6 _aadb _aade']/span[@class='_ac2a _ac2b']"
                    toko = driver.find_elements(By.XPATH, xpath)[0].text.replace("万","000").replace(".","").replace('NaN',"0").replace(' ', '')
                    foler = driver.find_elements(By.XPATH, xpath)[1].text.replace("万","000").replace(".","").replace('NaN',"0").replace(' ', '')
                    fol = driver.find_elements(By.XPATH, xpath)[2].text.replace("万","000").replace(".","").replace('NaN',"0").replace(' ', '')
                    over_count = 0
                    break
                except:
                    if _ == 2:
                        print(f"マウスオーバーに失敗しました。over_count = {over_count}")
                        over_count += 1
                        # traceback.print_exc()
                    time.sleep(0.5)
                    pass
        driver.implicitly_wait(10)

        # 適当なところにマウスを置いて、ポップアップを解除
        elm = driver.find_element(By.CSS_SELECTOR, '._aadp')
        hover = ActionChains(driver).move_to_element(elm)
        hover.perform()

    now = datetime.datetime.now()

    user_info = {
        "ユーザーネーム" : username,
        "フォロワー数" : foler,
        "フォロー数" : fol,
        "投稿数" : toko,
        "名前" : name,
        # "プロフ文" : profile,
        '時刻' : "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    }

    return user_info, rmflag

# フォロー、フォロワーリスト作成。
def make_list(driver=None, myname=None, follow=0, follower=0):

    # prevlistが読めたかどうかのflag
    if follow == 1:
        moji = "フォロー中"
        dir = f"./{myname}_follow_list.csv"
    elif follower == 1:
        moji = "フォロワー"
        dir = f"./{myname}_follower_list.csv"
    else:
        now = datetime.datetime.now()
        print('時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
        print("エラー発生：どちらのリストを作成するか指定してください。プログラムを終了します。")
        sys.exit()
    
    try:
        prev_list = pd.read_csv(dir, encoding="shift jis")
    except:
        prev_list = pd.DataFrame()

    print(f'---- {moji}リストを作成します ----')
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    # ポップアップを表示させ、数を取ってくる
    num = dsp_pup_list(driver, myname, moji)
    df = prev_list
    try: # prev_list = pd.DataFrame() これの場合は[]にする
        prev_list = prev_list["ユーザーネーム"]
    except:
        prev_list = []
    cnt = 0
    for i in range(0,int(num)):
        # 必ずしもフォロワー数の要素があるとは限らない。理由は不明。
        try:
            user_info, _ = get_pup_info(driver, i, rm_list=None, prev_list=prev_list, moji=moji)
        except:
            traceback.print_exc()
            continue
        cnt += 1
        print(f"\r{moji}リスト作成中：{cnt}/{num}", end="")
        # prev_listに名前があった場合
        if user_info is None:
            continue
        df = pd.concat([
            df, 
            pd.DataFrame(user_info.values(), index=user_info.keys()).T],
            ignore_index=True
        )

    # csvに吐き出し
    with open(dir, mode="w", encoding="shift jis", errors="ignore", newline='') as f:
        df.to_csv(f, index=False)
    now = datetime.datetime.now()
    print('\n完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print(f'---- {moji}リスト作成を終了します ----')


# こちらが片思いしているユーザーをリムる
# 一度にリムりすぎると凍結の恐れがある？
def remove_kataomoi(driver, myname, max_remove=30):
    print('---- 片想いの人をリムーブします ----')
    print(f"最大{max_remove}人に対してリムーブを行います。")
    now = datetime.datetime.now()
    print('開始時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    dir = f"./{myname}_follow_list.csv"
    try:
        follow_list = pd.read_csv(dir, encoding="shift jis")
    except:
        print(f"{dir}がありませんでした。リムーブを終了します。")
        return
    dir = f"./{myname}_follower_list.csv"
    try:
        follower_list = pd.read_csv(dir, encoding="shift jis")
    except:
        print(f"{dir}がありませんでした。リムーブを終了します。")
        return
    follow_list = pd.DataFrame(follow_list["ユーザーネーム"], columns=["ユーザーネーム"])
    follower_list = pd.DataFrame(follower_list["ユーザーネーム"], columns=["ユーザーネーム"])

    # orient='list' の場合、 key が列ラベル、 value が値のリストとなる
    # すべての要素がTrueか判定: all() 1はaxis
    kataomoi_list = follow_list[~follow_list.isin(follower_list.to_dict(orient='list')).all(1)]

    num = dsp_pup_list(driver, myname, moji="フォロー中")
    rm_cnt = 0
    # 片思いリスト一人ひとりに対して、ポップアップの全リストを調査
    for i in range(0,int(num)):
        # 必ずしもフォロワー数の要素があるとは限らない。理由は不明。
        try:
            _, rmflag = get_pup_info(driver, i, rm_list=kataomoi_list["ユーザーネーム"], prev_list=None, moji="フォロー中")
        except:
            traceback.print_exc()
            continue
        if rmflag == 1:
            rm_cnt += 1
        print(f"\r片思いリムーブ実行中（{i}/{num} ）| 現在{rm_cnt}人リムーブしました。", end="")
        # 最大値になったら終了
        if rm_cnt == max_remove:
            break

    now = datetime.datetime.now()
    print('\n完了時刻：' + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print('---- 片想いリムーブを終了します ----')


def get_info(driver, href):
    # 新しいブランクタブを開く
    driver.execute_script('window.open()')
    time.sleep(1)

    # 新しいタブへ移動して開く
    driver.switch_to.window(driver.window_handles[1])
    jump_url(driver, href)

    # usernameを取得  
    username = driver.find_element(By.CSS_SELECTOR, '._7UhW9.fKFbl.yUEEX.KV-D4.fDxYl').text

    # フォロワー数を取得
    try:
        elems = driver.find_elements(By.CLASS_NAME, "g47SY")
    except:
        traceback.print_exc()
        pass

    # 一部文字を置換する
    num_follower = elems[1].text.replace("万","000").replace(".","").replace('NaN',"0").replace(' ', '')

    # findElement()もしくはfindElements()を呼んでいるときに限り要素が現れるまで一定の時間まで自動的に待機します
    driver.implicitly_wait(2)

    # 名前を取得
    try:
        name = driver.find_element(By.CLASS_NAME, "Yk1V7").text
    except:
        name = "None"
        pass

    # プロフ文を取得
    xpath = "//div[@class='QGPIr']/span"
    try:
        profile = driver.find_element(By.XPATH, xpath).text
    except:
        profile = "None"
        pass


    # フォロー数を取得
    try:
        num_follow = elems[2].text
    except:
        traceback.print_exc()
        num_follow = "None"
        pass

    # 投稿数を取得
    try:
        num_post = elems[0].text
    except:
        traceback.print_exc()
        num_post = "None"
        pass

    now = datetime.datetime.now()

    user_info = {
        "ユーザーネーム" : username,
        "フォロワー数" : num_follower,
        "フォロー数" : num_follow,
        "投稿数" : num_post,
        "名前" : name,
        "プロフ文" : profile,
        '時刻' : "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second)
    }

    # 元に戻す
    driver.implicitly_wait(10)

    #開いたタブを閉じる
    driver.close()

    # ちょっと待つ
    time.sleep(1)

    # 現在開いてるタブの取得
    handle_array = driver.window_handles

    # 今まで開いていたタブに切り替える
    driver.switch_to.window(handle_array[0])

    return user_info

# 新しいフォロワーを抽出
def get_diff_follower_list(driver=None, myname=None, max_tnk_dm=20):
    # 前のリストからユーザーネームリストを取得
    try:
        prev_list = pd.read_csv( f"./{myname}_follower_list.csv", encoding="shift jis")["ユーザーネーム"]
    except:
        prev_list = []
        pass
    
    num_follower = dsp_pup_list(driver, myname, moji="フォロワー")

    diff_list = []

    max_num = min(int(max_tnk_dm*1.5), int(num_follower))

    for i in range(0,int(num_follower)):
        # 必ずしもフォロワー数の要素があるとは限らない。理由は不明。
        try:
            user_info, _ = get_pup_info(driver, i, rm_list=None, prev_list=prev_list, moji="フォロワー") 
        except:
            continue
        if not user_info is None:
            diff_list.append(user_info["ユーザーネーム"])
        # そんなに多くの人を検出するとスコアが下がる
        # チェックした回数ではなくdiffを検出した回数なことに注意
        if len(diff_list) == max_num:
            print(f"新規フォロワー検出中{len(diff_list)}/{max_num}")
            break
        else:
            print(f"新規フォロワー検出中{len(diff_list)}/{max_num}", end="\r")
            

    return diff_list

def auto_follow(driver: WebDriver):
    print("---- 指定のユーザーへ直近でアクションがあるユーザーを自動でフォローする ----")
    now = datetime.datetime.now()
    print("開始時刻: " + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))

    text_follow = "フォロー"
    text_following = "フォロー中"
    text_requested = "リクエスト済み"

    xpath_link_like = "//a[substring(@href, string-length(@href) - 9) = '/liked_by/' or substring(@href, string-length(@href) - 8) = '/liked_by']"
    xpath_dialog = "//*[@role='dialog']"
    xpath_close_post = "//*[@role='button']//*[@aria-label='閉じる']"
    xpath_button = "//main//button//text()/.."
    xpath_button_follow = f"//button//*[text()='{text_follow}']"
    xpath_button_not_follow = f"//button//*[text()='{text_following}' or text()='{text_requested}']"
    xpath_button_header_follow = f"//header{xpath_button_follow}"
    xpath_button_header_not_follow = f"//header{xpath_button_not_follow}"
    xpath_text_user = "//main//a//span"
    xpath_text_post_time = "//a/span/time"

    wait = WebDriverWait(driver, 60)

    users = {} # ユーザーID: 重み(重複取集件数)

    for user in SETTING["auto_follow"]["users"]:
        try:
            # プロフィールを開く
            driver.get(f"https://www.instagram.com/{user}")

            xpath_posts = "//a[@role='link']"
            # wait.until(EC.presence_of_element_located((By.XPATH, "//a[@href[starts-with(., '/p/')]]")))
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_posts)))

            # 投稿のリンクを取得
            e_posts = driver.find_elements(By.XPATH, xpath_posts)
            for e in e_posts[:6]:
                try:
                    # 投稿ダイアログを開く
                    # ActionChains(driver).move_to_element(e).perform()
                    e.click()
                    wait.until(EC.presence_of_element_located((By.XPATH, xpath_dialog)))
                    time.sleep(5)
                    # 投稿日時を取得
                    post_date_str = driver.find_element(By.XPATH, xpath_dialog).find_element(By.XPATH, "." + xpath_text_post_time).get_attribute('datetime')
                    post_date = datetime.datetime.fromisoformat(post_date_str)
                    hour_diff = (datetime.datetime.now(datetime.timezone.utc) - post_date).total_seconds() / 3600
                    if hour_diff > SETTING["auto_follow"]["active_period"]:
                        print(f"ユーザー`@{user}`の投稿が古いためスキップ: {convert_time_to_unit(hour_diff)}前")
                        # 古い投稿は取得対象外なのでダイアログを閉じる
                        driver.find_element(By.XPATH, xpath_close_post).click()
                        wait.until(EC.invisibility_of_element_located((By.XPATH, xpath_dialog)))
                        continue

                    # いいね一覧を別タブで開く
                    main_window_handle = driver.current_window_handle
                    path_like = driver.find_element(By.XPATH, xpath_link_like).get_attribute('href')
                    driver.execute_script(f"window.open('{path_like}', '_blank');")
                    new_tab_handle = [handle for handle in driver.window_handles if handle != main_window_handle][0]
                    driver.switch_to.window(new_tab_handle)
                    try:
                        wait.until(EC.presence_of_element_located((By.TAG_NAME, "main")))
                        time.sleep(5)
                        # ユーザーのリストを収集
                        e_users = driver.find_elements(By.XPATH, xpath_text_user)
                        e_buttons = driver.find_elements(By.XPATH, xpath_button)
                        if len(e_users) != len(e_buttons):
                            print(f"WARN: ユーザーの数とフォローボタンの数が一致しないため、フォロー済みのユーザーも含めて収集します。")
                            for e_u in e_users:
                                name = e_u.text.strip()
                                if name in users:
                                    users[name] = users[name] + 1
                                else:
                                    users[name] = 1
                        else:
                            for e_u, e_b in zip(e_users, e_buttons):
                                btn_text = e_b.text.strip()
                                if btn_text != text_follow:
                                    # フォロー済みのユーザーは収集しない
                                    continue
                                name = e_u.text.strip()
                                if name in users:
                                    users[name] = users[name] + 1
                                else:
                                    users[name] = 1
                        print(f"ユーザー`@{user}`の投稿から{len(e_users)}件のユーザーを取得しました。")
                    except Exception as e:
                        print(f"ERROR: ユーザー`@{user}`のいいね一覧の表示と取得に失敗しました。", e)
                        traceback.print_exc()
                    finally:
                        # いいね一覧タブを閉じる
                        driver.close()
                        driver.switch_to.window(main_window_handle)
                    
                    # 投稿ダイアログを閉じる
                    driver.find_elements(By.XPATH, xpath_close_post)[0].click()
                    wait.until(EC.invisibility_of_element_located((By.XPATH, xpath_dialog)))
                
                except Exception as e:
                    print(f"ERROR: ユーザー`@{user}`の投稿の表示に失敗しました。", e)
                    traceback.print_exc()
                    # 開いたダイアログを閉じる
                    e_close_posts = driver.find_elements(By.XPATH, xpath_close_post)
                    for e_c in e_close_posts:
                        e_c.click()
                        wait.until(EC.invisibility_of_element_located(e_c))
                    
        except Exception as e:
            print(f"ERROR: ユーザー`@{user}`へいいねしてるユーザーの取得に失敗しました:", e)
            traceback.print_exc()


    # 指定のユーザーをフォローしていく
    top_users = sorted(users.keys(), key=lambda x: users[x], reverse=True)[:SETTING["auto_follow"]["max_follow_limit"]]
    print(f"今から以下のユーザーをフォローします: {len(top_users)}人")
    for user in top_users:
        print(f"  @{user}")
    for user in top_users:
        try:
            driver.get(f"https://www.instagram.com/{user}")
            time.sleep(5)
            wait.until(EC.presence_of_element_located((By.XPATH, f"{xpath_button_header_follow} | {xpath_button_header_not_follow}")))
            driver.find_element(By.XPATH, xpath_button_header_follow).click()
            wait.until(EC.presence_of_element_located((By.XPATH, xpath_button_header_not_follow)))
            print(f"ユーザー`@{user}`をフォローしました。")
            time.sleep(10)
        except Exception as e:
            if any(driver.find_elements(By.XPATH, xpath_button_header_not_follow)):
                print(f"ユーザー`@{user}`はすでにフォローしています。")
            else:
                print(f"ユーザー`@{user}`のフォローに失敗しました:", e)
            traceback.print_exc()
    
    now = datetime.datetime.now()
    print("\n完了時刻: " + "{}年{}月{}日 {}:{}:{}".format(now.year, now.month, now.day, now.hour, now.minute, now.second))
    print("---- 自動でフォローを終了します ----")


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


if __name__ == '__main__':

    print("version 1.3")

    # webdriverを取得
    # stealth_mode=1 でステルスモードオン
    # driver = get_webdriver(stealth_mode=1, ostype="mac", use_profile=1)
    driver = get_webdriver(stealth_mode=1, ostype="win", use_profile=1)

    # 指定時間内にCounter_Maxの数だけランダム時間を生成
    wait_time = time_management(max_like_fol+400, interval)    

    # 何回目のログインか
    global n_login
    n_login = 0

    # instagramへログイン
    insta_login(driver, myname, password)

    # マウスオーバー用の変数
    global over_count
    over_count = 0

    # action数の初期化
    p_count = 0
    ac_count = 0
    while True:
        if ac_count > max_like_fol:
            ac_count = 0
        try:
            if p_count == 0:
                p_count += 1
                if flag["dm"] == 1:
                    # フォローしてくれた人にDM
                    thank_you_dm(driver=driver, max_tnk_dm=max_tnk_dm, myname=myname)

            
            if p_count == 1:
                p_count += 1
                if flag["ri"] == 1:
                    # いいね返し
                    ac_count = reply_like(
                        driver=driver, 
                        ac_count=ac_count, 
                        iine_return_ninnzuu=iine_return_ninnzuu
                        )

            if p_count == 2:
                p_count += 1
                if flag["ml"] == 1 or flag["rm"] == 1:
                    # 現時点のフォロワーリストを作成
                    make_list(driver=driver, myname=myname, follow=0, follower=1)
                    # 現時点のフォロリストを作成
                    make_list(driver=driver, myname=myname, follow=1, follower=0)


            if p_count == 3:
                p_count += 1
                if flag["rm"] == 1:
                    # 片思いの人をリムる
                    remove_kataomoi(driver, myname, max_remove)

            if p_count == 4:
                p_count += 1
                if flag["lf"] == 1:
                    # タグ検索からいいね、フォロー
                    tag_action(
                        driver=driver,
                        ac_count=ac_count,
                        max_follower=max_follower,
                        wait_time=wait_time
                        )
                    
            if p_count == 5:
                p_count +=1
                if SETTING["auto_follow"]["enabled"]:
                    auto_follow(driver=driver)
            
            p_count = 0

            # 避難用ブランクダブを開く
            driver.execute_script('window.open()')

            time.sleep(3)
            # インスタの画面を表示させておくとスコアが下がる説
            driver.close()

            # ブランクタブが０になるのでそれに切り替え
            driver.switch_to.window(driver.window_handles[0])

            # n時間待つ
            wait_minute = 1 #int(wait_hour * 60)
            for i in range(0,int(wait_minute)):
                if (int(wait_minute)-i) % 60 == 0:
                    print(f"待機時間残り (Standby time remaining) {(int(wait_minute)-i) // 60}時間です。")
                time.sleep(60)
            
            n_login += 1
            
            # instagramへログイン
            insta_login(driver, myname, password)
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
                print(f"問題が発生したため再起動します。3分待ちます。 (A problem occurred and we'll restart it for you. Please wait 3 minutes.) (process_id = {p_count})")
                time.sleep(60*3)
                # タブすべてを閉じる
                driver.quit()
                driver = get_webdriver(stealth_mode=1, ostype="mac", use_profile=1)
                try:
                    insta_login(driver, myname, password)
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
                sys.exit()

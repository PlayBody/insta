from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def get_webdriver(stealth_mode=0, ostype=None, use_profile=0):
    options = Options()

    options.add_argument('--disable-extensions')    #拡張機能 、ユーザースクリプト無効
    options.add_argument('log-level=1') # INFOのログを出力しない
    options.add_argument('--lang=ja-JP')
    if stealth_mode == 1:
        options.add_argument('--lang=ja-JP') # ステルスモードだと英語表記になるのを解消
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)

    if use_profile == 1:
        import getpass
        username = getpass.getuser()
        if ostype == "win":
            #work_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
            work_dir = f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data\\insta"
            #work_dir = f"C:\\Users\\{username}\\AppData\\Local\\selenium_insta_makitonf"
        elif ostype == "mac": # mac
            #work_dir = f"/Users/{username}/Library/Application Support/Google/Chrome/"
            work_dir = f"/Users/{username}/Library/Application Support/Google/Chrome/insta/"
            # work_dir = f"/Users/{username}/Library/Application Support/selenium_insta1"
        else:
            # work_dir = f"/home/{username}/.config/google-chrome/default"
            work_dir = f"/home/{username}/.config/selenium"
    options.add_argument('--user-data-dir=' + work_dir)
    options.add_argument('--profile-directory=Default')
    options.add_argument('--disable-gpu')    #ヘッドレスモードで暫定的に必要 
    options.add_argument('--start-maximized')    #全画面で起動 


    # driver = webdriver.Chrome(chrome_options=options)
    s=Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=s, options=options)
    if stealth_mode == 1:
        from selenium_stealth import stealth
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        stealth(driver,
            languages=["ja-JP", "ja"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True
        )

    # findElement()もしくはfindElements()を呼んでいるときに限り要素が現れるまで一定の時間まで自動的に待機
    driver.implicitly_wait(10)
    
    return driver

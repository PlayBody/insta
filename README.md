# insta_tool
セレニウムを使ってインスタの自動フォローなどを行うツールです

# プログラムの実行方法
`python main.py`で実行できます。

# 実行ファイルの使い方
https://note.com/hryu_/n/na79f4546ed26

# click elementの方法
以下3パターンくらいある

1. driver.find_element(By.XXXX, "yyyy").click()
2. driver.find_element_by_xxxx("yyyy").click()
3. elem = driver.find_element(By.XPATH, xpath) ; driver.execute_script('arguments[0].click();', elem)

安定感は`3>=2>>>1`

3や2を積極的に使っていこう

# 実行ファイルの作成方法
pyinstallerを使用して作成します。

.specファイルを作成します。

```
pyinstaller main.py --onefile
```

.specファイルを編集します。
hiddenimportsへ`selenium_stealth`を設定します。
またdatasへjsファイルを紐付けます。

poetryを使用している場合は'./venv/lib/python3.11/site-packages/selenium_stealth/js/'の部分は、`poetry env info --path`コマンドで取得できます。
`コマンドで取得したパス` + `/Lib/site-packages/selenium_stealth/js/`になります。
```
a = Analysis(
    ['main.py'],
    pathex=[],
    # ...
    datas=[('./venv/lib/python3.11/site-packages/selenium_stealth/js/', 'selenium_stealth/js')],
    hiddenimports=['selenium_stealth'],
    # ...
)
```

バイナリを生成
```
pyinstaller main.spec
```

# 設定ファイルの保存方法
`./insta2.json`に保存する原始的なやり方

# elementの指定方法
指定さえできれば何でもいい。

ただし、クラス名はコロコロ変わるのでXPATHで`//div[contains(text(),'アカウントが見つかりません。')]`こんな感じで指定してあげると都度都度変更の回数が減って楽


# （おまけ）DMを送る人の仕様
現在は過去のリスト(`./{myname}_follower_list.csv`)と現在の差分を取って新しくフォローしてもらった人にのみDMを送っているが、以下のアルゴリズムの方が良いかもしれない。

1. 自身のプロフのフォロー欄から適当に何人か読み込む
2. その人らにDMを送る。ただし、すでにDM送ったことある人はスキップ。指定した人数だけトライ
3. `./{myname}_already_mailed_list.csv`なんかのファイルにすでにDMを送った人を保存しておいて再度DMを送ろうとしない


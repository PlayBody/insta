import tkinter as tk
from tkinter import *
import json

def get_setting():
    # 配列はあらかじめ配列として宣言
    flag = {
        "dm" : 1,
        "rm" : 1,
        "ri" : 1,
        "ml" : 1,
        "lf" : 1
    }
    # Mutual Follow
    taglist = ["相互フォロー", "相互フォロー", "相互フォロー"]

    try:
        with open('./insta2.json') as f:
            setting = json.load(f)
    except:
        setting = {
            'myname': "",
            'password': "", 
            # フォローする間隔は60s以上開けないと凍結するらしい
            'interval': 280, #  フォローする間隔の最小値[s]
            'max_like_fol': 20, # いいね、フォロー数の上限
            'max_remove': 20, # 一度にリムーブする最大値
            'max_follower': 5000, # タグアクションする最大フォロワー数
            'iine_return_ninnzuu': 20, # いいね返しする最大人数
            'max_tnk_dm': 20, # 新しくフォローしてくれた人へDMする最大人数
            'message': "フォローありがとうございます!!", # 新しくフォローしてくれた人へDMするメッセ
            'dm_interval': 280,
            'rm_interval': 280,
            'wait_hour': 12, # 待機時間
            "DMONOFF": 1,
            "RMONOFF": 1,
            "LFONOFF": 1,
            "MLONOFF": 1,
            "RIONOFF": 1,
            "tag1": "相互フォロー",
            "tag2": "フォロバ100",
            "tag3": "fff",
            "dm_condition": [
                {
                    "nationality": "foreigner",
                    "message": "Thank you for the follow!"
                }
            ],
            "auto_follow": {
                "enabled": True,
                "active_period": 168,
                "max_follow_limit": 20,
                "users": []
            }
        }

    # ウィンドウを作成
    win = tk.Tk()
    win.title('インスタ自動運用設定画面 (Insta Auto Operation Settings Screen)')
    win.geometry('700x700')

    frame_base_grid = tk.Frame(win)
    frame_base_grid.pack()

    frame_grid_1_1 = tk.Frame(frame_base_grid)
    frame_grid_1_1.grid(row=0, column=0, sticky='n')

    frame_grid_2_1 = tk.Frame(frame_base_grid)
    frame_grid_2_1.grid(row=0, column=1, sticky='n')

    frame1 = tk.LabelFrame(frame_grid_1_1, text='基本設定 (Basic settings)')
    frame1.pack(fill=tk.X, padx=4, pady=4)


    # ラベルを作成
    label = tk.Label(frame1, text="ユーザーネーム (Username)")
    label.pack()

    # テキストボックスを作成
    text1 = tk.Entry(frame1, bg="white")
    text1.pack()
    text1.insert(tk.END, setting["myname"])

    # ラベルを作成
    label = tk.Label(frame1, text="パスワード (password)")
    label.pack()

    # テキストボックスを作成
    text2 = tk.Entry(frame1, bg="white")
    text2.pack()
    text2.insert(tk.END, setting["password"])

    # ラベルを作成
    label = tk.Label(frame1, text="待機時間[時間] (Waiting time [hours])")
    label.pack()

    # テキストボックスを作成
    text10 = tk.Entry(frame1, bg="white")
    text10.pack()
    text10.insert(tk.END, setting["wait_hour"])



    frame2 = tk.LabelFrame(frame_grid_2_1, text='新規フォロワーへのDM (DM to new followers)')
    frame2.pack(fill=tk.X, padx=4, pady=4)

    flag["dm"] = IntVar()
    flag["dm"].set(setting["DMONOFF"])
    radio_0=tk.Radiobutton(frame2,value=1,variable=flag["dm"],text="ON")
    radio_0.grid(row=0, column=0)
    radio_1=tk.Radiobutton(frame2,value=0,variable=flag["dm"],text="OFF")
    radio_1.grid(row=0, column=1)

    # ラベルを作成
    label = tk.Label(frame2, text="DMを送る最小間隔[秒] (Minimum interval for sending DM [sec])")
    label.grid(row=1, column=0, columnspan=2)

    # テキストボックスを作成
    text11 = tk.Entry(frame2, bg="white")
    text11.grid(row=2, column=0, columnspan=2)
    text11.insert(tk.END, setting["dm_interval"])

    # ラベルを作成
    label = tk.Label(frame2, text="一度にDMする最大人数 (Maximum number of people to DM at once)")
    label.grid(row=3, column=0, columnspan=2)

    # テキストボックスを作成
    text8 = tk.Entry(frame2, bg="white")
    text8.grid(row=4, column=0, columnspan=2)
    text8.insert(tk.END, setting["max_tnk_dm"])

    # 送信条件と内容フレームを作成
    frame2_c = tk.LabelFrame(frame2, text="送信条件と内容 (Transmission conditions and contents)")
    frame2_c.grid(row=5, column=0, columnspan=2, padx=8, pady=8)

    # クロージャ用の変数
    condition_flames = []
    dm_condition_input = []
    text9 = None

    def get_dm_condition(dm_condition_input):
        conditions = []
        for input in dm_condition_input:
            conditions.append({
                "nationality": input["nationality"].get(),
                "message": input["message"].get("1.0", "end-1c")
            })
        return conditions

    def del_dm_condition(index):
        """DM送信条件と内容を削除する"""
        nonlocal condition_flames
        nonlocal dm_condition_input

        # フレーム内部を全削除
        for f in condition_flames:
            f.pack_forget()
        condition_flames = []
        frame2_c_add.pack_forget()

        # 現在の入力状況を取得して全削除
        del dm_condition_input[index]
        conditions = get_dm_condition(dm_condition_input)
        dm_condition_input = []

        # フレーム内を再生成
        new_dm_condition(conditions)
        frame2_c_add.pack()

    def add_dm_condition(index, value):
        """DM送信条件と内容を追加する"""
        # フレーム作成
        f = tk.LabelFrame(frame2_c, text=str(index + 1) + "つ目")
        f.pack(padx=8, pady=8)

        # フレームを配列に格納
        condition_flames.append(f)

        # 入力値格納用辞書を生成
        dm_condition_input.append({
            "nationality": tk.StringVar(),
            "message": tk.Text(f, bg="white", height=3, width= 40)
        })

        # ラベルを作成
        label = tk.Label(f, text="国籍 (nationality)")
        label.pack()

        # 国籍入力欄
        dm_condition_input[index]["nationality"].set(value["nationality"])
        radio_frame = tk.Frame(f)
        radio_frame.pack()
        radio_0=tk.Radiobutton(radio_frame, value="japanese", variable=dm_condition_input[index]["nationality"], text="日本人 (JP)")
        radio_0.grid(row=0, column=0)
        radio_1=tk.Radiobutton(radio_frame, value="foreigner", variable=dm_condition_input[index]["nationality"], text="外国人 (Ex)")
        radio_1.grid(row=0, column=1)

        # ラベルを作成
        label = tk.Label(f, text="DM内容 (content)")
        label.pack()

        # テキストボックスを作成
        text = dm_condition_input[index]["message"]
        text.pack()
        text.insert(tk.END, value["message"])

        # 条件削除ボタン
        frame2_c_del = tk.Button(f, text="条件を削除 (Delete a condition)", command=lambda: del_dm_condition(index))
        frame2_c_del.pack()

    def new_dm_condition(conditions):
        """送信条件と内容のサブフレームを作成"""
        for i, s in enumerate(conditions):
            nonlocal text9
            add_dm_condition(i, s)
            # DMメッセージ内容の後方互換性の担保
            if i <= 0:
                text9 = dm_condition_input[i]["message"]

    def frame2_c_add_on_click():
        frame2_c_add.pack_forget()
        add_dm_condition(len(dm_condition_input), {
            "nationality": None,
            "message": ""
        })
        frame2_c_add.pack()

    # 送信内容と条件のフレーム内部を生成
    new_dm_condition(setting["dm_condition"])

    # 条件追加ボタン
    frame2_c_add = tk.Button(frame2_c, text="条件を追加 (Add a condition)", command=frame2_c_add_on_click)
    frame2_c_add.pack()

    # 自動フォロー機能
    var_auto_follow_enabled = BooleanVar(value=setting["auto_follow"]["enabled"])
    var_active_period = IntVar(value=setting["auto_follow"]["active_period"])
    var_max_follow_limit = IntVar(value=setting["auto_follow"]["max_follow_limit"])
    var_auto_follow_users = [StringVar(value=u) for u in setting["auto_follow"]["users"]]
    frame_auto_follow = create_frame_auto_follow(frame_grid_1_1, var_auto_follow_enabled, var_active_period, var_max_follow_limit, var_auto_follow_users)
    frame_auto_follow.pack(fill=tk.X, padx=4, pady=4)

    frame3 = tk.LabelFrame(win, text='片思いリムーブ (Unrequited Love Remove)')
    # TODO: 正常に動作しないためこの機能は一時的に無効化
    # frame3.grid(row=1, column=1, columnspan=1, padx=15, pady=6, sticky='w')

    flag["rm"] = IntVar()
    flag["rm"].set(setting["RMONOFF"])
    radio_0=tk.Radiobutton(frame3,value=1,variable=flag["rm"],text="ON")
    radio_0.grid(row=0, column=0)
    radio_1=tk.Radiobutton(frame3,value=0,variable=flag["rm"],text="OFF")
    radio_1.grid(row=0, column=1)


    # ラベルを作成
    label = tk.Label(frame3, text="リムーブする最小間隔[s] (Minimum interval to remove)")
    label.grid(row=1, column=0, columnspan=2)

    # テキストボックスを作成
    text12 = tk.Entry(frame3, bg="white")
    text12.grid(row=2, column=0, columnspan=2)
    text12.insert(tk.END, setting["rm_interval"])

    # ラベルを作成
    label = tk.Label(frame3, text="一度にリムーブする最大人数 (Maximum number of people to remove at once)")
    label.grid(row=3, column=0, columnspan=2)

    # テキストボックスを作成
    text5 = tk.Entry(frame3, bg="white")
    text5.grid(row=4, column=0, columnspan=2)
    text5.insert(tk.END, setting["max_remove"])


    frame4 = tk.LabelFrame(win, text='いいね・フォロー (Like/Follow)')
    # TODO: 正常に動作しないためこの機能は一時的に無効化
    # frame4.grid(row=1, column=0, columnspan=1, padx=15, pady=6, sticky='w', rowspan=2)


    flag["lf"] = IntVar()
    flag["lf"].set(setting["LFONOFF"])
    radio_0=tk.Radiobutton(frame4,value=1,variable=flag["lf"],text="ON")
    radio_0.grid(row=0, column=0)
    radio_1=tk.Radiobutton(frame4,value=0,variable=flag["lf"],text="OFF")
    radio_1.grid(row=0, column=1)


    # ラベルを作成
    label = tk.Label(frame4, text="フォローする最小間隔[s] (Minimum interval to follow)")
    label.grid(row=1, column=0, columnspan=2)

    # テキストボックスを作成
    text3 = tk.Entry(frame4, bg="white")
    text3.grid(row=2, column=0, columnspan=2)
    text3.insert(tk.END, setting["interval"])

    # ラベルを作成
    label = tk.Label(frame4, text="一度にするいいね、フォロー数の上限 (Limit on number of likes and follows at one time)")
    label.grid(row=3, column=0, columnspan=2)

    # テキストボックスを作成
    text4 = tk.Entry(frame4, bg="white")
    text4.grid(row=4, column=0, columnspan=2)
    text4.insert(tk.END, setting["max_like_fol"])

    # ラベルを作成
    label = tk.Label(frame4, text="タグアクションする最大フォロワー数 (Maximum number of followers to tag)")
    label.grid(row=5, column=0, columnspan=2)

    # テキストボックスを作成
    text6 = tk.Entry(frame4, bg="white")
    text6.grid(row=6, column=0, columnspan=2)
    text6.insert(tk.END, setting["max_follower"])

    # ラベルを作成
    label = tk.Label(frame4, text="タグ検索のワード（重複可能） (Tag search words (multiple words allowed))")
    label.grid(row=8, column=0, columnspan=2)

    # テキストボックスを作成
    text13 = tk.Entry(frame4, bg="white")
    text13.grid(row=9, column=0, columnspan=2)
    text13.insert(tk.END, setting["tag1"])

    # テキストボックスを作成
    text14 = tk.Entry(frame4, bg="white")
    text14.grid(row=10, column=0, columnspan=2)
    text14.insert(tk.END, setting["tag2"])

    # テキストボックスを作成
    text15 = tk.Entry(frame4, bg="white")
    text15.grid(row=11, column=0, columnspan=2)
    text15.insert(tk.END, setting["tag3"])


    frame5 = tk.LabelFrame(win, text='その他機能 (Other features)')
    # TODO: 正常に動作しないためこの機能は一時的に無効化
    # frame5.grid(row=2, column=1, columnspan=1, padx=15, pady=6, sticky='w')


    # ラベルを作成
    label = tk.Label(frame5, text="いいね返し (Like back)")
    label.grid(row=0, column=0, columnspan=2)

    flag["ri"] = IntVar()
    flag["ri"].set(setting["RIONOFF"])
    radio_0=tk.Radiobutton(frame5,value=1,variable=flag["ri"],text="ON")
    radio_0.grid(row=1, column=0)
    radio_1=tk.Radiobutton(frame5,value=0,variable=flag["ri"],text="OFF")
    radio_1.grid(row=1, column=1)

    # ラベルを作成
    label = tk.Label(frame5, text="一度にいいね返しする最大人数 (Maximum number of people who can like at once)")
    label.grid(row=2, column=0, columnspan=2)

    # テキストボックスを作成
    text7 = tk.Entry(frame5, bg="white")
    text7.grid(row=3, column=0, columnspan=2)
    text7.insert(tk.END, setting["iine_return_ninnzuu"])


    # 決定ボタンを押したとき
    def ok_click():
        nonlocal d
        # テキストボックスの内容を得る
        myname = text1.get()
        password = text2.get()
        interval = int(text3.get())
        max_like_fol = int(text4.get())
        max_remove = int(text5.get())
        max_follower = int(text6.get())
        iine_return_ninnzuu = int(text7.get())
        max_tnk_dm = int(text8.get())
        message = text9.get("1.0", "end-1c") if text9 is not None else ""
        wait_hour = float(text10.get())
        dm_interval = int(text11.get())
        rm_interval = int(text12.get())
        flag["dm"] = int(flag["dm"].get())
        # TODO: 機能を一時的に無効化しているためOFFを設定
        flag["rm"] = 0 #int(flag["rm"].get())
        flag["lf"] = 0 #int(flag["lf"].get())
        flag["ml"] = 0 #int(flag["ml"].get())
        flag["ri"] = 0 #int(flag["ri"].get())
        taglist[0] = text13.get()
        taglist[1] = text14.get()
        taglist[2] = text15.get()
        dm_condition = get_dm_condition(dm_condition_input)
        
        win.destroy()

        d = {
            'myname': myname,
            'password': password,
            'interval': interval,
            'max_like_fol': max_like_fol,
            'max_remove': max_remove,
            'max_follower': max_follower,
            'iine_return_ninnzuu': iine_return_ninnzuu,
            'max_tnk_dm': max_tnk_dm,
            'message': message,
            'dm_interval': dm_interval,
            'rm_interval': rm_interval,
            'wait_hour': wait_hour,
            "DMONOFF": flag["dm"],
            "RMONOFF": flag["rm"],
            "LFONOFF": flag["lf"],
            "RIONOFF": flag["ri"],
            "MLONOFF": flag["ml"],
            "tag1": taglist[0],
            "tag2": taglist[1],
            "tag3": taglist[2],
            "dm_condition": dm_condition,
            "auto_follow": {
                "enabled": var_auto_follow_enabled.get(),
                "active_period": var_active_period.get(),
                "max_follow_limit": var_max_follow_limit.get(),
                "users": [u.get() for u in var_auto_follow_users]
            }
            }

        with open('./insta2.json', 'w') as f:
            json.dump(d, f, indent=4, ensure_ascii=False)
        
    # ボタンを作成
    d = {}
    okButton = tk.Button(win, text='決定 (OK)', command=ok_click)
    okButton.pack()

    # ウィンドウを動かす
    win.mainloop()

    return d

def create_frame_auto_follow(win : Tk, flag: BooleanVar, active_period: IntVar, max_follow_limit: IntVar, users: list[StringVar]) -> tk.LabelFrame:

    def add_user():
        nonlocal followers
        u = StringVar()
        users.append(u)
        f = create_user(len(followers), u)
        f.pack()
        followers.append(f)
        pass

    def del_user(index: int):
        nonlocal followers
        users.pop(index)
        for f in followers[index:]:
            f.pack_forget()
        followers = followers[:index]
        for u in users[index:]:
            i = 0
            f = create_user(index + i, u)
            f.pack()
            followers.append(f)
            i += 1

    def create_user(index: int, val: StringVar) -> tk.Frame:
        nonlocal frame_followers
        frame_follower = tk.Frame(frame_followers)
        tk.Entry(frame_follower, width= 17, textvariable=val).grid(row=0, column=0)
        tk.Button(frame_follower, text="削除 (Delete)", command=lambda: del_user(index)).grid(row=0, column=1)
        return frame_follower
    
    def convert_time_to_unit(hour: int):
        try:
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
    
    def change_label_active_datetime(event):
        nonlocal label_active_datetime
        nonlocal active_period
        try:
            label_active_datetime.config(text=f"計算値：{convert_time_to_unit(active_period.get())}")
        except:
            label_active_datetime.config(text="計算値：不明")

    frame = tk.LabelFrame(win, text='フォローの自動化 (Automated following)')

    # 有効・無効のラジオボタン
    frame_radios = tk.Frame(frame)
    radio_0=tk.Radiobutton(frame_radios,value=True,variable=flag,text="ON")
    radio_0.grid(row=0, column=0)
    radio_1=tk.Radiobutton(frame_radios,value=False,variable=flag,text="OFF")
    radio_1.grid(row=0, column=1)
    frame_radios.pack()

    # アクティブユーザーと認識する期間
    frame_active = tk.Frame(frame)
    tk.Label(frame_active, text="アクティブユーザーと認識する期間 (Period to recognize as an active user)").pack()
    frame_active_text = tk.Frame(frame_active)
    entry_active = tk.Entry(frame_active_text, width= 17, textvariable=active_period)
    entry_active.grid(row=0, column=0)
    entry_active.bind("<KeyRelease>", change_label_active_datetime)
    tk.Label(frame_active_text, text="時間前 (Hours ago)").grid(row=0, column=1)
    frame_active_text.pack(anchor="w")
    label_active_datetime = tk.Label(frame_active, text=f"計算値 (Calculated value:): {convert_time_to_unit(active_period.get())}", anchor="w")
    label_active_datetime.pack(fill=tk.X)
    frame_active.pack(fill=tk.X)

    # フォロー上限人数
    frame_follow_num = tk.Frame(frame)
    tk.Label(frame_follow_num, text="フォロー上限人数 (Maximum number of followers)").pack()
    frame_follow_num_text = tk.Frame(frame_follow_num)
    tk.Entry(frame_follow_num_text, width= 17, textvariable=max_follow_limit).grid(row=0, column=0)
    tk.Label(frame_follow_num_text, text="件").grid(row=0, column=1)
    frame_follow_num_text.pack(anchor="w")
    frame_follow_num.pack(fill=tk.X)

    # フォロワー検索対象のアカウント一覧
    followers = []
    frame_followers = tk.Frame(frame)
    tk.Label(frame_followers, text="検索対象のユーザー (Search for users)").pack()
    for index, user in enumerate(users):
        frame_follower = create_user(index, user)
        frame_follower.pack()
        followers.append(frame_follower)
    frame_followers.pack()

    # 追加ボタン
    tk.Button(frame, text="ユーザー追加 (Add User)", command=add_user).pack()

    return frame
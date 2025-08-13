# -*- coding: utf-8 -*-
# Copyright (c) 2021 Tachibana Securities Co., Ltd. All rights reserved.

# 2021.07.09,   yo.
# 2023.08.30 reviced,   yo.
# 2025.07.27 reviced,   yo.
#
# 立花証券ｅ支店ＡＰＩ利用のサンプルコード
#
# 動作確認
# Python 3.11.2 / debian12
# API v4r7
#
# 機能: ニュースヘッダー取得
#
# 必要な設定項目
# 取得したいカテゴリコード: my_p_CG     未指定時は全て対象。100:QUICKニュース、110:ＡＩ市況状況速報、120:AI開示速報（決算関連）、129:ＡＩ開示速報（その他）
# 取得したい銘柄コード: my_p_IS       未指定時は全て対象。
# ニュース日付（YYYYMMDD）範囲指定（from）: my_p_DT_FROM
# ニュース日付（YYYYMMDD）範囲指定（to）: my_p_DT_TO      p_DT_FROM <= p_DT_TOで設定する。
# レコード取得位置: my_p_REC_OFST   デフォルト＝０、直近先頭の意味。
# レコード取得件数最大: my_p_REC_LIMT     デフォルト＝100。1回に取得できる最大件数は100。
# 出力ファイル名: my_fname_output  （デフォルトは、'news_header_[銘柄コード].csv'）
#
# 利用方法: 
# 事前に「e_api_login_tel.py」を実行して、
# 仮想URL（1日券）等を取得しておいてください。
# 「e_api_login_tel.py」と同じディレクトリで実行してください。
#
#
# == ご注意: ========================================
#   本番環境にに接続した場合、実際に市場に注文が出ます。
#   市場で約定した場合取り消せません。
# ==================================================
#
#

import urllib3
import datetime
import json
import time
import base64
import urllib.parse


#--- 共通コード ------------------------------------------------------

# request項目を保存するクラス。配列として使う。
class class_req :
    def __init__(self) :
        self.str_key = ''
        self.str_value = ''
        
    def add_data(self, work_key, work_value) :
        self.str_key = func_check_json_dquat(work_key)
        self.str_value = func_check_json_dquat(work_value)


# 口座属性クラス
class class_def_account_property:
    def __init__(self):
        self.sUserId = ''           # userid
        self.sPassword = ''         # password
        self.sSecondPassword = ''   # 第2パスワード
        self.sUrl = ''              # 接続先URL
        self.sJsonOfmt = 5          # 返り値の表示形式指定
        
# ログイン属性クラス
class class_def_login_property:
    def __init__(self):
        self.p_no = 0                       # 累積p_no
        self.sJsonOfmt = ''                 # 返り値の表示形式指定
        self.sResultCode = ''               # 結果コード
        self.sResultText = ''               # 結果テキスト
        self.sZyoutoekiKazeiC = ''          # 譲渡益課税区分  1：特定  3：一般  5：NISA
        self.sSecondPasswordOmit = ''       # 暗証番号省略有無Ｃ  22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
        self.sLastLoginDate = ''            # 最終ログイン日時
        self.sSogoKouzaKubun = ''           # 総合口座開設区分  0：未開設  1：開設
        self.sHogoAdukariKouzaKubun = ''    # 保護預り口座開設区分  0：未開設  1：開設
        self.sFurikaeKouzaKubun = ''        # 振替決済口座開設区分  0：未開設  1：開設
        self.sGaikokuKouzaKubun = ''        # 外国口座開設区分  0：未開設  1：開設
        self.sMRFKouzaKubun = ''            # ＭＲＦ口座開設区分  0：未開設  1：開設
        self.sTokuteiKouzaKubunGenbutu = '' # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunSinyou = ''  # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiKouzaKubunTousin = ''  # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
        self.sTokuteiHaitouKouzaKubun = ''  # 配当特定口座区分  0：未開設  1：開設
        self.sTokuteiKanriKouzaKubun = ''   # 特定管理口座開設区分  0：未開設  1：開設
        self.sSinyouKouzaKubun = ''         # 信用取引口座開設区分  0：未開設  1：開設
        self.sSakopKouzaKubun = ''          # 先物ＯＰ口座開設区分  0：未開設  1：開設
        self.sMMFKouzaKubun = ''            # ＭＭＦ口座開設区分  0：未開設  1：開設
        self.sTyukokufKouzaKubun = ''       # 中国Ｆ口座開設区分  0：未開設  1：開設
        self.sKawaseKouzaKubun = ''         # 為替保証金口座開設区分  0：未開設  1：開設
        self.sHikazeiKouzaKubun = ''        # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
        self.sKinsyouhouMidokuFlg = ''      # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
        self.sUrlRequest = ''               # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
        self.sUrlMaster = ''                # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
        self.sUrlPrice = ''                 # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
        self.sUrlEvent = ''                 # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
        self.sUrlEventWebSocket = ''        # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
        self.sUpdateInformWebDocument = ''  # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
        self.sUpdateInformAPISpecFunction = ''  # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照

        

# 機能: システム時刻を"p_sd_date"の書式の文字列で返す。
# 返値: "p_sd_date"の書式の文字列
# 引数1: システム時刻
# 備考:  "p_sd_date"の書式：YYYY.MM.DD-hh:mm:ss.sss
def func_p_sd_date(int_systime):
    str_psddate = ''
    str_psddate = str_psddate + str(int_systime.year) 
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.month))[-2:]
    str_psddate = str_psddate + '.' + ('00' + str(int_systime.day))[-2:]
    str_psddate = str_psddate + '-' + ('00' + str(int_systime.hour))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.minute))[-2:]
    str_psddate = str_psddate + ':' + ('00' + str(int_systime.second))[-2:]
    str_psddate = str_psddate + '.' + (('000000' + str(int_systime.microsecond))[-6:])[:3]
    return str_psddate


# JSONの値の前後にダブルクオーテーションが無い場合付ける。
def func_check_json_dquat(str_value) :
    if len(str_value) == 0 :
        str_value = '""'
        
    if not str_value[:1] == '"' :
        str_value = '"' + str_value
        
    if not str_value[-1:] == '"' :
        str_value = str_value + '"'
        
    return str_value
    
    
# 受けたテキストの１文字目と最終文字の「"」を削除
# 引数：string
# 返り値：string
def func_strip_dquot(text):
    if len(text) > 0:
        if text[0:1] == '"' :
            text = text[1:]
            
    if len(text) > 0:
        if text[-1] == '\n':
            text = text[0:-1]
        
    if len(text) > 0:
        if text[-1:] == '"':
            text = text[0:-1]
        
    return text
    


# 機能: URLエンコード文字の変換
# 引数1: 文字列
# 返値: URLエンコード文字に変換した文字列
# 
# URLに「#」「+」「/」「:」「=」などの記号を利用した場合エラーとなる場合がある。
# APIへの入力文字列（特にパスワードで記号を利用している場合）で注意が必要。
#   '#' →   '%23'
#   '+' →   '%2B'
#   '/' →   '%2F'
#   ':' →   '%3A'
#   '=' →   '%3D'
def func_replace_urlecnode( str_input ):
    str_encode = ''
    str_replace = ''
    
    for i in range(len(str_input)):
        str_char = str_input[i:i+1]

        if str_char == ' ' :
            str_replace = '%20'       #「 」 → 「%20」 半角空白
        elif str_char == '!' :
            str_replace = '%21'       #「!」 → 「%21」
        elif str_char == '"' :
            str_replace = '%22'       #「"」 → 「%22」
        elif str_char == '#' :
            str_replace = '%23'       #「#」 → 「%23」
        elif str_char == '$' :
            str_replace = '%24'       #「$」 → 「%24」
        elif str_char == '%' :
            str_replace = '%25'       #「%」 → 「%25」
        elif str_char == '&' :
            str_replace = '%26'       #「&」 → 「%26」
        elif str_char == "'" :
            str_replace = '%27'       #「'」 → 「%27」
        elif str_char == '(' :
            str_replace = '%28'       #「(」 → 「%28」
        elif str_char == ')' :
            str_replace = '%29'       #「)」 → 「%29」
        elif str_char == '*' :
            str_replace = '%2A'       #「*」 → 「%2A」
        elif str_char == '+' :
            str_replace = '%2B'       #「+」 → 「%2B」
        elif str_char == ',' :
            str_replace = '%2C'       #「,」 → 「%2C」
        elif str_char == '/' :
            str_replace = '%2F'       #「/」 → 「%2F」
        elif str_char == ':' :
            str_replace = '%3A'       #「:」 → 「%3A」
        elif str_char == ';' :
            str_replace = '%3B'       #「;」 → 「%3B」
        elif str_char == '<' :
            str_replace = '%3C'       #「<」 → 「%3C」
        elif str_char == '=' :
            str_replace = '%3D'       #「=」 → 「%3D」
        elif str_char == '>' :
            str_replace = '%3E'       #「>」 → 「%3E」
        elif str_char == '?' :
            str_replace = '%3F'       #「?」 → 「%3F」
        elif str_char == '@' :
            str_replace = '%40'       #「@」 → 「%40」
        elif str_char == '[' :
            str_replace = '%5B'       #「[」 → 「%5B」
        elif str_char == ']' :
            str_replace = '%5D'       #「]」 → 「%5D」
        elif str_char == '^' :
            str_replace = '%5E'       #「^」 → 「%5E」
        elif str_char == '`' :
            str_replace = '%60'       #「`」 → 「%60」
        elif str_char == '{' :
            str_replace = '%7B'       #「{」 → 「%7B」
        elif str_char == '|' :
            str_replace = '%7C'       #「|」 → 「%7C」
        elif str_char == '}' :
            str_replace = '%7D'       #「}」 → 「%7D」
        elif str_char == '~' :
            str_replace = '%7E'       #「~」 → 「%7E」
        else :
            str_replace = str_char
        str_encode = str_encode + str_replace        
    return str_encode


# 機能： ファイルから文字情報を読み込み、その文字列を返す。
# 戻り値： 文字列
# 第１引数： ファイル名
# 備考： json形式のファイルを想定。
def func_read_from_file(str_fname):
    str_read = ''
    try:
        with open(str_fname, 'r', encoding = 'utf_8') as fin:
            while True:
                line = fin.readline()
                if not len(line):
                    break
                str_read = str_read + line
        return str_read
    except IOError as e:
        print('ファイルを読み込めません!!! ファイル名：',str_fname)
        print(type(e))


# 機能: ファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 出力するデータ
# 備考:
def func_write_to_file(str_fname_output, str_data):
    try:
        with open(str_fname_output, 'w', encoding = 'utf-8') as fout:
            fout.write(str_data)
    except IOError as e:
        print('ファイルに書き込めません!!!  ファイル名：',str_fname_output)
        print(type(e))


# 機能: class_req型データをjson形式の文字列に変換する。
# 返値: json形式の文字
# 第１引数： class_req型データ
def func_make_json_format(work_class_req):
    work_key = ''
    work_value = ''
    str_json_data =  '{\n\t'
    for i in range(len(work_class_req)) :
        work_key = func_strip_dquot(work_class_req[i].str_key)
        if len(work_key) > 0:
            if work_key[:1] == 'a' :
                work_value = work_class_req[i].str_value
                str_json_data = str_json_data + work_class_req[i].str_key \
                                    + ':' + func_strip_dquot(work_value) \
                                    + ',\n\t'
            else :
                work_value = func_check_json_dquat(work_class_req[i].str_value)
                str_json_data = str_json_data + func_check_json_dquat(work_class_req[i].str_key) \
                                    + ':' + work_value \
                                    + ',\n\t'
    str_json_data = str_json_data[:-3] + '\n}'
    return str_json_data


# 機能： API問合せ文字列を作成し返す。
# 戻り値： api問合せのurl文字列
# 第１引数： ログインは、Trueをセット。それ以外はFalseをセット。
# 第2引数： ログインは、APIのurlをセット。それ以外はログインで返された仮想url（'sUrlRequest'等）の値をセット。
# 第３引数： 要求項目のデータセット。クラスの配列として受取る。
def func_make_url_request(auth_flg, \
                          url_target, \
                          work_class_req) :
    str_url = url_target
    if auth_flg == True :   # ログインの場合
        str_url = str_url + 'auth/'
    str_url = str_url + '?'
    str_url = str_url + func_make_json_format(work_class_req)
    return str_url


# 機能: API問合せ。通常のrequest,price用。
# 返値: API応答（辞書型）
# 第１引数： URL文字列。
# 備考: APIに接続し、requestの文字列を送信し、応答データを辞書型で返す。
#       master取得は専用の func_api_req_muster を利用する。
def func_api_req(str_url): 
    print('送信文字列＝')
    print(str_url)  # 送信する文字列

    # APIに接続
    http = urllib3.PoolManager()
    req = http.request('GET', str_url)
    print("req.status= ", req.status )

    # 取得したデータを、json.loadsを利用できるようにstr型に変換する。日本語はshift-jis。
    bytes_reqdata = req.data
    str_shiftjis = bytes_reqdata.decode("shift-jis", errors="ignore")

    print('返信文字列＝')
    print(str_shiftjis)

    # JSON形式の文字列を辞書型で取り出す
    json_req = json.loads(str_shiftjis)

    return json_req


# 機能： アカウント情報をファイルから取得する
# 引数1: 口座情報を保存したファイル名
# 引数2: 口座情報（class_def_account_property型）データ
def func_get_acconut_info(fname, class_account_property):
    str_account_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_account_info = json.loads(str_account_info)

    class_account_property.sUserId = json_account_info.get('sUserId')
    class_account_property.sPassword = json_account_info.get('sPassword')
    class_account_property.sSecondPassword = json_account_info.get('sSecondPassword')
    class_account_property.sUrl = json_account_info.get('sUrl')

    # 返り値の表示形式指定
    class_account_property.sJsonOfmt = json_account_info.get('sJsonOfmt')
    # "5"は "1"（1ビット目ON）と”4”（3ビット目ON）の指定となり
    # ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定


# 機能： ログイン情報をファイルから取得する
# 引数1: ログイン情報を保存したファイル名（fname_login_response = "e_api_login_response.txt"）
# 引数2: ログインデータ型（class_def_login_property型）
def func_get_login_info(str_fname, class_login_property):
    str_login_respons = func_read_from_file(str_fname)
    dic_login_respons = json.loads(str_login_respons)

    class_login_property.sResultCode = dic_login_respons.get('sResultCode')                 # 結果コード
    class_login_property.sResultText = dic_login_respons.get('sResultText')                 # 結果テキスト
    class_login_property.sZyoutoekiKazeiC = dic_login_respons.get('sZyoutoekiKazeiC')       # 譲渡益課税区分  1：特定  3：一般  5：NISA
    class_login_property.sSecondPasswordOmit = dic_login_respons.get('sSecondPasswordOmit')     # 暗証番号省略有無Ｃ
    class_login_property.sLastLoginDate = dic_login_respons.get('sLastLoginDate')               # 最終ログイン日時
    class_login_property.sSogoKouzaKubun = dic_login_respons.get('sSogoKouzaKubun')             # 総合口座開設区分  0：未開設  1：開設
    class_login_property.sHogoAdukariKouzaKubun = dic_login_respons.get('sHogoAdukariKouzaKubun')       # 保護預り口座開設区分  0：未開設  1：開設
    class_login_property.sFurikaeKouzaKubun = dic_login_respons.get('sFurikaeKouzaKubun')               # 振替決済口座開設区分  0：未開設  1：開設
    class_login_property.sGaikokuKouzaKubun = dic_login_respons.get('sGaikokuKouzaKubun')               # 外国口座開設区分  0：未開設  1：開設
    class_login_property.sMRFKouzaKubun = dic_login_respons.get('sMRFKouzaKubun')                       # ＭＲＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTokuteiKouzaKubunGenbutu = dic_login_respons.get('sTokuteiKouzaKubunGenbutu') # 特定口座区分現物  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunSinyou = dic_login_respons.get('sTokuteiKouzaKubunSinyou')   # 特定口座区分信用  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiKouzaKubunTousin = dic_login_respons.get('sTokuteiKouzaKubunTousin')   # 特定口座区分投信  0：一般  1：特定源泉徴収なし  2：特定源泉徴収あり
    class_login_property.sTokuteiHaitouKouzaKubun = dic_login_respons.get('sTokuteiHaitouKouzaKubun')   # 配当特定口座区分  0：未開設  1：開設
    class_login_property.sTokuteiKanriKouzaKubun = dic_login_respons.get('sTokuteiKanriKouzaKubun')     # 特定管理口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSinyouKouzaKubun = dic_login_respons.get('sSinyouKouzaKubun')         # 信用取引口座開設区分  0：未開設  1：開設
    class_login_property.sSakopKouzaKubun = dic_login_respons.get('sSakopKouzaKubun')           # 先物ＯＰ口座開設区分  0：未開設  1：開設
    class_login_property.sMMFKouzaKubun = dic_login_respons.get('sMMFKouzaKubun')               # ＭＭＦ口座開設区分  0：未開設  1：開設
    class_login_property.sTyukokufKouzaKubun = dic_login_respons.get('sTyukokufKouzaKubun')     # 中国Ｆ口座開設区分  0：未開設  1：開設
    class_login_property.sKawaseKouzaKubun = dic_login_respons.get('sKawaseKouzaKubun')         # 為替保証金口座開設区分  0：未開設  1：開設
    class_login_property.sHikazeiKouzaKubun = dic_login_respons.get('sHikazeiKouzaKubun')       # 非課税口座開設区分  0：未開設  1：開設  ※ＮＩＳＡ口座の開設有無を示す。
    class_login_property.sKinsyouhouMidokuFlg = dic_login_respons.get('sKinsyouhouMidokuFlg')   # 金商法交付書面未読フラグ  1：未読（標準Ｗｅｂを起動し書面確認実行必須）  0：既読  ※未読の場合、ｅ支店・ＡＰＩは利用不可のため    仮想ＵＲＬは発行されず""を設定。  ※既読の場合、ｅ支店・ＡＰＩは利用可能となり    仮想ＵＲＬを発行し設定。  
    class_login_property.sUrlRequest = dic_login_respons.get('sUrlRequest')     # 仮想URL（REQUEST)  業務機能    （REQUEST I/F）仮想URL
    class_login_property.sUrlMaster = dic_login_respons.get('sUrlMaster')       # 仮想URL（MASTER)  マスタ機能  （REQUEST I/F）仮想URL
    class_login_property.sUrlPrice = dic_login_respons.get('sUrlPrice')         # 仮想URL（PRICE)  時価情報機能（REQUEST I/F）仮想URL
    class_login_property.sUrlEvent = dic_login_respons.get('sUrlEvent')         # 仮想URL（EVENT)  注文約定通知（EVENT I/F）仮想URL
    class_login_property.sUrlEventWebSocket = dic_login_respons.get('sUrlEventWebSocket')    # 仮想URL（EVENT-WebSocket)  注文約定通知（EVENT I/F WebSocket版）仮想URL
    class_login_property.sUpdateInformWebDocument = dic_login_respons.get('sUpdateInformWebDocument')    # 交付書面更新予定日  標準Ｗｅｂの交付書面更新予定日決定後、該当日付を設定。  【注意】参照
    class_login_property.sUpdateInformAPISpecFunction = dic_login_respons.get('sUpdateInformAPISpecFunction')    # ｅ支店・ＡＰＩリリース予定日  ｅ支店・ＡＰＩリリース予定日決定後、該当日付を設定。  【注意】参照
    

# 機能： p_noをファイルから取得する
# 引数1: p_noを保存したファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: login情報（class_def_login_property型）データ
def func_get_p_no(fname, class_login_property):
    str_p_no_info = func_read_from_file(fname)
    # JSON形式の文字列を辞書型で取り出す
    json_p_no_info = json.loads(str_p_no_info)
    class_login_property.p_no = int(json_p_no_info.get('p_no'))
        
    
# 機能: p_noを保存するためのjson形式のテキストデータを作成します。
# 引数1: p_noを保存するファイル名（fname_info_p_no = "e_api_info_p_no.txt"）
# 引数2: 保存するp_no
# 備考:
def func_save_p_no(str_fname_output, int_p_no):
    # "p_no"を保存する。
    str_info_p_no = '{\n'
    str_info_p_no = str_info_p_no + '\t' + '"p_no":"' + str(int_p_no) + '"\n'
    str_info_p_no = str_info_p_no + '}\n'
    func_write_to_file(str_fname_output, str_info_p_no)
    print('現在の"p_no"を保存しました。 p_no =', int_p_no)            
    print('ファイル名:', str_fname_output)

#--- 以上 共通コード -------------------------------------------------





# 'sCLMID:CLMMfdsGetNewsHead'の利用方法
#
# 接続に使う仮想url: master用仮想URL
#
# 資料
# API専用ページ
# ５．マニュアル 
# １．共通説明
# （３）ブラウザからの利用方法
# 別紙「ｅ支店・ＡＰＩ、ブラウザからの利用方法」参照 のリンクをクリック。
# エクセルファイル「api_web_access.xlsx」を取得し開く。
# 「ニュース」シートを選択。
# 「ｅ支店・ＡＰＩ（ｖ４ｒ４）、ブラウザからの利用方法・ニュース情報取得編」
# 
##２－１．追加機能一覧								
##  No	機能ID			概要
##  1	CLMMfdsGetNewsHead      ニュースヘッダー問合取得I/F、ニュース一覧を（ニュースを取得した）降順に取得する。
##  2	CLMMfdsGetNewsBody      ニュースボディー問合取得I/F、個別のニュース内容を取得する。
##  ※ニュース関連システムの仕様で取得情報．ニュースIDの降順（取得順に採番される仕様）にソートしたリストを取得する。								
##  よって、データとしてニュース日付、ニュース時刻を返すが、その順序はニュース関連システムの仕様で保証されない。								
##
##（１）ニュースヘッダー問合取得I/F																		
##	【要求】																			
##	No  項目	    設定値												
##	1   sCLMID      CLMMfdsGetNewsHead												
##	2   p_CG ※１    取得したいカテゴリコードを１つ指定する。未指定時は全て対象。												
##	                コード     説明									
##	                100     QUICKニュース									
##	                110     ＡＩ市況状況速報									
##	                120     AI開示速報（決算関連）									
##	                129	ＡＩ開示速報（その他）									
##																				
##	    p_IS ※１         取得したい銘柄コードを１つ指定する。未指定時は全て対象。												
##	    p_DT_FROM ※１    ニュース日付（YYYYMMDD）範囲指定（from）。												N≧fromで検索。
##	    p_DT_TO ※１      ニュース日付（YYYYMMDD）範囲指定（to）。												N≦toで検索。
##	    p_REC_OFST ※１   レコード取得位置（デフォルト＝０、直近先頭の意味）。												指定条件検索後の位置。
##	    p_REC_LIMT ※１   レコード取得件数最大（デフォルト＝１００）。												指定条件検索後の件数。
##	※１、該当項目はオプション項目で指定した項目についてAND条件でデータ取得を実行する。
#
#
##【応答】																				
##No 項目		設定値													
##1 sCLMID		CLMMfdsGetNewsHead													
##2 p_REC_MAX	        取得（検索した）レコード数。													
##3 aCLMMfdsNewsHead    取得（検索した）レコード情報リスト（配列）。													
##	1 p_ID      ニュースID（レコード毎にユニーク）。													
##	2 p_DT	    ニュース日付（YYYYMMDD）。													
##	3 p_TM	    ニュース時刻（HHMMSS）。													
##	4 p_CGL	    ニュースカテゴリリスト。複数設定時は「,」区切り。	※１
##	5 p_GNL	    ニュースジャンルリスト。複数設定時は「,」区切り。	※１
##	6 p_ISL	    ニュース関連銘柄コードリスト。複数設定時は「,」区切り。						
##	7 p_HDL	    ニュースヘッドライン（タイトル）。   ※２						
##※１、カテゴリ及びジャンルについては別紙「立花証券・ｅ支店・ＡＰＩ、EVENT I/F 利用方法、データ仕様」３．（５）NSを参照。																				
##※２、ShiftJIS 日本語コード文字列を BASE64 変換し設定。取得側で各デコード後利用する。																				

#
# 補足1
# p_HDL、p_TXは、元の文字列をパーセントエンコード(URLエンコード)してから、base64変換されている。
# 元の文字列に戻すためには、base64でデコードしてから、パーセントエンコードのデコードを行う。
#
# 補足2
# p_DT_FROM <= p_DT_TO で設定する。p_DT_FROM > p_DT_TO では取得できない。
#
# 補足3
# p_REC_LIMT の最大値は100。
#
# 注意
# ニュースヘッダーは、時間軸で降順に取得される。
# このため当日分の取得の場合、新しいニュースが配信されると、
# p_REC_OFST で指定する起点の位置が新しく配信されたニュース分だけ後方にずれていく。
# 100を超えるニュースヘッダーを重複と漏れが無いように取得するためには、
# p_ID（ニュースID）を利用したチェックが必要になる。


# --- 以上資料 --------------------------------------------------------




# 機能: ニュースヘッダー取得
# 返値： 辞書型データ（APIからのjson形式返信データをshift-jisのstring型に変換し、更に辞書型に変換）
# 引数1: p_no
# 引数2: 取得したいカテゴリコードを１つ指定。未指定時は全て対象。										
#       コード     説明									
#	100     QUICKニュース									
#	110     ＡＩ市況状況速報									
#	120     AI開示速報（決算関連）									
#	129	ＡＩ開示速報（その他）
# 引数3: 取得したい銘柄コードを１つ指定する。未指定時は全て対象。
# 引数4: ニュース日付（YYYYMMDD）範囲指定（from）。
# 引数5: ニュース日付（YYYYMMDD）範囲指定（to）。
# 引数6: レコード取得位置（デフォルト＝０、直近先頭の意味）。
# 引数7: レコード取得件数最大（デフォルト＝１００）。
# 引数8: 口座属性クラス
# 備考: 引数2-7の項目で指定した項目についてAND条件でデータ取得を実行する。
def funcGetNewsHeader(int_p_no,
                        str_p_CG,
                        str_p_IS,
                        str_p_DT_FROM,
                        str_p_DT_TO,
                        str_p_REC_OFST,
                        str_p_REC_LIMT,
                        class_login_property
                        ):

    req_item = [class_req()]
    str_p_sd_date = func_p_sd_date(datetime.datetime.now())     # システム時刻を所定の書式で取得

    str_key = '"p_no"'
    str_value = func_check_json_dquat(str(int_p_no))
    #req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    str_key = '"p_sd_date"'
    str_value = str_p_sd_date
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # API request区分
    str_key = '"sCLMID"'
    str_value = 'CLMMfdsGetNewsHead'  # ニュースヘッダー取得を指示。
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)
    
    # 値が設定されず''になっている場合、
    # パラメーターとして送信するとエラーになるため、
    # パラメーターを送信しない処理が必要。
    #
    # 取得したいカテゴリコード
    if len(str_p_CG) > 0 :  
        str_key = '"p_CG"'
        str_value = str_p_CG
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)
    
    # 取得したい銘柄コード
    if len(str_p_IS) > 0 :
        str_key = '"p_IS"'
        str_value = str_p_IS
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)

    # ニュース日付（YYYYMMDD）範囲指定（from）
    if len(str_p_DT_FROM) > 0 :
        str_key = '"p_DT_FROM"'
        str_value = str_p_DT_FROM
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)

    # ニュース日付（YYYYMMDD）範囲指定（to）
    if len(str_p_DT_TO) > 0 :
        str_key = '"p_DT_TO"'
        str_value = str_p_DT_TO
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)

    # レコード取得位置
    if len(str_p_REC_OFST) > 0 :
        str_key = '"p_REC_OFST"'
        str_value = str_p_REC_OFST
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)

    # レコード取得件数最大    1度に取得できる最大値は100
    if len(str_p_REC_LIMT) > 0 :
        str_key = '"p_REC_LIMT"'
        str_value = str_p_REC_LIMT
        req_item.append(class_req())
        req_item[-1].add_data(str_key, str_value)


    # 返り値の表示形式指定
    str_key = '"sJsonOfmt"'
    str_value = class_login_property.sJsonOfmt    # "5"は "1"（ビット目ＯＮ）と”4”（ビット目ＯＮ）の指定となり「ブラウザで見や易い形式」且つ「引数項目名称」で応答を返す値指定
    req_item.append(class_req())
    req_item[-1].add_data(str_key, str_value)

    # URL文字列の作成
    # ニュースの取得は、master用仮想URL
    str_url = func_make_url_request(False, \
                                     class_login_property.sUrlMaster, \
                                     req_item)
    # API問合せ
    json_return = func_api_req(str_url)

    return json_return



# 機能: ニュース用タイトル行を出力ファイルに書き込む
# 引数1: 出力ファイル名
# 備考: 指定ファイルを開き、１行目に項目コード、２行目に項目名を書き込む。
def func_write_news_header_title(str_fname_output):
    try:
        with open(str_fname_output, 'w', encoding = 'shift_jis') as fout:
            print('file open at w, "fout": ', str_fname_output )
            # 項目コード
            str_text_out = ''
            str_text_out = str_text_out + 'p_ID' + ','
            str_text_out = str_text_out + 'p_DT' + ','
            str_text_out = str_text_out + 'p_TM' + ','
            str_text_out = str_text_out + 'p_CGL' + ','
            str_text_out = str_text_out + 'p_GNL' + ','
            str_text_out = str_text_out + 'p_ISL' + ','
            str_text_out = str_text_out + 'p_HDL' + '\n'
            fout.write(str_text_out)     # １行目に列名を書き込む

            # 項目名
            str_text_out = ''
            str_text_out = str_text_out + 'ニュースID（レコード毎にユニーク）。' + ','
            str_text_out = str_text_out + 'ニュース日付（YYYYMMDD）' + ','
            str_text_out = str_text_out + 'ニュース時刻（HHMMSS）' + ','
            str_text_out = str_text_out + 'ニュースカテゴリリスト' + ','
            str_text_out = str_text_out + 'ニュースジャンルリスト' + ','
            str_text_out = str_text_out + 'ニュース関連銘柄コードリスト' + ','
            str_text_out = str_text_out + 'ニュースヘッドライン（タイトル）' + '\n'
            fout.write(str_text_out)     # 2行目に列名を書き込む

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))





# 機能: ニュースヘッドライン（タイトル）、ニュースボディー（本文）をデコードする。
# 引数1: テキスト。string型。
# 備考:
# p_HDL、p_TXは、
# 元の文字列はshiftjisで、それをパーセントエンコード(URLエンコード)して、base64変換されている。
# 元の文字列に戻すためには、base64でデコードしてから、パーセントエンコードのデコードを行う。
#
# base64のデコード（base64.b64decode）は、引数の文字列をバイト型にしてから実行する。
# パーセントエンコード(URLエンコード)のデコード（urllib.parse.unquote）は、string型にしてから実行する。
# 
# デコードは、次の手順で行なう。
# string型で取得 →
#   byte型に変換 →
#       base64デコード: base64.b64decode() →
#           string型に変換 →
#               パーセントエンコードのデコード: urllib.parse.unquote()
def func_decode_base64_data(str_encoded_text):
    byte_base64_text = str_encoded_text.encode()        # string型のp_HDLをbyte型に変換
    byte_escape_text = base64.b64decode(byte_base64_text)  # base64でデコード。デコードされた文字列は、元のパーセントエンコード(URLエンコード)された文字列。
    str_escape_text = byte_escape_text.decode()         # urllib.parse.unquoteは引数がstring型。
    str_text = urllib.parse.unquote(str_escape_text, encoding='shift-jis')   # urllib.parse.unquote の第1引数は、string型。
    return str_text




# 機能: 取得したニュースヘッダーを追記モードでファイルに書き込む
# 引数1: 出力ファイル名
# 引数2: 取得したニュースヘッダー（リスト型）
# 備考:
#   指定ファイルを開き、1〜2行目に取得する情報名を書き込み、3行目以降で取得した情報を書き込む。
def func_write_news_header_data(str_fname_output, list_return):
    try:
        with open(str_fname_output, 'a', encoding = 'shift_jis') as fout:
            print('file open at a, "fout": ', str_fname_output )
            # 取得した情報から行データを作成し書き込む
            str_text_out = ''
            
            # ニュースヘッダーを取得できた場合。
            if list_return != None :
                for i in range(len(list_return)):
                    str_p_HDL = func_decode_base64_data(list_return[i].get('p_HDL'))
                    
                    # 行データ作成
                    str_text_out = ''
                    str_text_out = str_text_out + list_return[i].get('p_ID') + ',' 
                    str_text_out = str_text_out + list_return[i].get('p_DT') + ','
                    str_text_out = str_text_out + list_return[i].get('p_TM') + ','
                    str_text_out = str_text_out + list_return[i].get('p_CGL') + ','
                    str_text_out = str_text_out + list_return[i].get('p_GNL') + ','
                    str_text_out = str_text_out + '"' + list_return[i].get('p_ISL') + '"' + ','
                    str_text_out = str_text_out + '"' + str_p_HDL + '"' +'\n'

                    fout.write(str_text_out)     # 処理済みのニュースヘッダーをファイルに書き込む
                
                print('取得件数 len(list_return):', len(list_return))
                    
            # ニュースヘッダーを取得できない場合。
            else :
                str_text_out = 'ニュースヘッダーを取得できません。\n'
                print(str_text_out)
            

    except IOError as e:
        print('Can not Write!!!')
        print(type(e))
        


    




    
# ======================================================================================================
# ==== プログラム始点 =================================================================================
# ======================================================================================================
# 必要な設定項目
# 取得したいカテゴリコード: my_p_CG     未指定時は全て対象。100:QUICKニュース、110:ＡＩ市況状況速報、120:AI開示速報（決算関連）、129:ＡＩ開示速報（その他）
# 取得したい銘柄コード: my_p_IS       未指定時は全て対象。
# ニュース日付（YYYYMMDD）範囲指定（from）: my_p_DT_FROM
# ニュース日付（YYYYMMDD）範囲指定（to）: my_p_DT_TO      p_DT_FROM <= p_DT_TOで設定する。
# レコード取得位置: my_p_REC_OFST   デフォルト＝０、直近先頭の意味。
# レコード取得件数最大: my_p_REC_LIMT     デフォルト＝100。1回に取得できる最大件数は100。
# 出力ファイル名: my_fname_output  （デフォルトは、'news_header_[銘柄コード].csv'）

if __name__ == "__main__":

    # --- 利用時に変数を設定してください -------------------------------------------------------
    # コマンド用パラメーター -------------------    
    my_p_CG = ''            # 取得したいカテゴリコードを１つ指定。未指定時は全て対象。100:QUICKニュース、110:ＡＩ市況状況速報、120:AI開示速報（決算関連）、129:ＡＩ開示速報（その他）
    my_p_IS = ''            # 取得したい銘柄コードを１つ指定する。未指定時は全て対象。
    my_p_DT_FROM = ''       # ニュース日付（YYYYMMDD）範囲指定（from）。
    my_p_DT_TO = ''         # ニュース日付（YYYYMMDD）範囲指定（to）。 p_DT_FROM <= p_DT_TOで設定する。
    my_p_REC_OFST = ''      # レコード取得位置（デフォルト＝０、直近先頭の意味）。
    my_p_REC_LIMT = ''      # レコード取得件数最大（デフォルト＝１００）。1度に取得できる最大値は100。

    my_fname_output = 'news_header_' + my_p_IS + '.csv'   # 書き込むファイル名。カレントディレクトリに上書きモードでファイルが作成される。

    # --- 以上設定項目 -------------------------------------------------------------------------

    # --- ファイル名等を設定（実行ファイルと同じディレクトリ） ---------------------------------------
    fname_account_info = "./e_api_account_info.txt"
    fname_login_response = "./e_api_login_response.txt"
    fname_info_p_no = "./e_api_info_p_no.txt"
    # --- 以上ファイル名設定 -------------------------------------------------------------------------

    my_account_property = class_def_account_property()
    my_login_property = class_def_login_property()
    
    # 口座情報をファイルから読み込む。
    func_get_acconut_info(fname_account_info, my_account_property)
    
    # ログイン応答を保存した「e_api_login_response.txt」から、仮想URLと課税flgを取得
    func_get_login_info(fname_login_response, my_login_property)

    
    my_login_property.sJsonOfmt = my_account_property.sJsonOfmt                   # 返り値の表示形式指定
    my_login_property.sSecondPassword = func_replace_urlecnode(my_account_property.sSecondPassword)        # 22.第二パスワード  APIでは第2暗証番号を省略できない。 関連資料:「立花証券・e支店・API、インターフェース概要」の「3-2.ログイン、ログアウト」参照
    
    # 現在（前回利用した）のp_noをファイルから取得する
    func_get_p_no(fname_info_p_no, my_login_property)
    my_login_property.p_no = my_login_property.p_no + 1
    # "p_no"を保存する。
    func_save_p_no(fname_info_p_no, my_login_property.p_no)

    print()
    print('-- ニュースヘッダー 取得  -------------------------------------------------------------')

    # ニュースヘッダー取得
    dic_return = funcGetNewsHeader(my_login_property.p_no,
                                    my_p_CG,
                                    my_p_IS,
                                    my_p_DT_FROM,
                                    my_p_DT_TO,
                                    my_p_REC_OFST,
                                    my_p_REC_LIMT,
                                    my_login_property
                                    )

    if dic_return.get('p_errno') != '-2' and dic_return.get('p_errno') != '2':
        # 出力ファイルにタイトル行を書き込む。
        func_write_news_header_title(my_fname_output)
        
        # ニュースヘッダー部分をリスト型で抜き出す。
        my_list_return = dic_return.get('aCLMMfdsNewsHead')

        # 取得したニュースヘッダーを追記モードでファイルに書き込む。
        func_write_news_header_data(my_fname_output, my_list_return)

    elif dic_return.get('p_errno') == '-2' :
        print("パラメーターの設定に誤りが有ります。")

    # 仮想URLが無効になっている場合
    # if dic_return.get('p_errno') == '2':
    else:
        print()
        print('p_errno', dic_return.get('p_errno'))
        print('p_err', dic_return.get('p_err'))
        print()    
        print("仮想URLが有効ではありません。")
        print("電話認証 + e_api_login_tel.py実行")
        print("を再度行い、新しく仮想URL（1日券）を取得してください。")    
    
    

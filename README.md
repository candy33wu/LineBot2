# LineBot2
對發票機器人(含爬蟲)

- 架設於 Heroku
## 主要目標:  
此程式主要執行目標為實作出一LineBot，該LineBot提供對發票服務 

## 程式運行方式:  

**LINE**    
請將LineBot加入好友

<img src="https://upload.cc/i1/2020/10/22/KW4CXi.png" width = "200" height = "200" alt="LineBotInformation" align=center />

## 簡要使用說明:   

- 點擊對話界面下方選單

  <img src="https://upload.cc/i1/2020/10/22/Pyr8R1.png" width = "200" height = "350" alt="Menu" align=center />

- 選擇所需功能

   <img src="https://upload.cc/i1/2020/10/22/hNCs8I.png" width = "200" height = "350" alt="Menu" align=center /> 

> 使用範例    
  
  - 對獎(中獎)
  
    <img src="https://upload.cc/i1/2020/10/22/onrb1D.png" width = "180" height = "180" alt="中獎" align=center /> 
    
  - 對獎(未中獎)
   
    <img src="https://upload.cc/i1/2020/10/22/18B4ND.png" width = "180" height = "160" alt="未中獎" align=center />
   
  - 前期中獎號碼、本期中獎號碼
    
    <img src="https://upload.cc/i1/2020/10/22/wGHuEU.png" width = "200" height = "350" alt="中獎號碼" align=center />
  

## 程式結構說明:    
```py
from flask import Flask
app = Flask(__name__)

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage ,ImageSendMessage, StickerSendMessage ,LocationSendMessage, MessageAction, QuickReply, QuickReplyButton

import requests
try:
	import xml.etree.cElementTree as ET
except ImportError:
	import xml.etree.ElementTree as ET

line_bot_api = LineBotApi('iL66PL4mgXCJj43T9IqelN8zZrFfm89g0mqrGkvL7vzzASHV4Fg1MNadzl8uuf8OHlr70wKc23eS4tBcsRw/7/t5aU+X7UnnOl5mTz7WHSRQK7YP/BxU+SDJz/ozB9i7mqiyCIUTkCELWq1aNBQTeQdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('0604fc94e673267be9cea8c6a0d560b0')
```

- 使用 Flask 模組建立網站伺服器

```py
@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']
	body = request.get_data(as_text=True)
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'
```

- 建立 callback 路由，檢查LINE Bot 的資料是否正確

```py
content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
tree = ET.fromstring(content.text)
```

- 財政部提供了 RSS 發票中獎號碼 XML 網頁 [Link]('https://invoice.etax.nat.gov.tw/invoice.xml')
- 從根目錄開始XML 解析，使用xml.etree.ElementTree 模組 ```變數=ET.fromstring(XML 文字內容)``` 取得根目錄

```py
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	mtext = event.message.text
	if len(mtext) == 3 and mtext.isdigit():       
		try:
			items = list(tree.iter(tag = 'item')) #找標籤資料
			ptext = items[0][2].text
			ptext = ptext.replace('<p>','').replace('</p>','\n')[:-1]
			temlist = ptext.split('：')
			prizelist = []
			prizelist.append(temlist[1][5:8]) #取中獎號碼後三碼，放入陣列儲存
			prizelist.append(temlist[2][5:8])
			for i in range(3):
				prizelist.append(temlist[3][9*i+5:9*i+8]) #頭獎有三個，取中獎號碼後三碼，放入陣列儲存
			sixlist = temlist[4].split('、')
			for i in range(len(sixlist)): #將增開的六獎(3碼數字)直接存入陣列
				prizelist.append(sixlist[i])
			if mtext in prizelist:
				message = TextSendMessage( text = '符合某獎項後三碼，請自行核對發票前五碼!\n\n' + monoNum(0))

			else:
				message = TextSendMessage( text = '很可惜，未中獎。請輸入下一張發票最後三碼。')
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票最後三碼進行對獎!'))
	elif mtext == '@輸入發票最後三碼':
		try:
			message = TextSendMessage( text = "請輸入發票最後三碼進行對獎！")
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票最後三碼進行對獎!'))
```

- 若輸入三碼數字，則對照本期中獎號碼，判定是否中獎
- 若點擊選單 "對獎" ，告知使用者對獎輸入方式

```py
	elif mtext == '@前期中獎號碼':
		try:
			items = list(tree.iter(tag = 'item'))
			message = TextSendMessage( text = monoNum(1)+'\n\n'+monoNum(2))
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤!'))

	elif mtext == '@本期中獎號碼':
		try:
			items = list(tree.iter(tag = 'item'))
			message = TextSendMessage( text = monoNum(0))
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='發生錯誤!'))
	else:            
		line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text)) 
```
- 若點擊選單 "本期中獎號碼" ，回傳該期中獎資料
- 若點擊選單 "前期中獎號碼" ，回傳前兩期中獎資料(前兩期中獎發票仍可兌換)

- 其中使用到 monoNum(): 用以輸出指定期數之中獎資料，為排版方便

```py
def monoNum(n):
	items = list(tree.iter(tag = 'item'))
	title = items[n][0].text
	ptext = items[n][2].text
	ptext = ptext.replace('<p>','').replace('</p>','\n')
	return title + '月\n' + ptext[:-1]
```

## 待改進之問題:
- 程式中有些 "對"獎，誤入為 "兌"獎


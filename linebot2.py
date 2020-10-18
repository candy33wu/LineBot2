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
@app.route("/callback", methods=['POST'])
def callback():
	signature = request.headers['X-Line-Signature']
	body = request.get_data(as_text=True)
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		abort(400)
	return 'OK'

content = requests.get('https://invoice.etax.nat.gov.tw/invoice.xml')
tree = ET.fromstring(content.text)

def monoNum(n):
	items = list(tree.iter(tag = 'item'))
	title = items[n][0].text
	ptext = items[n][2].text
	ptext = ptext.replace('<p>','').replace('</p>','\n')
	return title + '月\n' + ptext[:-1]
	#message = TextSendMessage( text = items[1][0].text + '月\n' + items[1][2].text.replace('<p>','').replace('</p>','\n')[:-1])


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
	mtext = event.message.text
	if len(mtext) == 3 and mtext.isdigit():       
		try:
			items = list(tree.iter(tag = 'item'))
			ptext = items[0][2].text
			ptext = ptext.replace('<p>','').replace('</p>','\n')[:-1]
			temlist = ptext.split('：')
			prizelist = []
			prizelist.append(temlist[1][5:8])
			prizelist.append(temlist[2][5:8])
			for i in range(3):
				prizelist.append(temlist[3][9*i+5:9*i+8])
			sixlist = temlist[4].split('、')
			for i in range(len(sixlist)):
				prizelist.append(sixlist[i])
			if mtext in prizelist:
				message = TextSendMessage( text = '符合某獎項後三碼，請自行核對發票前五碼!\n\n' + monoNum(0))

			else:
				message = TextSendMessage( text = '很可惜，未中獎。請輸入下一張發票最後三碼。')
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票最後三碼進行兌獎!'))
	elif mtext == '@輸入發票最後三碼':
		try:
			message = TextSendMessage( text = "請輸入發票最後三碼進行對獎！")
			line_bot_api.reply_message(event.reply_token,message)
		except:
			line_bot_api.reply_message(event.reply_token, TextSendMessage(text='請輸入發票最後三碼進行兌獎!'))
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
        
		

if __name__ == '__main__':
	app.run()
	

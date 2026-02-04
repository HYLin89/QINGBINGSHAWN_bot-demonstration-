from flask import Flask,request,abort
from linebot import LineBotApi,WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent,TextMessage,TextSendMessage,ImageMessage,FlexSendMessage,BubbleContainer,CarouselContainer,PostbackEvent
import os,datetime
from ultralytics import YOLO
import emoji
from urllib.parse import parse_qs
import sys

app=Flask(__name__)
model = YOLO('best.pt')

if (not os.path.exists('static')):
    try:

        os.mkdir('static')
    except OSError as e:
        print(e)


from search_logic import search_recipes


channel_access_token = os.environ.get('CHANNEL_ACCESS_TOKEN')
channel_secret=os.environ.get('CHANNEL_SECRET')
if (not channel_access_token or not channel_secret):
    try:
        import config
        channel_access_token = config.CHANNEL_ACCESS_TOKEN
        channel_secret=config.CHANNEL_SECRET
    except Exception as e:
        print('cant find token or secret:'+e)
        sys.exit(1)



# Line initialization
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

#---------------------bot_handshake-----------------------------


@app.route('/callback',methods=['POST'])
#web-server test
def callback():
    signature=request.headers['X-Line-Signature']
    body=request.get_data(as_text=True)
    # print("HERES BODY : "+body)
    try:
        handler.handle(body,signature)
    except InvalidSignatureError:
        # print('signature FAiled')
        abort(400)
    return 'OK'


#message (text) response - searching and response recipes
@handler.add(MessageEvent,message=TextMessage)
def handle_message(event):
    user_msg=event.message.text.strip()
    #string control
    if (user_msg.lower().startswith('test:')):
        
        input_str=user_msg[5:]
        if ('、' in input_str or ',' in input_str):
            print(input_str)
            input_str=input_str.replace('、',',').split(',')
        else:
            print(type([input_str]))
            input_str=[input_str]

        ingredient=[x.strip() for x in input_str if x.strip()]
        results=search_recipes(ingredient)
        if (not results):
            reply_txt='我找不到符合的食譜 \U0001FAE0'
        else:
            reply_txt='今晚你可以來點：\n'
            for r in results:
                reply_txt+=f"{r['食譜']}\n"
                reply_txt+=f"{r['url']}\n"
                reply_txt+='-' * 10+ '\n'
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_txt)
        )


    else:
        #bot echoes(only for test)
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=f'SUCCESS, THE USER says {user_msg}')
        )


#--------------computer vision setting------------------------

#message (image) response
@handler.add(MessageEvent,message=ImageMessage)
def handler_image(event):
    message_img_content=line_bot_api.get_message_content(event.message.id)
    file_name=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')+'.jpg'
    save_path=os.path.join('static',file_name)
    with open (save_path,'wb') as f:
        for chunk in message_img_content.iter_content():
            f.write(chunk)

    #call YOLO model
    results=model.predict(source=save_path,conf=0.5)
    
    detect_tags=set()#extract tags as sets

    for result in results:
        for box in result.boxes:
            class_id=int(box.cls[0])
            class_name=model.names[class_id]
            detect_tags.add(class_name)
    
    tagList=list(detect_tags)
    print(f'the results: {tagList}')

    #search recipes from tag list
    if (not tagList):
        reply_msg=TextSendMessage(text='抱歉，請試試換個角度再給我看一次🥺\n請試著拍得再清楚一點，或是看我看其他食材')
    else:

        #first search
        recommanded_recipes,has_more=search_recipes(tagList,start_idx=0,count=5)
        
        if recommanded_recipes:
            if has_more:
                next_idx=5
            else:
                None

            try:
                
                reply_msg=create_recipe_flex(recommanded_recipes,tagList,next_idx)
            except Exception as e:
                print(f'-->氣泡錯誤bubble error: {e}')
                reply_txt='今晚你可以來點：\n'
                for r in recommanded_recipes:
                    reply_txt+=f"{r['食譜']}\n"
                    reply_txt+=f"{r['url']}\n"
                    reply_txt+='-' * 10+ '\n'
                reply_msg=reply_txt
        else:
            reply_txt='現在我找不到符合的食譜 \U0001FAE0'




    line_bot_api.reply_message(
        event.reply_token,
        reply_msg
    )


#------------------------look more-----------------------
@handler.add(PostbackEvent)
def handle_postback(event):
    data=event.postback.data
    params=parse_qs(data)

    action=params['action'][0]
    if action == 'more':
        start_idx=int(params['start'][0])
        tags_str=params['tags'][0]
        tags_list=tags_str.split(',')

        recipes,has_more=search_recipes(tags_list,start_idx=start_idx,count=5)

        if (recipes):
            if (has_more):
                next_index=(start_idx+5)
            else:
                None
            flex_msg=create_recipe_flex(recipes,tags_list,next_index)
            line_bot_api.reply_message(
                event.reply_token,
                flex_msg
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='目前我想不到更多食譜了 🥴')
            )


#-----------------------flex_message---------------------
def create_recipe_flex(recipes,current_ingreds,next_start_index):
    
    #store recipes into LINE flex message
    bubbles=[]
    for recipe in recipes:
        match_score=recipe['match_score']
        header_color = '#B2FF59' if match_score>=2 else '#FFCA28'
        status_text='高度吻合' if match_score>=2 else '相關食譜'
        bubble = {
            "type": "bubble",
            "size": "micro", 
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": header_color,
                "paddingAll": "sm",
                "contents": [
                    {
                        "type": "text",
                        "text": status_text,
                        "color": "#00000080",
                        "size": "xs",
                        "weight": "bold",
                        "align": "center"
                    }
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "paddingAll": "md", 
                "contents": [

                    {
                        "type": "text",
                        "text": recipe['食譜'],
                        "weight": "bold",
                        "size": "sm",
                        "wrap": True,
                        "maxLines": 3,
                        "align": "start" 
                    },
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "link",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "👉 查看食譜",
                            "uri": recipe['url']
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble)
    
    if (next_start_index is not None):
        ingredients_str=','.join(current_ingreds)   #sent present results as list
        more_bubble = {
            "type": "bubble",
            "size": "micro",
            "body": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#E8F8F5",
                "justifyContent": "center",
                "height": "100%",
                "contents": [
                    {
                        "type": "text",
                        "text": "發現更多 🔎",
                        "size": "xs",
                        "color": "#888888",
                        "align": "center"
                    },
                    {
                        "type": "text",
                        "text": "看下 5 筆",
                        "size": "md",
                        "weight": "bold",
                        "color": "#27AE60",
                        "align": "center",
                        "margin": "sm"
                    }
                ]
            },
            "action": {

                "type": "postback",
                "label": "看更多",

                "data": f"action=more&start={next_start_index}&tags={ingredients_str}",
                "displayText": "我想要更多食譜"
            }
        }
        bubbles.append(more_bubble)

    return FlexSendMessage(
        alt_text="Here's your recipes, Bon Apetit !!",
        contents=CarouselContainer(contents=bubbles)
    )





if __name__=="__main__":

    port=int(os.environ.get('PORT',5000))
    app.run(host='0.0.0.0',port=port)








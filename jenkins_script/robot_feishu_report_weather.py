# -*- coding:UTF-8 -*-
import json
import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


count = 3


while count:
    try:
        import requests
        print 'requests已经安装'
        break
    except:
        print '开始安装requests'
        os.system('pip install requests')
        count -= 1
        continue




def get_tenant_access_token(tenant_access_token_url, appId, appSecret):
    header = {'Content-Type': 'application/json'}
    data = {"app_id": appId, "app_secret": appSecret}
    result = requests.post(tenant_access_token_url, data=json.dumps(data), headers=header,)
    tenant_access_token = result.json()["tenant_access_token"]
    return tenant_access_token


def get_ChatId(tenant_access_token, chatId_url):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % tenant_access_token}
    params = {'Authorization': tenant_access_token, 'page_size': '20'}
    result = requests.get(chatId_url, headers=header, params=params)
    chat_id = result.json()['data']["groups"][0]['chat_id']
    return chat_id


def get_weather():
    params = {"cityid":"101020100"}
    result_weather = requests.get('https://www.tianqiapi.com/free/week?appid=62548893&appsecret=5zlbcJul', params=params)
    weather = result_weather.json()['data'][1]['wea']
    max_tem = result_weather.json()['data'][1]['tem_day']
    min_tem = result_weather.json()['data'][1]['tem_night']
    wind_speed = result_weather.json()['data'][1]['win_speed']
    return ("明日上海天气：{0}, 温度：{1}～{2}，风速：{3}   注意：今日的日报记得写一下～").format(weather, max_tem, min_tem, wind_speed)


def send_msg(send_msg_url,  tenant_access_token, chat_id):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % tenant_access_token}
    data = {"chat_id": chat_id, "msg_type": "text", "content": {
        "text": "%s<at user_id='all'></at>" %(get_weather())
    }
}
    result = requests.post(send_msg_url, headers=header, data=json.dumps(data))
    return result.json()


if __name__ == '__main__':
    # token 数据获取
    appId = '*************'
    appSecret = '**********************'
    tenant_access_token_url = 'https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/'
    tenant_access_token = get_tenant_access_token(tenant_access_token_url, appId, appSecret)

    # chat_id 数据获取
    chaId_url = 'https://open.feishu.cn/open-apis/chat/v4/list'
    chat_id = get_ChatId(tenant_access_token, chaId_url)

    # send_msg 数据获取
    send_msg_url = 'https://open.feishu.cn/open-apis/message/v4/send/'
    send_msg(send_msg_url, tenant_access_token, chat_id)

    print 'well done'




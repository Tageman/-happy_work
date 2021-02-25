# -*- coding:utf-8 -*-
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')

from flask import Flask, request
import requests
import json
app = Flask(__name__)



@app.route('/ssapi', methods=['POST'])
def ssapi():
    data = json.loads(request.data)
    chat_id = data['event']['open_chat_id']
    user_id = data['event']['user_open_id']
    msg_user = data['event']['text_without_at_bot'].strip()
    msg_reply_result = requests.get('http://api.qingyunke.com/api.php?key=free&appid=0&msg=%s' % msg_user)
    msg_reply = msg_reply_result.json()['content']
    send_msg(user_id, chat_id, msg_reply)
    return request.data.decode('utf8')

@app.route('/sstapd', methods=['POST'])
def sstapd():
    event = request.form.get('event')
    event_from = request.form.get('event_from')
    workspace_id = request.form.get('workspace_id')
    id = request.form.get('id')
    secret = request.form.get('secret')
    created = request.form.get('created')
    print(event, event_from, workspace_id, id, secret, created)
    return request.data


def get_token():
    appId = '******************'
    appSecret = '***********************'
    header_token = {'Content-Type': 'application/json'}
    data_token = {"app_id": appId, "app_secret": appSecret}
    result_token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
                                 data=json.dumps(data_token), headers=header_token, )
    tenant_access_token = result_token.json()["tenant_access_token"]
    return tenant_access_token

def send_msg(user_id, chat_id, msg_reply):
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % get_token()}
    data = {"chat_id": chat_id, "msg_type": "text", "content": {
        "text": "<at user_id=\"%s\"></at>%s" % (user_id, msg_reply)
    }
}
    result = requests.post('https://open.feishu.cn/open-apis/message/v4/send/', headers=header, data=json.dumps(data))
    return result.json()


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=9999)

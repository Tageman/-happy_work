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

# 接收来自tapd的消息
@app.route('/sstapd', methods=['POST'])
def sstapd():
    event = request.form.get('event')
    event_from = request.form.get('event_from')
    workspace_id = request.form.get('workspace_id')
    bug_id = request.form.get('id')
    secret = request.form.get('secret')
    created = request.form.get('created')
    print(event, event_from, workspace_id, bug_id, secret, created)

    # 调用get_tapd()函数获取到信息 然后组成数据调用send函数发送数据
    workspace_names, bug_titles, current_owners = get_tapd(workspace_id, bug_id)

    # 获取机器人所在群组
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % get_token()}
    result = requests.get('https://open.feishu.cn/open-apis/chat/v4/list', headers=header)
    robot_chat_id = result.json()['data']['groups'][0]['chat_id']

    data = {"chat_id": robot_chat_id, "msg_type": "text", "content": {
        "text": "@%s 您有一条新的bug在【%s中】 bug标题:%s ; 请及时修改～" % (current_owners[0], workspace_names[0], bug_titles[0])
    }
            }
    # 发送消息
    requests.post('https://open.feishu.cn/open-apis/message/v4/send/', headers=header, data=json.dumps(data))



    return request.data



# 根据接收的tapd的消息获取tapd对应的处理人、workspace_id对应的名称
def get_tapd(workspace_id, bug_id):
    workspace_name = []
    bug_titles = []
    current_owners = []


    # base meassage
    api_user =  "***********嘿嘿***********"
    api_password =  "***********嘿嘿***********"
    company_id =  "***********嘿嘿***********"

    # 获取bug current_owner and bug_title 将其加入到数组中
    bug_url = "https://api.tapd.cn/bugs?workspace_id=%s" %(workspace_id)
    bug_data = {"id": bug_id}
    bug_result = requests.get(bug_url, params=bug_data, auth=(api_user, api_password))
    bug_titles.append(bug_result.json()['data']['Bug']['title'])
    current_owners.append(bug_result.json()['data']['Bug']['current_owner'].split(";")[0])

    # 获取bug所在project并将其加入到数组中
    project_url = "https://api.tapd.cn/workspaces/projects?company_id=%s" %(company_id)
    project_result = requests.get(project_url, auth=(api_user, api_password))
    for workspace in project_result.json()['data']:
        if workspace['Workspace']['id'] == workspace_id:
            workspace_name.append(workspace['Workspace']['name'])


    return workspace_name, bug_titles, current_owners


# 获取飞书token
def get_token():
    appId =  "***********嘿嘿***********"
    appSecret =  "***********嘿嘿***********"
    header_token = {'Content-Type': 'application/json'}
    data_token = {"app_id": appId, "app_secret": appSecret}
    result_token = requests.post('https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal/',
                                 data=json.dumps(data_token), headers=header_token, )
    tenant_access_token = result_token.json()["tenant_access_token"]
    return tenant_access_token

# 发送信息到飞书
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

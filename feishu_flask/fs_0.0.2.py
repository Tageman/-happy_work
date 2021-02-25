# -*- coding:utf-8 -*-
import sys
if sys.getdefaultencoding() != 'utf-8':
    reload(sys)
    sys.setdefaultencoding('utf-8')



from flask import Flask, request
import requests
import json
import logging
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
    # 打印日志
    request_form_data = request.form
    app.logger.info("data %s" % (request_form_data))

    # 调用get_tapd()函数获取到信息 然后组成数据调用send函数发送数据
    workspace_names, bug_titles, current_owners = get_tapd(workspace_id, bug_id)

    # 获取机器人所在群组(这个地方获取一下当前bug worksapce_id下的群成员 组成一个临时的 字典 然后bug的current与email做匹配之后 将email 当作私信发送出去)
    header = {'Content-Type': 'application/json', 'Authorization': 'Bearer %s' % get_token()}

    if current_owners[0] in get_user_email(workspace_id).keys():
	    user_email = get_user_email(workspace_id)[current_owners[0]]
	    email = user_email.split('@')[0] + "@" +"infoloop.cn"
	    print email
        data = {"email": email, "msg_type": "text", "content": {
            "text": "您于(%s)收到一条新的bug在【%s中】bug标题：%s； 请及时修改～[回复TD退订！]" % (created, workspace_names[0], bug_titles[0])
        }
            }
        #发送消息
        ss_result = requests.post('https://open.feishu.cn/open-apis/message/v4/send/', headers=header, data=json.dumps(data))
	    print ss_result.json()
    return request.data




# 获取当前项目下的所有的用户的email以及username
def get_user_email(workspace_id):
    username_useremail = {}
    api_user = "********"
    api_password =  "***********嘿嘿***********"
    user_email_url = "https://api.tapd.cn/workspaces/users?workspace_id=%s&fields=user,email" %(workspace_id)
    user_email_result = requests.get(user_email_url, auth=(api_user, api_password))
    for data in user_email_result.json()['data']:
       username_useremail[data["UserWorkspace"]["user"]] = data["UserWorkspace"]["email"]
    return username_useremail


# 根据接收的tapd的消息获取tapd对应的处理人、workspace_id对应的名称
def get_tapd(workspace_id, bug_id):
    workspace_name = []
    bug_titles = []
    current_owners = []


    # base meassage TAPD基础信息需要隐藏
    api_user = "********"
    api_password = "***********嘿嘿***********"
    company_id = "*****哈哈*****"

    # 获取bug current_owner and bug_title 将其加入到数组中
    bug_url = "https://api.tapd.cn/bugs?workspace_id=%s" %(workspace_id)
    bug_data = {"id": bug_id}
    bug_result = requests.get(bug_url, params=bug_data, auth=(api_user, api_password))
    bug_titles.append(bug_result.json()['data']['Bug']['title'])
    # 如果创建的时候没有填写处理人名称 直接赋值ren.xiaogang@infoloop.cn 然后去监督测试正常报问题
    if bug_result.json()['data']['Bug']['current_owner'] != None:
        current_owners.append(bug_result.json()['data']['Bug']['current_owner'].split(";")[0])
    else:
        current_owners.append(u'\u4efb\u5c0f\u521a')

    # current_owners.append(bug_result.json()['data']['Bug']['current_owner'].split(";")[0])

    # 获取bug所在project并将其加入到数组中
    project_url = "https://api.tapd.cn/workspaces/projects?company_id=%s" %(company_id)
    project_result = requests.get(project_url, auth=(api_user, api_password))
    for workspace in project_result.json()['data']:
        if workspace['Workspace']['id'] == workspace_id:
            workspace_name.append(workspace['Workspace']['name'])


    return workspace_name, bug_titles, current_owners


# 获取飞书token
def get_token():
    appId = '**************' # 飞书相关
    appSecret = '******************' # 飞书相关
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
    app.debug = True
    handler = logging.FileHandler('/data/feishu_flask/flask.log', encoding='UTF-8')
    handler.setLevel(logging.DEBUG)
    logging_format = logging.Formatter("%(asctime)s flask %(levelname)s %(message)s")
    handler.setFormatter(logging_format)
    app.logger.addHandler(handler)

    app.run(host='0.0.0.0', port=9999)

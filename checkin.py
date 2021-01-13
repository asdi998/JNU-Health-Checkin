from base64 import b64encode
from datetime import datetime
from json import loads
from os import getenv
from traceback import format_exc
from typing import Optional

from Crypto.Cipher import AES
from requests import post


class STUHealth():
    def __init__(self, username, password) -> None:
        self.remove_list = ['personType', 'id', 'createTime', 'del']
        self.api = 'https://stuhealth.jnu.edu.cn/api/'
        self.headers = {
            'Connection': 'keep-alive',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
            'Content-Type': 'application/json',
            'Origin': 'https://stuhealth.jnu.edu.cn',
            'Sec-Fetch-Site': 'same-origin',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Dest': 'empty',
            'Referer': 'https://stuhealth.jnu.edu.cn/',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        self.login(username, password)

    def query(self, api, data) -> str:
        response = post(self.api+api, headers=self.headers, json=data)
        result = loads(response.text)
        success = result['meta']['success']
        msg = result['meta']['msg']
        self.result = result
        if not success:
            raise Exception(msg)
        print(msg)
        return msg

    @staticmethod
    def encrypt(password) -> str:
        CRYPTOJSKEY = 'xAt9Ye&SouxCJziN'.encode('utf-8')
        BS = AES.block_size
        def pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        cipher = AES.new(CRYPTOJSKEY, AES.MODE_CBC, CRYPTOJSKEY)
        enrypted = b64encode(cipher.encrypt(
            pad(password).encode('utf-8'))).decode('utf-8')
        enrypted = enrypted.replace(
            '/', '_').replace('+', '-').replace('=', '*', 1)
        return enrypted

    def filter_table(self, table) -> dict:
        new_table = {k: v for k, v in table.items() if v}
        for i in self.remove_list:
            del new_table[i]
        if 'way2Start' not in new_table:
            new_table['way2Start'] = ""
        new_table['declareTime'] = datetime.now().strftime("%Y-%m-%d")
        return new_table

    def login(self, username, password) -> None:
        if len(password) != 24:
            password = STUHealth.encrypt(password)
        api = 'user/login'
        data = {"username": username, "password": password}
        self.login_msg = self.query(api, data)
        self.idtype = self.result['data']['idtype']
        self.jnuid = self.result['data']['jnuid']
        self.jnuId = self.result['data']['jnuId']
        self.wrote = (self.result['meta']['code'] != 200)

    def stuinfo(self) -> dict:
        api = 'user/stuinfo'
        data = {"jnuid": self.jnuid, "idType": self.idtype}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        return mainTable

    def stucheckin(self) -> int:
        api = 'user/stucheckin'
        data = {"jnuid": self.jnuid}
        self.query(api, data)
        checkinInfo = self.result['data']['checkinInfo']
        last_id = 0
        for info in checkinInfo:
            if info['flag'] == True:
                last_id = info['id']
                break
        return last_id

    def review(self, id) -> dict:
        api = 'user/review'
        data = {"jnuid": self.jnuid, "id": id}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        return mainTable

    def write(self, mainTable) -> tuple:
        api = 'write/main'
        data = {"jnuid": self.jnuid, "mainTable": mainTable}
        return self.query(api, data)


def sc_send(text, desp='') -> None:
    postdata = {'text': text, 'desp': desp}
    post('http://sc.ftqq.com/'+SCKEY+'.send', data=postdata)


def checkin(username, password) -> Optional[str]:
    try:
        stu = STUHealth(username, password)
        print(stu.login_msg)
        if stu.wrote:
            return
        last_id = stu.stucheckin()
        last_table = stu.review(last_id)
        mainTable = stu.filter_table(last_table)
        msg = stu.write(mainTable)
        return "打卡{}：{}".format(username, msg)
    except Exception as e:
        print('发生异常{}，详情如下：{}'.format(e, format_exc()))
        return "打卡错误{}：{}".format(username, e)


if __name__ == "__main__":
    # accounts settings
    usernames, passwords, SCKEY = getenv('USERNAME').split(), getenv('PASSWORD').split(), getenv('SCKEY')
    accounts = [ (username,password) for username in usernames for password in passwords ]
    # run
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    push_msg = []
    for account in accounts:
        print("开始打卡...")
        msg = checkin(*account)
        if msg is not None:
            push_msg.append(msg)
    if SCKEY and push_msg:
        print('发送微信推送...')
        sc_send('\n\n'.join(push_msg))

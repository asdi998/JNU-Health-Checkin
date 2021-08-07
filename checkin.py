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
        # Init
        CRYPTOJSKEY = 'xAt9Ye&SouxCJziN'.encode('utf-8')
        BS = AES.block_size
        def _pad(s): return s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
        # Hash
        cipher = AES.new(CRYPTOJSKEY, AES.MODE_CBC, CRYPTOJSKEY)
        enrypted = cipher.encrypt(_pad(password).encode('utf-8'))
        enrypted = b64encode(enrypted).decode('utf-8')
        enrypted = enrypted.replace('/', '_').replace('+', '-').replace('=', '*', 1)
        return enrypted

    @staticmethod
    def filter_tables(mainTable, secondTable) -> tuple:
        # Init
        REMOVE_LIST = ['personType', 'id', 'createTime', 'del', 'mainId']
        MAIN_ADD_LIST = ['way2Start']
        MAIN_TO_SECOND = {
            'inChina': 'other1',
            'countryArea': 'other2',
            'personC4': 'other3',
            'personC1': 'other4',
            'personC1id': 'other5',
            'personC2': 'other6',
            'personC2id': 'other7',
            'personC3': 'other8',
            'personC3id': 'other9',
        }
        # Filter Main Table
        new_mainTable = {k: v for k, v in mainTable.items() if v if k not in REMOVE_LIST}
        for i in MAIN_ADD_LIST:
            if i not in new_mainTable:
                new_mainTable[i] = ""
        new_mainTable['declareTime'] = datetime.now().strftime("%Y-%m-%d")
        # Filter Second Table
        if secondTable is not None:
            new_secondTable = {k: v for k, v in secondTable.items() if v if k not in REMOVE_LIST}
        elif mainTable['currentArea'] == "1":
            new_secondTable = {v: mainTable[k] for k, v in MAIN_TO_SECOND.items() if mainTable[k]}
        else:
            new_secondTable = secondTable
        return new_mainTable, new_secondTable

    def login(self, username, password) -> None:
        if len(password) != 24:
            password = self.encrypt(password)
        api = 'user/login'
        data = {"username": username, "password": password}
        self.login_msg = self.query(api, data)
        self.idtype = self.result['data']['idtype']
        self.jnuid = self.result['data']['jnuid']
        self.jnuId = self.result['data']['jnuId']
        self.need_write = (self.result['meta']['code'] == 200)

    def stuinfo(self) -> tuple:
        api = 'user/stuinfo'
        data = {"jnuid": self.jnuid, "idType": self.idtype}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        secondTable = self.result['data']['secondTable']
        return mainTable, secondTable

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

    def review(self, id) -> tuple:
        api = 'user/review'
        data = {"jnuid": self.jnuid, "id": id}
        self.query(api, data)
        mainTable = self.result['data']['mainTable']
        secondTable = self.result['data']['secondTable']
        return mainTable, secondTable

    def write(self, mainTable, secondTable) -> str:
        api = 'write/main'
        data = {"jnuid": self.jnuid, "mainTable": mainTable}
        if secondTable is not None:
            data['secondTable'] = secondTable
        msg = self.query(api, data)
        return msg


def sc_send(text, desp='') -> None:
    postdata = {'text': text, 'desp': desp}
    post('http://sc.ftqq.com/'+SCKEY+'.send', data=postdata)


def tg_send(desp='') -> None:
    tg_api = 'https://api.telegram.org/bot'+BOTTOKEN+'/sendMessage'
    tg_data = {'chat_id': TGCHATID, 'text': desp}
    post(tg_api, data=tg_data)


def checkin(username, password) -> Optional[str]:
    try:
        stu = STUHealth(username, password)
        if not stu.need_write:
            return
        last_id = stu.stucheckin()
        last_tables = stu.review(last_id)
        tables = stu.filter_tables(*last_tables)
        msg = stu.write(*tables)
        return "打卡{}：{}".format(username, msg)
    except Exception as e:
        print('发生异常{}，详情如下：{}'.format(e, format_exc()))
        return "打卡错误{}：{}".format(username, e)


if __name__ == "__main__":
    # accounts settings
    usernames = getenv('USERNAME', '').split()
    passwords = getenv('PASSWORD', '').split()
    SCKEY = getenv('SCKEY')
    TGCHATID = getenv('TGCHATID')
    BOTTOKEN = getenv('TGTOKEN')
    # run
    print(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    push_msg = []
    for account in zip(usernames, passwords):
        print("开始打卡...")
        msg = checkin(*account)
        if msg is not None:
            push_msg.append(msg)
    if SCKEY and push_msg:
        print('发送微信推送...')
        sc_send('\n\n'.join(push_msg))
        tg_send('\n\n'.join(push_msg))

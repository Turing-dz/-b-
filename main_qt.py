import requests
import csv
import execjs
import re
import math
from PyQt5.QtWidgets import QApplication,QMainWindow,QFileDialog, QMessageBox
from PyQt5.QtCore import *
import sys
import os
#自定义类
from bili_comment import Ui_Form#导入自定义的Form
class Bili_Comment(QMainWindow):
    def __init__(self):
        super(Bili_Comment,self).__init__()
        self.ui=Ui_Form()
        self.ui.setupUi(self)
        self.url=""
        self.csv_bool=False
        self.avatar_bool=False
        self.save_path="./csv"
        self.title=""
        self.session_id=""#第一页无session_id
        self.web_location=1315875#必须是整数类型啊！！！
        self.cookies = {
            'buvid3': '6C16A34E-4B78-F350-03AA-71E6B21A703519906infoc',
            'b_nut': '1726211919',
            '_uuid': '828DDCCD-F3CD-3997-11077-1729B6881A6120884infoc',
            'enable_web_push': 'DISABLE',
            'buvid4': '3CB58DB4-B2F0-07C1-06FA-E452949C4A8942274-024082300-j2Owk+KrE1E0oCXj+7DzqA%3D%3D',
            'header_theme_version': 'CLOSE',
            'rpdid': "|(u|kkmlu~ll0J'u~kYkukl|m",
            'fingerprint': '65fbd3ec7ea1fba4aa76eb96cb7f6249',
            'buvid_fp_plain': 'undefined',
            'buvid_fp': '65fbd3ec7ea1fba4aa76eb96cb7f6249',
            'DedeUserID': '37611353',
            'DedeUserID__ckMd5': 'af2f5320e5c29dea',
            'bp_t_offset_37611353': '1020612344109072384',
            'bili_ticket': 'eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3MzY0OTQzNTgsImlhdCI6MTczNjIzNTA5OCwicGx0IjotMX0.UA_DNnfYHwmuWf3mk3zAc45Ar6QrABl70LmFhjli-ms',
            'CURRENT_FNVAL': '4048',
            'SESSDATA': 'd0b56cac%2C1752455376%2C9a0da%2A12CjAOnVM6uYDuArVzsKs0vyy35cm-VhRFHM4S5_iarXLGWicX0fecOg0Qh9tqsaryutkSVmJ0WFBtVWl0cmdGUC02VmxQNEh1NDk0bm54VzlheWd1alBXSlVPRTZ0dkExcmRsZEtzd0ZYeVNNYkh6MkF5Q3ptYzRHTjRKNnNZd3RGd0JRdlBaYVhRIIEC',
            'sid': '7lfoc3ai',#8位
            'bili_jct': 'b155c6e8ee5318259a0bc50ecf260edb',
            'bili_ticket_expires': '1736992392',  
            'b_lsid': 'ACF7894A_19468277AD7',#位
            'home_feed_column': '4',
            'browser_resolution': '1229-569',  
        }
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9',
            'cache-control': 'no-cache',
            'origin': 'https://www.bilibili.com',
            'pragma': 'no-cache',
            'priority': 'u=1, i',
            'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-site',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        }
    #1.用户输入的url，解析到视频标题和oid等信息
    def give_oid(self):
        response = requests.get(self.url, cookies=self.cookies, headers=self.headers).text
        rule_oid=re.compile(r'"aid":(\d+),')
        rule_title=re.compile(r'"title":"([^"]+)"')
        oid=re.findall(rule_oid,response)[0]
        title=re.findall(rule_title,response)[0]
        return oid, title
    #2.请求评论接口
    def download_image(self,image_url):
        try:
            response = requests.get(image_url, stream=True)
            if response.status_code == 200:
                # 检查目录是否存在，如果不存在则创建
                directory = os.path.join(self.save_path, "avatar")
                if not os.path.exists(directory):
                    os.makedirs(directory)
                with open(os.path.join(directory, image_url.split("/")[-1] + ".jpg"),  'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
        except Exception as e:
            pass
    def dict2csv(self,all_count,save_data_dict):
        with open(f"{self.save_path}/{self.title}_{all_count}.csv", "a", newline='',encoding="utf-8") as f:
            f_csv=csv.writer(f)#写入缓存
            if f.tell() == 0:  # 检查文件是否为空，如果是，则先写入表头
                headers_csv=[key for key in save_data_dict.keys()]
                f_csv.writerow(headers_csv)
            data=[value for value in save_data_dict.values()]
            f_csv.writerow(data)#写入一行
    def encode_params(self,oid):
        pagination_str = "{\"offset\":\"{\\\"type\\\":1,\\\"direction\\\":1,\\\"session_id\\\":\\\""+str(self.session_id)+"\\\",\\\"data\\\":{}}\"}" if self.session_id else '{\"offset\":\"\"}'
        params={
        "oid": oid,
        "type": 1,
        "mode": 3,
        "pagination_str": pagination_str,
        "plat": 1,
        'seek_rpid': '',
        "web_location": self.web_location
        }
        # 获取 JS 文件的路径
        if getattr(sys, 'frozen', False):  # 判断是否为打包后的应用
            js_file = os.path.join(sys._MEIPASS, 'comment_url.js')  # 打包后的路径
        else:
            js_file = 'comment_url.js'  # 未打包时的路径
        ctx=execjs.compile(open(js_file,'r',encoding='utf-8').read()).call('lt',params)
        params.update({
            'w_rid': ctx["w_rid"],
            'wts': ctx["wts"]
        })
        return params
    def handle_cursor(self,cursor):
        is_end=cursor["is_end"]#是否最后一页
        all_count=cursor["all_count"]#总评论数
        self.session_id=cursor["session_id"]
        return {"is_end":is_end,"all_count":all_count}
    def handle_content(self,list_comment,is_end,all_count):
        save_data_dict={}
        for comment in list_comment:
            save_data_dict["root"]=comment["root"]
            save_data_dict["rpid"]=comment["rpid"]
            save_data_dict["rcount"]=comment["rcount"]#评论回复数
            save_data_dict["message"]=comment["content"]["message"]#评论内容
            save_data_dict["like"]=comment["like"]#点赞数
            # save_data_dict["mid"]=comment["member"]["mid"]#评论者id
            save_data_dict["avatar"]=comment["member"]["avatar"]#评论者头像
            save_data_dict["sex"]=comment["member"]["sex"]#评论者性别
            save_data_dict["uname"]=comment["member"]["uname"]#评论者昵称
            save_data_dict["oid"]=comment["oid"]#我以及我的回复者们共用id
            save_data_dict["parent"]=comment["parent"]#回复者id
            if comment["replies"]:
                replay_data=self.handle_replay(save_data_dict["oid"],save_data_dict["rpid"],save_data_dict["rcount"])
                self.handle_content(replay_data,is_end,all_count)
            if self.csv_bool:
                self.dict2csv(all_count,save_data_dict)
            if self.avatar_bool:
                self.download_image(save_data_dict["avatar"])
            self.ui.textEdit.append(save_data_dict["message"])
            self.ui.textEdit.repaint()  # 强制刷新
    def singal_url_comment(self,oid):
        while True:
            params=self.encode_params(oid)
            response = requests.get(
            'https://api.bilibili.com/x/v2/reply/wbi/main',
            cookies=self.cookies,
            headers=self.headers,
            params=params,
        )
            cursor_data=self.handle_cursor(response.json()["data"]["cursor"])
            # print(cursor_data)
            self.handle_content(response.json()["data"]["replies"],cursor_data.get("is_end"),cursor_data.get("all_count"))
            # print(f"第{count}页爬完了")
            # count+=1
            if cursor_data.get("is_end")==True:
                page=cursor_data.get("all_count")
                # print(f"爬取完成,一共有{page}条")
                break
        return page,cursor_data.get("all_count",0)
    #3.请求回复接口
    def handle_replay(self,oid,rpid,rcount):
        out=[]
        count = math.ceil(rcount / 10)
        for i in range(count):
            params = {
                'oid': oid,
                'type': '1',
                'root': rpid,
                'ps': '10',
                'pn': str(i+1),
                'web_location': '333.788',
            }
            response = requests.get('https://api.bilibili.com/x/v2/reply/reply', params=params, cookies=self.cookies, headers=self.headers)
            out.extend(response.json().get("data").get("replies"))
        return out
    #qt操作
    def save_local_dir(self):
        # 打开文件选择对话框，让用户选择目录
        directory = QFileDialog.getExistingDirectory(self, "选择保存目录", "")
        if directory:  # 如果用户选择了目录
            self.ui.lineEdit_2.setText(directory)
    def start(self):
        self.url=self.ui.lineEdit.text()
        self.csv_bool=self.ui.radioButton.isChecked()
        self.avatar_bool=self.ui.radioButton_2.isChecked()
        self.save_path=self.ui.lineEdit_2.text()
        oid, self.title=self.give_oid()
        page,comment_count=self.singal_url_comment(oid)
        if page:
            msg = QMessageBox()
            msg.setWindowTitle("信息")
            msg.setText(f"爬取完成，一共{comment_count}条评论")
            msg.setIcon(QMessageBox.Information)
            msg.exec_()  

if __name__=="__main__":
    # bi=Bili_Comment()
    # oid, title=bi.give_oid()#1.拿到视频的oid和title
    # bi.singal_url_comment(oid)
    app=QApplication(sys.argv)
    win=Bili_Comment()
    win.show()#显示Form
    sys.exit(app.exec_())



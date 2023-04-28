#coding=utf-8
# import sys
# sys.path.append("/Users/ethan/whatsapp-py")

import tornado.web
import tornado.ioloop
import tornado.httpserver
import tornado.options
from tornado.options import options, define
from tornado.web import url, RequestHandler
import re
from tornado import gen
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor
import time
import datetime
from login.cli import CliStack

from login.register import *
from config.v1.config import Config
import os

define("port", default=8001, type=int, help="run server on the given port.")

class mobileField():
    REGULAR = "^([1-9]+\\d*)"

    def __init__(self, error_dict=None, required=True):
        self.error_dict = {}
        if error_dict:
            self.error_dict.update(error_dict)
        self.required = required
        self.error = None
        self.is_valid = False
        self.value = None

    def validate(self, name, input_value):
        if not self.required:
            # 如果输入的值可以为空，
            self.is_valid = True
            self.value = input_value

        else:
            # 如果要求输入的值不能为空
            if not input_value.strip():
                # 如果我输入的值是空值，然后我就去取error_dict里面required对应的值
                if self.error_dict.get("required", None):
                    self.error = self.error_dict["required"]
                else:
                    # 否则，默认把required赋值到self.error
                    self.error = "%s is required" % name
            else:
                # 如果我输入的值不是空值，那么我就要和正则表达式进行比较
                ret = re.match(mobileField.REGULAR, input_value)
                if ret:
                    self.is_valid = True
                    # self.value = ret.group()
                    self.value = input_value
                else:
                    if self.error_dict.get("valid", None):
                        self.error = self.error_dict["valid"]
                    else:
                        self.error = "%s is invalid" % name

class BaseForm(object):
    def check_valid(self, handle):
        flag = True
        error_message_dict = {}
        success_value_dict = {}

        for key, regular in self.__dict__.items():
            input_value = handle.get_argument(key, default="")
            regular.validate(key, input_value)
            if regular.is_valid:
                success_value_dict[key] = regular.value
            else:
                error_message_dict[key] = regular.error
                flag = False
        return flag, success_value_dict, error_message_dict

class MainForm(BaseForm):
    def __init__(self):
        self.mobile = mobileField(required=False, error_dict={"required": "手机号", "valid": "格式错误"})
        self.countryCode = mobileField(required=False, error_dict={"required": "国家码", "valid": "格式错误"})
        self.ipAgent = mobileField(required=False, error_dict={"valid": "格式错误"})
        self.ipAgentName = mobileField(required=False, error_dict={"valid": "格式错误"})
        self.ipAgentPassword = mobileField(required=False, error_dict={"valid": "格式错误"})

        self.SMSCode = mobileField(required=False, error_dict={"valid": "格式错误"})

        self.toMobile = mobileField(required=False, error_dict={"valid": "格式错误"})
        self.toText = mobileField(required=False, error_dict={"valid": "格式错误"})

        self.groupUrl = mobileField(required=False, error_dict={"valid": "格式错误"})


class IndexHandler(RequestHandler):
    def get(self):
        self.render("index.html")


#获取验证码
class getCodeHandler(RequestHandler):
    def initialize(self, subject):
        self.subject = subject

    def get(self):
        obj = MainForm()
        is_valid, success_dict, error_dict = obj.check_valid(self)
        if is_valid:
            print("success", success_dict)
            resu = {'code': 200, 'message': '成功'}

            config = Config()

            config.phone = success_dict['mobile']
            config.cc = success_dict['countryCode']
            config.sim_mcc = search_mcc(config.cc)
            config.sim_mnc = "01"
            p_in = str(config.phone)[len(str(config.cc)):]

            profile = Profile(config.phone)
            if profile.config is None:
                config.pushname = "steatt"

            if not profile.config or not profile.config.edge_routing_info:
                r = register(config)
                result = r.handleRequestCode(method="sms", config=r._config)
                self.write(result)
            else:
                self.write({'code': 1001, 'message':'本地已有登录数据可直接登录'})

        else:
            print("error", error_dict)
            self.render("index.html", error_dict=error_dict)

class registerHandler(RequestHandler):
    executor = ThreadPoolExecutor(4)

    def initialize(self, subject):
        self.subject = subject

    @gen.coroutine
    def get(self):
        obj = MainForm()
        is_valid, success_dict, error_dict = obj.check_valid(self)
        if is_valid:
            print("success", success_dict)

            config = Config()

            config.phone = success_dict['mobile']
            config.cc = success_dict['countryCode']
            config.sim_mcc = search_mcc(config.cc)
            config.sim_mnc = "01"
            smsCode = success_dict['SMSCode']

            profile = Profile(config.phone)
            if profile.config is None:
                config.pushname = "stedgg"

            if not profile.config or not profile.config.edge_routing_info:
                r = register(profile.config)
                result = r.handleRegister(code=smsCode, config=r._config)
                self.write(result)
                #注册成功后登录
                try:
                    start = time.time()
                    # 并行执行
                    result1, result2 = yield gen.with_timeout(datetime.timedelta(seconds=300),
                                                              [self.login(config.phone), self.doing()],
                                                              quiet_exceptions=tornado.gen.TimeoutError)
                    print(result1, result2)
                    print(time.time() - start)
                except gen.TimeoutError:
                    print("Timeout")

            else:
                self.write({'code': 1001, 'message': '本地已有登录数据可直接登录'})
                #注册成功后登录
                try:
                    start = time.time()
                    # 并行执行
                    result1, result2 = yield gen.with_timeout(datetime.timedelta(seconds=300),
                                                              [self.login(config.phone), self.doing()],
                                                              quiet_exceptions=tornado.gen.TimeoutError)
                    print(result1, result2)
                    print(time.time() - start)
                except gen.TimeoutError:
                    print("Timeout")

        else:
            print("error", error_dict)
            self.render("index.html", error_dict=error_dict)

    @run_on_executor
    def login(self, mobile):
        profile = Profile(mobile)
        stack = CliStack(profile)
        stack.connect()
        return {'code': 0, 'message': '完成注册登录'}

    @run_on_executor
    def doing(self):
        return "2"

class messageHandler(RequestHandler):
    executor = ThreadPoolExecutor(4)

    @gen.coroutine
    def get(self):
        obj = MainForm()
        is_valid, success_dict, error_dict = obj.check_valid(self)
        if is_valid:
            profile = Profile(success_dict['mobile'])
            if profile.config and profile.config.edge_routing_info:
                try:
                    start = time.time()
                    result = yield gen.with_timeout(datetime.timedelta(seconds=300),
                                                              [self.sendMessage(profile.config.phone, success_dict['toMobile'], success_dict['toText'])],
                                                              quiet_exceptions=tornado.gen.TimeoutError)
                    self.write(result[0])
                    print(time.time() - start)
                except gen.TimeoutError:
                    print("Timeout")

            else:
                self.write({'code': 1002, 'message': '登录数据已失效请重新登录'})

        else:
            print("error", error_dict)
            self.render("index.html", error_dict=error_dict)

    @run_on_executor
    def sendMessage(self, mobile, to, text):
        profile = Profile(mobile)
        stack = CliStack(profile)
        stack.sendMessages(to, text)
        return {'code': 0, 'message': '发送完成'}

class GroupJoin(RequestHandler):
    executor = ThreadPoolExecutor(4)

    @gen.coroutine
    def get(self):
        obj = MainForm()
        is_valid, success_dict, error_dict = obj.check_valid(self)
        if is_valid:
            groupUrl = success_dict['groupUrl']
            profile = Profile('6281995412652')

            if profile.config and profile.config.edge_routing_info:
                try:
                    start = time.time()
                    result = yield gen.with_timeout(datetime.timedelta(seconds=300),
                                                              [self.groupJoinUrl(profile.config.phone, groupUrl)],
                                                              quiet_exceptions=tornado.gen.TimeoutError)
                    self.write(result[0])
                    print(time.time() - start)
                except gen.TimeoutError:
                    print("Timeout")

            else:
                self.write({'code': 1002, 'message': '登录数据已失效请重新登录'})

        else:
            print("error", error_dict)
            self.render("index.html", error_dict=error_dict)

    @run_on_executor
    def groupJoinUrl(self, mobile, groupUrl):
        profile = Profile(mobile)
        stack = CliStack(profile)
        stack.groupInfoList(groupUrl)

        return {'code': 0, 'message': '完成注册登录'}

import pandas as pd
def search_mcc(countryCode='86'):
    df = pd.read_csv(os.path.abspath('.') + '/countries.tsv', header=None, encoding='utf-8', delimiter='\t', skiprows=1)
    line = df[df[2] == int(countryCode)]
    countryCode = line[3]
    mcc = "460"
    for i, v in countryCode.items():
        mcc = v
        break
    print ("mcc = " + mcc)
    return mcc.split(",")[0]

class Test(RequestHandler):

    @gen.coroutine
    def get(self):
        print(self.get_argument("tag"), self.get_argument("time"))
        self.finish({"tag":self.get_argument("tag"),'time': self.get_argument("time")})


# /api/WhatsAppProtocol/SendSMSCode
if __name__ == "__main__":
    tornado.options.parse_command_line()
    app = tornado.web.Application([
        (r"/", IndexHandler),
        (r"/api/WhatsAppProtocol/SendSMSCode", getCodeHandler, {"subject": "success"}),
        (r"/api/WhatsAppProtocol/Register", registerHandler, {"subject": "success"}),
        (r"/api/WhatsAppProtocol/SendText", messageHandler),
        (r"/api/WhatsAppProtocol/GroupJoin", GroupJoin),
        (r"/api/test", Test),

    ],
        debug=False)

    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

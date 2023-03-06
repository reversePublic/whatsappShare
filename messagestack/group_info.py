import datetime

from common.singleonConfig import SingleonConfig
from config.enumExec import ExecTypes
from mycli.cli.exportgroup import ExportGroupUpload
from mycli.http_request import requests_send
from mycli.mysql.mysql_cli import mobile_update

class ExportGroupResult():

    @classmethod
    def fail(cls, result, type_num):

        mobile = result.get("phone")
        reason = result.get("reason")
        data = result.get("data")

        dataPenetrate = SingleonConfig().getParamsAction()
        upload_url = dataPenetrate.get("UploadUrl")
        work_upload_url = dataPenetrate.get("WorkUploadUrl")

        upload_data = {
            "FullPhoneNumber": mobile,
            "OptType": None,
            "OptAppType": 2,
            "OptTime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "OptIp": "",
            "OptReamrk": None,
            "ProtocolType": 1
        }
        if type_num == ExecTypes.login:

            if reason == 403:
                mobile_update(mobile, reason)
                upload_data["OptType"] = 5
                message = "封号"
                upload_data["OptReamrk"] = message
            else:
                upload_data["OptType"] = 2
                message = "登录失败"
                upload_data["OptReamrk"] = message
            ExportGroupUpload.send_http("POST", work_upload_url, upload_data, mobile, message)

        elif type_num == ExecTypes.group_join:

            group_link = data.get("GroupUrl")
            data["groupUser"] = []

            upload_data["OptType"] = 7
            message = "加群[{}]失败".format(group_link)
            upload_data["OptReamrk"] = message
            upload_response = requests_send("POST", upload_url, json=data)
            if not upload_response:
                requests_send("POST", upload_url, json=upload_data)

            ExportGroupUpload.send_http("POST", work_upload_url, upload_data, mobile, message)

        elif type_num == ExecTypes.group_info:

            group_link = data.get("GroupUrl")
            data["groupUser"] = []

            upload_data["OptType"] = 7
            message = "导群[{}]失败".format(group_link)
            upload_data["OptReamrk"] = message
            upload_response = requests_send("POST", upload_url, json=data)
            if not upload_response:
                requests_send("POST", upload_url, json=upload_data)

            ExportGroupUpload.send_http("POST", work_upload_url, upload_data, mobile, message)

    @classmethod
    def success(cls, result, type_num):
        data = result.get("data")
        mobile = result.get("phone")

        dataPenetrate = SingleonConfig().getParamsAction()
        upload_url = dataPenetrate.get("UploadUrl")
        work_upload_url = dataPenetrate.get("WorkUploadUrl")

        upload_data = {
            "FullPhoneNumber": mobile,
            "OptType": None,
            "OptAppType": 2,
            "OptTime": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f"),
            "OptIp": "",
            "OptReamrk": None,
            "ProtocolType": 1
        }
        if type_num == ExecTypes.login:

            upload_data["OptType"] = 1
            message = "登录成功"
            upload_data["OptReamrk"] = message
            ExportGroupUpload.send_http("POST", work_upload_url, upload_data, mobile, message)

        elif type_num == ExecTypes.group_join:
            print("导群加群成功")

        elif type_num == ExecTypes.group_info:

            group_link = data.get("GroupUrl")

            upload_data["OptType"] = 6
            message = "导群[{}]成功".format(group_link)
            upload_data["OptReamrk"] = message

            upload_response = requests_send("POST", upload_url, json=data)
            if not upload_response:
                requests_send("POST", upload_url, json=upload_data)

            ExportGroupUpload.send_http("POST", work_upload_url, upload_data, mobile, message)


from common.singleonConfig import SingleonConfig
from config.enumExec import ExecTypes
from mycli.cli.playgroup import PlayGroupHandle
from mycli.logger import logger
from mycli.mysql.mysql_cli import mobile_update

class PlayGroupResult():

    @classmethod
    def fail(cls, result, type_num):
        if type_num == ExecTypes.login:
            reason = result.get("reason")
            mobile = result.get("phone")

            if reason == 403:  # 封号
                mobile_update(mobile, reason)

            queue = result.pop('queue')
            result["type_num"] = type_num
            queue.put(result)

        elif type_num == ExecTypes.group_join:
            queue = result.pop('queue')
            result["type_num"] = type_num
            queue.put(result)
        elif type_num == ExecTypes.send_text:
            queue = result.pop('queue')
            result["type_num"] = type_num
            queue.put(result)

    @classmethod
    def success(cls, result, type_num):
        if type_num == ExecTypes.group_kick:
            return
        phone = result.get("phone")
        data = result.get("data")

        dataPenetrate = SingleonConfig().getParamsAction()
        upload_url = dataPenetrate.get("PlayGroupUploadUrl")

        if type_num == ExecTypes.login:
            logger.info("{}:炒群号码登录成功".format(phone))
        elif type_num == ExecTypes.group_join:
            dataPenetrate[phone] = type_num
            SingleonConfig().setParamsAction(dataPenetrate)
            PlayGroupHandle.upload(data, "AddGroup", upload_url, "AddGroupSuccessed", phone)
        elif type_num == ExecTypes.send_text:
            PlayGroupHandle.upload(data, "SendMessage", upload_url, "SendMessageSuccessed", phone)

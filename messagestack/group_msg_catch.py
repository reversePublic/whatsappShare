from config.enumExec import ExecTypes
from mycli.cli.playgroup import logger
from mycli.mysql.group_msg_catch import group_msg_insert, busy_update
from mycli.mysql.mysql_cli import mobile_update


class GroupMessageCatchResult():

    @classmethod
    def fail(cls, result, type_num):

        phone = result.get("phone")
        reason = result.get("reason")

        if type_num == ExecTypes.login:
            if reason == 403:
                mobile_update(phone, reason)
            logger.info("{}:群消息抓取号码登录失败:{}".format(phone, reason))

    @classmethod
    def success(cls, result, type_num):

        phone = result.get("phone")
        data = result.get("data")

        if type_num == ExecTypes.login:
            busy_update(phone, 1)
            logger.info("{}:群消息抓取号码登录成功".format(phone))
        elif type_num == ExecTypes.receive_text:
            group_id = data.get("groupId")
            if group_id:
                message = data.get("text")
                message_id = data.get("messageId")
                group_msg_insert(phone, group_id, message, message_id)
                logger.info("{}:群消息入库成功:{}".format(phone, data))

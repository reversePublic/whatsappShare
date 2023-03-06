from common.singleonConfig import SingleonConfig
from config.enumExec import ExecTypes
from mycli.cli.register_result import ResultMq
from mycli.mysql.mysql_cli import mobile_insert

class RegisterResult():

    @classmethod
    def fail(cls, result, type_num):

        if type_num == ExecTypes.login:
            mobile = result.get("phone")
            reason = result.get("reason")

            dataPenetrate = SingleonConfig().getParamsAction()
            is_mq = dataPenetrate.get("is_mq")
            RabbitMq = dataPenetrate.get("RabbitMq")
            master_id = dataPenetrate.get("master_id")
            message = "{}:注册登录失败,{}".format(mobile, reason)
            ResultMq.send_mq(master_id, message, is_mq, mq_config=RabbitMq)

            dataPenetrate["login"] = True
            dataPenetrate["fail"] = True
            SingleonConfig().setGroupControlAction(dataPenetrate)

    @classmethod
    def success(cls, result, type_num):

        if type_num == ExecTypes.login:
            data = result.get("data")
            mobile = result.get("phone")

            dataPenetrate = SingleonConfig().getParamsAction()
            action = dataPenetrate.get("action")
            RabbitMq = dataPenetrate.get("RabbitMq")
            is_mq = dataPenetrate.get("is_mq")
            master_id = dataPenetrate.get("master_id")

            if data.get("isFirst"):
                cc = data.get("cc")
                ca = data.get("country")
                mobile_insert(mobile, cc, ca, action, master_id)
                message = "{}:注册登录成功".format(mobile)
                ResultMq.send_mq(master_id, message, is_mq, mq_config=RabbitMq)

            dataPenetrate["login"] = True
            dataPenetrate["success"] = True
            SingleonConfig().setGroupControlAction(dataPenetrate)


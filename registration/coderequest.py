from common.http.warequest import WARequest
from common.http.waresponseparser import JSONResponseParser
from common.tools import WATools
from registration.existsrequest import WAExistsRequest
from registration.clientLogRequest import WAClientLogRequest

from env import MyEnv


class WACodeRequest(WARequest):
    def __init__(self, method, config):
        """
        :type method: str
        :param config:
        :type config: Config
        """
        super(WACodeRequest,self).__init__(config)

        self.addParam("sim_mcc", config.sim_mcc.zfill(3))
        self.addParam("sim_mnc", config.sim_mnc.zfill(3))
        self.addParam("method", method)
        self.addParam("token", MyEnv.getCurrent().getToken(self._p_in))

        self.url = "v.whatsapp.net/v2/code"

        self.pvars = ["status","reason","length", "method", "retry_after", "code", "param"] +\
                    ["login", "type", "sms_wait", "voice_wait", "notify_after"]
        self.setParser(JSONResponseParser())

    def send(self, parser = None, encrypt=True, preview=False):
        if self._config.id is not None:
            request = WAExistsRequest(self._config)
            result = request.send(encrypt=encrypt, preview=preview)

            if result:
                if result["status"] == "ok":
                    return result
                elif result["status"] == "fail" and "reason" in result and result["reason"] == "blocked":
                    return result
        else:
            self._config.id = WATools.generateIdentity()
            self.addParam("id", self._config.id)

            request = WAExistsRequest(self._config)
            result = request.send(encrypt=encrypt, preview=preview)
            print(result)
            request1 = WAClientLogRequest(self._config)
            result1 = request1.send(encrypt=encrypt, preview=preview)
            print(result1)
            self._config.backup_token = WATools.generateBackupToken()
            self.addParam("backup_token", self._config.backup_token)


        res = super(WACodeRequest, self).send(parser, encrypt=encrypt, preview=preview)

        return res

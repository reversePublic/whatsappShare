from common.http.warequest import WARequest
from common.http.waresponseparser import JSONResponseParser
from env import MyEnv


class WAClientLogRequest(WARequest):

    def __init__(self, config):
        """
        :param config:
        :type config: Config
        """
        super(WAClientLogRequest,self).__init__(config)
        if config.id is None:
            raise ValueError("Config does not contain id")

        self.url = "v.whatsapp.net/v2/client_log"

        self.pvars = ["status", "login"]
        self.setParser(JSONResponseParser())
        self.addParam("token", MyEnv.getCurrent().getToken(self._p_in))

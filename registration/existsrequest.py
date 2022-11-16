from common.http.warequest import WARequest
from common.http.waresponseparser import JSONResponseParser
from env import MyEnv


class WAExistsRequest(WARequest):

    def __init__(self, config):
        """
        :param config:
        :type config: Config
        """
        super(WAExistsRequest,self).__init__(config)
        if config.id is None:
            raise ValueError("Config does not contain id")

        self.url = "v.whatsapp.net/v2/exist"
        #   "reason" : "incorrect",
        #   "sms_wait" : 0,
        #   "status" : "fail",
        #   "flash_type" : 0,
        #   "sms_length" : 6,
        #   "voice_length" : 6,
        #   "voice_wait" : 0,
        #   "login" : "85295640514"
        self.pvars = ["status", "reason", "sms_length", "voice_length", "result","param", "login", "type",
                      "chat_dns_domain", "edge_routing_info"
                    ]

        self.setParser(JSONResponseParser())
        self.addParam("token", MyEnv.getCurrent().getToken(self._p_in))

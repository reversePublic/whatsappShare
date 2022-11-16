from common.http.warequest import WARequest
from common.http.waresponseparser import JSONResponseParser


class WARegRequest(WARequest):

    def __init__(self, config, code):
        """
        :param config:
        :type config: Config
        :param code:
        :type code: str
        """
        super(WARegRequest,self).__init__(config)

        if config.id is None:
            raise ValueError("config.id is not set.")

        self.addParam("code", code)

        self.url = "v.whatsapp.net/v2/register"

        self.pvars = ["status", "login", "autoconf_type", "security_code_set", "type", "reason", "edge_routing_info", "chat_dns_domain"
                      "reason",]

        self.setParser(JSONResponseParser())

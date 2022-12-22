from .env_config import MyEnvConfig

# 俄罗斯
class RUEnvConfig(MyEnvConfig):
    _JINDOU = "2838"
    _CC = "7"
    _COUNTRY = "ru"
    _MCC = "250"
    _MNC = "002"
    _DURING = 20


    def getJinDou(self):
        return self.__class__._JINDOU

    def getCc(self):
        return self.__class__._CC

    def getCountry(self):
        return self.__class__._COUNTRY

    def getMcc(self):
        return self.__class__._MCC

    def getMnc(self):
        return self.__class__._MNC

    def getDuringTime(self):
        return self.__class__._DURING

    def getProxyName(self, mobile):
        return self.__class__._PROXY_NAME.format(
            country=self.getCountry(),
            session_name=mobile,
            session_time=self.getDuringTime()

        )

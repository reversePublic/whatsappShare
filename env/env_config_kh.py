from .env_config import MyEnvConfig

# 柬埔寨
class KHEnvConfig(MyEnvConfig):
    _JINDOU = "2123"
    _CC = "855"
    _COUNTRY = "kh"
    _MCC = "456"
    # 02 04 06 08 09 18
    _MNC = "02"
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

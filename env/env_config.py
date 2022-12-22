import abc
import logging
from six import with_metaclass

logger = logging.getLogger(__name__)

# 印度尼西亚
DEFAULT = "ID"


class MyEnvConfigType(abc.ABCMeta):
    def __init__(cls, name, bases, dct):
        if name != "MyEnvConfig":
            MyEnvConfig.registerEnv(cls)
        super(MyEnvConfigType, cls).__init__(name, bases, dct)


class MyEnvConfig(with_metaclass(MyEnvConfigType, object)):
    __metaclass__ = MyEnvConfigType
    _PROXY_NAME = "kkone88-zone-custom-region-{country}-session-{session_name}-sessTime-{session_time}"

    __ENVS = {}
    __CURR = None

    @classmethod
    def registerEnv(cls, envCls):
        envName = envCls.__name__.lower().replace("envconfig", "")
        cls.__ENVS[envName] = envCls
        logger.debug("registered envconfig %s => %s" % (envName, envCls))

    @classmethod
    def setEnv(cls, envName):
        if not envName in cls.__ENVS:
            raise ValueError("%s envconfig does not exist" % envName)
        logger.debug("Current env changed to %s " % envName)
        cls.__CURR = cls.__ENVS[envName]()

    @classmethod
    def getEnv(cls, envName):
        if not envName in cls.__ENVS:
            raise ValueError("%s envconfig does not exist" % envName)

        return cls.__ENVS[envName]()

    @classmethod
    def getRegisteredEnvs(cls):
        return list(cls.__ENVS.keys())

    @classmethod
    def getCurrent(cls):
        """
        :rtype: 印度尼西亚
        """
        if cls.__CURR is None:
            env = DEFAULT
            envs = cls.getRegisteredEnvs()
            if env not in envs:
                env = envs[0]
            logger.debug("EnvConfig not set, setting it to %s" % env)
            cls.setEnv(env)
        return cls.__CURR

    @abc.abstractmethod
    def getJinDou(self):
        pass

    @abc.abstractmethod
    def getCc(self):
        pass

    @abc.abstractmethod
    def getCountry(self):
        pass

    @abc.abstractmethod
    def getMcc(self):
        pass

    @abc.abstractmethod
    def getMnc(self):
        pass

    @abc.abstractmethod
    def getDuringTime(self):
        pass



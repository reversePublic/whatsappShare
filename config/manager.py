from config.v1.config import Config
from config.transforms.dict_keyval import DictKeyValTransform
from config.transforms.dict_json import DictJsonTransform
from config.v1.serialize import ConfigSerialize
from common.tools import StorageTools
import logging
import os
from mysql.execSql import *
import base64

logger = logging.getLogger(__name__)


class ConfigManager(object):
    NAME_FILE_CONFIG = "config"

    TYPE_KEYVAL = 1
    TYPE_JSON = 2

    TYPE_NAMES = {
        TYPE_KEYVAL: "keyval",
        TYPE_JSON: "json"
    }

    MAP_EXT = {
        "yo": TYPE_KEYVAL,
        "json": TYPE_JSON,
    }

    TYPES = {
        TYPE_KEYVAL: DictKeyValTransform,
        TYPE_JSON: DictJsonTransform
    }

    def load(self, path_or_profile_name, profile_only=False, fromNet=False):
        # type: (str, bool) -> Config
        """
        Will first try to interpret path_or_profile_name as direct path to a config file and load from there. If
        this fails will interpret it as profile name and load from profile dir.
        :param path_or_profile_name:
        :param profile_only
        :return Config instance, or None if no config could be found
        """
        logger.debug("load(path_or_profile_name=%s, profile_only=%s)" % (path_or_profile_name, profile_only))

        exhausted = []
        if not profile_only:
            if fromNet:
                mobile = path_or_profile_name
                sql = "SELECT config FROM phone_conf WHERE id={m_value}".format(m_value=mobile)
                execSql = ExecuteSQL(MYSQL_NAME)
                results = execSql.fetch_sql(sql)
                execSql.db_close()

                if len(results):
                    r = results[0]
                    config = str(r[0])
                    data = str(base64.b64decode(config), "utf-8")
                    datadict = self.TYPES[2]().reverse(data)

                    config = self.load_data(datadict)
                else:
                    print(mobile + "：mysql config为空!")
                    config = self._load_path(path_or_profile_name)

            else:
                config = self._load_path(path_or_profile_name)
        else:
            config = None
        if config is not None:
            return config
        else:
            logger.debug("path_or_profile_name is not a path, using it as profile name")
            if not profile_only:
                exhausted.append(path_or_profile_name)
            profile_name = path_or_profile_name
            config_dir = StorageTools.getStorageForProfile(profile_name)
            logger.debug("Detecting config for profile=%s, dir=%s" % (profile_name, config_dir))
            for ftype in self.MAP_EXT:
                if len(ftype):
                    fname = (self.NAME_FILE_CONFIG + "." + ftype)
                else:
                    fname = self.NAME_FILE_CONFIG

                fpath = os.path.join(config_dir, fname)
                logger.debug("Trying %s" % fpath)
                if os.path.isfile(fpath):
                    return self._load_path(fpath)

                exhausted.append(fpath)

            logger.error("Could not find a config for profile=%s, paths checked: %s" % (profile_name, ":".join(exhausted)))

    def _type_to_str(self, type):
        """
        :param type:
        :type type: int
        :return:
        :rtype:
        """
        for key, val in self.TYPE_NAMES.items():
            if key == type:
                return val

    def _load_path(self, path):
        """
        :param path:
        :type path:
        :return:
        :rtype:
        """
        logger.debug("_load_path(path=%s)" % path)
        if os.path.isfile(path):
            configtype = self.guess_type(path)
            logger.debug("Detected config type: %s" % self._type_to_str(configtype))
            if configtype in self.TYPES:
                logger.debug("Opening config for reading")
                with open(path, 'r') as f:
                    data = f.read()
                datadict = self.TYPES[configtype]().reverse(data)
                return self.load_data(datadict)
            else:
                raise ValueError("Unsupported config type")
        else:
            logger.debug("_load_path couldn't find the path: %s" % path)


    def load_data(self, datadict):
        logger.debug("Loading config")
        return ConfigSerialize(Config).deserialize(datadict)

    def guess_type(self, config_path):
        dissected = os.path.splitext(config_path)
        if len(dissected) > 1:
            ext = dissected[1][1:].lower()
            config_type = self.MAP_EXT[ext] if ext in self.MAP_EXT else None
        else:
            config_type = None

        if config_type is not None:
            return config_type
        else:
            logger.debug("Trying auto detect config type by parsing")
            with open(config_path, 'r') as f:
                data = f.read()
            for config_type, transform in self.TYPES.items():
                config_type_str = self.TYPE_NAMES[config_type]
                try:
                    logger.debug("Trying to parse as %s" % config_type_str)
                    if transform().reverse(data):
                        logger.debug("Successfully detected %s as config type for %s" % (config_type_str, config_path))
                        return config_type
                except Exception as ex:
                    logger.debug("%s was not parseable as %s, reason: %s" % (config_path, config_type_str, ex))

    def get_str_transform(self, serialize_type):
        if serialize_type in self.TYPES:
            return self.TYPES[serialize_type]()

    def config_to_str(self, config, serialize_type=TYPE_JSON):
        transform = self.get_str_transform(serialize_type)
        if transform is not None:
            return transform.transform(ConfigSerialize(config.__class__).serialize(config))

        raise ValueError("unrecognized serialize_type=%d" % serialize_type)

    def save(self, profile_name, config, serialize_type=TYPE_JSON, dest=None):
        outputdata = self.config_to_str(config, serialize_type)

        if dest is None:
            StorageTools.writeProfileConfig(profile_name, outputdata)
        else:
            with open(dest, 'wb') as outputfile:
                outputfile.write(outputdata)

    def uploadData(self, phone):
        config = self.load(phone)
        outputdata = self.config_to_str(config)

        configData = str(base64.b64encode(outputdata.encode("utf-8")), "utf-8")
        import time
        localTime = time.localtime(time.time())
        strTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
        execSql = ExecuteSQL()
        actionValue = (phone, strTime, configData)
        sqlInsert = "INSERT INTO wa_users_data (phone, time, config) VALUES {values} ON DUPLICATE KEY UPDATE config='{c_value}'".format(
            values=actionValue, c_value=configData)
        execSql.execute_sql(sqlInsert)
        execSql.db_close()

    def downloadData(self, phone):
        sql = "SELECT config FROM wa_users_data WHERE phone={m_value}".format(m_value=phone)
        execSql = ExecuteSQL()
        results = execSql.fetch_sql(sql)
        execSql.db_close()

        if len(results):
            r = results[0]
            config = str(r[0])
            data = str(base64.b64decode(config), "utf-8")
            datadict = self.TYPES[2]().reverse(data)

            config = self.load_data(datadict)
            self.save(phone, config)
            return config
        else:
            return None
    # {
    #     "__version__": 1,
    #     "cc": "62",
    #     "client_static_keypair": "qFrn5lw9208ixtrqeH4Ll91UBeuyk/1wJjc8nFHR+ExDqy/1UsUUUAaEO0c4B86Vr68uFjbTO/enrJyWPIl3Bw==",
    #     "country": "id",
    #     "edge_routing_info": "CAIIDQ==",
    #     "expid": "nYEJmaIQSmyg7A/hnDlvmw==",
    #     "fdid": "a5bc7fbc-4f55-4c1e-b95b-c7b8ffee9893",
    #     "id": "b2O9CbIxNK9cSEXU0js/gVXvnlc=",
    #     "login": "6283182456634",
    #     "phone": "6283182456634",
    #     "pushname": "Fterri Mremington",
    #     "server_static_public": "xDn6MqBPn3O6ptDhPQt/tqcXrv2dK7aR//NQLFIVal0=",
    #     "sim_mcc": "510",
    #     "sim_mnc": "001"
    # }
    def saveLoginData(self, phone, datadict, loginData):
        config = self.load_data(datadict)
        outputdata = self.config_to_str(config)

        configData = str(base64.b64encode(outputdata.encode("utf-8")), "utf-8")
        import time
        localTime = time.localtime(time.time())
        strTime = time.strftime("%Y-%m-%d %H:%M:%S", localTime)
        import json
        jsonData=json.dumps(loginData)
        actionValue = (phone, strTime, configData, datadict['env_name'], jsonData)


        execSql = ExecuteSQL()
        sqlInsert = "INSERT INTO wa_users_data (phone, time, config, env, data) VALUES {values} ON DUPLICATE KEY UPDATE config='{c_value}', time='{time}', data='{data}'".format(
            values=actionValue, c_value=configData, time=strTime, data=jsonData)
        execSql.execute_sql(sqlInsert)

        deviceInfo = SingleonConfig()

        values = (deviceInfo.deviceId, deviceInfo.versionId, loginData['phone'], loginData['nickName'], loginData['cc'], loginData['country'], strTime, strTime, "")
        sql = "INSERT INTO wa_users (device_id, version_id, phone, name, cc, country, rtime, utime, exec) VALUES {values}".format(values=values)
        execSql.execute_sql(sql)
        execSql.db_close()

        self.save(phone, config)
        return config

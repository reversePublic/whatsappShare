from config.base.transform import ConfigTransform


class ConfigDictTransform(ConfigTransform):
    def __init__(self, cls):
        self._cls = cls

    def transform(self, config):
        """
        :param config:
        :type config: dict
        :return:
        :rtype: Config
        """
        out = {}
        for prop in vars(config):
            out[prop] = getattr(config, prop)
        return out

    def reverse(self, data):
        """
        :param data:
        :type data: config.config.Config
        :return:
        :rtype: dict
        """
        return self._cls(**data)

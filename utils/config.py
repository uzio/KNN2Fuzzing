# coding=utf-8
import ConfigParser

class ICSConfig:
    """
    封装了ConfigParser，配置文件在根目录下的ics.ini, 默认使用DEFAULT这个section
    """
    def __init__(self, config_path, section='DEFAULT'):
        """
        :param config_path: ics.ini的路径
        :param section: 表示哪一个章节，默认使用DEFAULT
        """
        self._config_path = config_path
        self._conf = ConfigParser.ConfigParser()
        self._conf.read(config_path)
        self._section = section

    def save(self):
        with open(self._config_path, 'w') as fp:
            self._conf.write(fp)

    def __getitem__(self, item):
        return self._conf.get(self._section, item)

    def __setitem__(self, key, value):
        self._conf.set(self._section, key, value)

    def dict(self):
        return dict(self._conf.items(self._section))


# if __name__ == '__main__':
#     import os
#     ROOT_PATH = os.path.join(os.getcwd(), '..')
#     CONFIG_PATH = os.path.join(ROOT_PATH, 'ics.ini')
#     config = ICSConfig(CONFIG_PATH)
#     print(config['mongo'])
#     config['mongo'] = '123'
#     config.save()
#     print(config.dict())

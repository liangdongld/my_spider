"""
Author: liangdong09
Date: 2022-05-09 10:45:39
LastEditTime: 2022-05-10 15:12:02
LastEditors: liangdong09
Description: 
FilePath: /my_good_coder/core/config_load.py
"""


import logging
import configparser
import os

class ConfigLoad(object):
    """
    配置文件加载工具类
    """

    def __init__(self, conf_file_path):
        self.conf_file_path = conf_file_path
        self.logger = logging.getLogger(__name__)

    def config_load(self, section, option):
        """
        根据section和option读取配置文件的配置项值
        :param section: 配置文件中的区块(section)名
        :param option: 配置项的名称
        :return: 配置项的值，字符串
        :raises: Exception
        """
        # 判断配置文件是否存在
        if not os.path.exists(self.conf_file_path):
            self.logger.fatal("未找到config文件, 路径: %s" % self.conf_file_path)
            raise Exception('conf_file_path is not exist!')
        config_parser = configparser.ConfigParser()
        # 配置文件可能会有中文
        config_parser.read(self.conf_file_path)
        try:
            value = config_parser.get(section, option)
        except Exception as e:
            self.logger.fatal("读取config出错. section = %s, option = %s , 出错原因:%s" % (
                section, option, str(e)))
            return None
        return value

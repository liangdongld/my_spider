#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Author: liangdong09
Date: 2022-05-07 15:32:00
LastEditTime: 2022-05-10 21:37:50
LastEditors: liangdong09
Description: mini_spider启动主程序
FilePath: /mini_spidier/mini_spider.py
"""
import argparse

import logging
import logging.config
import os

from core import config_load
from core import spider_executor

SPIDER_CONF = './conf/spider.conf'
APP_CONF = './conf/application.conf'
LOG_CONF = './conf/log.conf'
LOG_DIR = './logs/'


def init_spider():
    """ 
    description: 初始化命令行传入参数提示,并对用户指定的参数进行运行
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--conf", '-c', help="mini_spider的conf配置路径")
    parser.add_argument("--version", '-v', help="显示版本信息", action='store_true')
    args = parser.parse_args()
    if args.version:
        get_version()
    elif args.conf:
        run_spider(args.conf)


def init_log():
    """
    description: 初始化log
    """
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    logging.config.fileConfig(LOG_CONF)
    logger = logging.getLogger('mini_spider')
    logger.debug("初始化log成功")


def get_version():
    """
    description: 获取版本信息
    """
    app_config = config_load.ConfigLoad(APP_CONF)
    version = app_config.config_load('application', 'version')
    print(version)


def run_spider(conf_path):
    executor = spider_executor.SpiderExecutor(conf_path)
    executor.start_executor()


def main():
    # 首先初始化log
    init_log()
    # 然后对spider进行初始化
    init_spider()


if __name__ == "__main__":
    main()

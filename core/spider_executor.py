"""
Author: liangdong09
Date: 2022-05-09 21:43:13
LastEditTime: 2022-05-10 21:06:22
LastEditors: liangdong09
Description: 
FilePath: /my_good_coder/core/spider_executor.py
"""
import logging
import os
import time

from core import config_load
from core import spider_task
from core import url_queue
from core import url_crawl


class SpiderExecutor(object):

    def __init__(self, conf_path) -> None:
        self.__thread_list = []
        self.__cur_deep = 0
        self.__conf_path = conf_path
        self.__logger = logging.getLogger(__name__)

        """ 以下参数为从配置文件读取 """
        self.__url_list = []
        self.__max_depth = None
        self.__crawl_interval = None
        self.__thread_count = None

        # 读取conf文件
        self.__read_from_conf()
        spider_task.SpiderTask.set_interval(self.__crawl_interval)
        self.__url_queue = url_queue.UrlQueue()
        print(self.__url_queue)
        # 添加url
        self.__url_queue.append_url(self.__url_list)
        self.__url_queue.goto_next_depth()

    def __read_from_conf(self):
        conf = config_load.ConfigLoad(self.__conf_path)
        self.__thread_count = int(conf.config_load('spider', 'thread_count'))
        self.__max_depth = int(conf.config_load('spider', 'max_depth'))
        self.__crawl_interval = int(
            conf.config_load('spider', 'crawl_interval'))
        url_list = conf.config_load('spider', 'url_list_file')
        self.__url_list = self.__read_from_url(url_list)
        url_crawl.UrlCrawl.read_from_conf(self.__conf_path)

    def __read_from_url(self, file_path):
        """
        description: 从url文件中读取url
        param file_path: url文件路径
        return 读取到的url_list
        """
        ret_list = list()
        if not os.path.exists(file_path):
            raise Exception("can not find url file, path: %s" % file_path)
        with open(file_path) as f:
            for line in f.readlines():
                line = line.strip()
                ret_list.append(line)
        return ret_list

    def start_executor(self):
        while self.__cur_deep <= self.__max_depth and not self.__url_queue.cur_queue.empty():
            self.__logger.info("当前深度：%s ,  当前队列长度为： %s, 开始抓取." % (
                self.__cur_deep, self.__url_queue.cur_queue.qsize()))
            self.__thread_list = []
            start_time = time.time()
            for i in range(0, self.__thread_count):
                cur_thread = spider_task.SpiderTask(
                    thread_name='spider_' + str(i))
                cur_thread.setDaemon(True)
                cur_thread.start()
                self.__thread_list.append(cur_thread)
            for th in self.__thread_list:
                th.join()
            end_time = time.time()
            self.__logger.info("深度 %s 抓取完毕,共耗时 %s ms" %
                               (self.__cur_deep, int(end_time - start_time) * 1000))
            self.__url_queue.goto_next_depth()
            # 深度自增1
            self.__cur_deep += 1

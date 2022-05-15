"""
Author: liangdong09
Date: 2022-05-10 10:20:11
LastEditTime: 2022-05-10 21:14:53
LastEditors: liangdong09
Description: 
FilePath: /my_good_coder/core/spider_task.py
"""

import threading
import logging
import time

from core import url_queue
from core import url_crawl


class SpiderTask(threading.Thread):
    """爬虫任务执行类"""
    __crawl_interval = None

    def __init__(self, thread_name):
        # 线程初始化，设置线程名
        threading.Thread.__init__(self, name=thread_name)
        self.__logger = logging.getLogger(__name__)

    @classmethod
    def set_interval(cls, crawl_interval):
        """
        description: 类函数，用于设置爬虫间隔时间
        param crawl_interval: 爬虫间隔时间
        return {*}
        """
        cls.__crawl_interval = crawl_interval

    def run(self):
        while True:
            if url_queue.UrlQueue().cur_queue.empty():
                break
            url = url_queue.UrlQueue().cur_queue.get()
            # 抓取url
            self.__logger.debug("start crawl, url = %s" % url)
            try:
                url_crawl.UrlCrawl().crawl_url(url)
                self.__logger.debug("finished crawl, url = %s" % url)
            except Exception as e:
                self.__logger.error("url = %s, 出现错误: %s" % (url, str(e)))
            time.sleep(SpiderTask.__crawl_interval)

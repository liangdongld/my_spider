"""
Author: liangdong09
Date: 2022-05-09 20:58:01
LastEditTime: 2022-05-10 20:59:43
LastEditors: liangdong09
Description: 
FilePath: /my_good_coder/core/url_queue.py
"""
import queue
import threading


def singleton(cls, *args, **kwargs):
    instances = {}

    def _singleton():
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton


@singleton
class UrlQueue(object):
    """
    单例模式
    """

    def __init__(self):
        self.cur_queue = None
        self.__next_queue = queue.Queue()
        self.__url_requested = list()
        self.__lock = threading.Lock()

    def append_url(self, urls=None):
        """
        description: 向下层队列增加url
        param urls: 要增加的url
        return {*}
        """
        if urls is None:
            return
        # 加锁，确保线程独占临界资源
        with self.__lock:
            for url in urls:
                # 如果待添加的url不在
                if url in self.__url_requested:
                    continue
                self.__next_queue.put(url)
                # 将url添加到已访问的列表中
                self.__url_requested.append(url)

    def goto_next_depth(self):
        """
        description: 在遍历下一层时，调用此方法。
        """
        self.cur_queue = self.__next_queue
        self.__next_queue = queue.Queue()

"""
Author: liangdong09
Date: 2022-05-10 10:52:49
LastEditTime: 2022-05-10 16:45:33
LastEditors: liangdong09
Description: 处理url, 包括抓取下一层的url和保存资源
FilePath: /my_good_coder/core/url_crawl.py
"""
from core.config_load import ConfigLoad
from core.url_queue import UrlQueue

import requests
import logging
import urllib.parse
import re
import bs4
import os


SPIDER_SECTION = 'spider'
WEB_FILE_EXT_NAMES = ['html', 'htm', 'jsp', 'php', 'asp']

requests.packages.urllib3.disable_warnings()


class UrlCrawl(object):
    """ 抓取url的工具类 """
    __out_put_dir = None
    __target_url = None
    __crawl_timeout = None
    __logger = logging.getLogger(__name__)
    __url_queue = UrlQueue()
    __requested_resource_list = []

    @classmethod
    def read_from_conf(cls, conf_path):
        """
        description: 读取conf, 赋值给类变量
        param conf_path: conf文件路径
        return {*}
        """
        conf = ConfigLoad(conf_path)
        cls.__out_put_dir = conf.config_load(
            SPIDER_SECTION, 'output_directory')
        cls.__target_url = conf.config_load(SPIDER_SECTION, 'target_url')
        cls.__crawl_timeout = int(conf.config_load(
            SPIDER_SECTION, 'crawl_timeout'))
        if not os.path.exists(cls.__out_put_dir):
            os.mkdir(cls.__out_put_dir)

    @classmethod
    def crawl_url(cls, url):
        """
        description: 抓取url,返回子ur和静态资源列表
        param url:
        return 子url和和静态资源列表
        """
        page_text = cls.__get_page_text(url)
        if not page_text:
            cls.__logger.error("请求url出错, url = [%s]" % url)
            return
        resource_list = cls.__get_resource_list(page_text)
        sub_url_list = cls.__get_sub_urls(url, page_text)
        logging.debug("url = %s \nsub_url_list = %s \nresource_list = %s " % (
            url, sub_url_list, resource_list))
        # 保存爬到的资源
        cls.__save_resource(url, resource_list)
        # 将子url写到下层
        cls.__url_queue.append_url(sub_url_list)

    @classmethod
    def __get_page_text(cls, url):
        res = cls.__request_url(url)
        if res is None:
            return res
        res.encoding = 'utf-8'
        if res.status_code != 200:
            cls.__logger.error(res.text)
            cls.__logger.error('get_page_body error, res.status_code is {}, url: {}'.format(
                res.status_code, url))
            return None
        return res.text

    @classmethod
    def __request_url(cls, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) \
            AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.67 Safari/537.36'
        }
        res = None
        try:
            res = requests.get(url, headers=headers,
                               timeout=cls.__crawl_timeout, verify=False)
        except requests.ConnectionError as conn_error:
            cls.__logger.error(
                msg='ConnectionError in get_page_text, url = %s' % url, exc_info=conn_error)
            return None
        except requests.HTTPError as http_error:
            cls.__logger.error(
                msg='HTTPError in get_page_text, url = %s' % url, exc_info=http_error)
            return None
        except requests.RequestException as req_ex:
            cls.__logger.error(
                msg='RequestException in get_page_text, url = %s' % url, exc_info=req_ex)
            return None
        return res

    @classmethod
    def __get_resource_list(cls, page_text: str):
        pattern = re.compile(cls.__target_url)
        soup = bs4.BeautifulSoup(page_text, 'html.parser')
        tag_list = soup.findAll(src=pattern)
        resource_list = []
        for tag_item in tag_list:
            resource_list.append(tag_item.get('src'))
        return list(set(resource_list))

    @classmethod
    def __get_sub_urls(cls, url, page_text):
        ret_urls = set()
        soup = bs4.BeautifulSoup(page_text, 'html.parser')
        link_elements = soup.findAll('a')
        skip_flag = [None, '#', ' ', '']
        protocol = ['http', 'https']
        for item in link_elements:
            href = item.get('href')
            if not href:
                continue
            href_protocol = href.split(':')[0]
            if href in skip_flag:
                continue
            if href_protocol is None:
                ret_urls.add(urllib.parse.urljoin(url, href))
            elif href_protocol in protocol:
                ret_urls.add(href)
        return list(ret_urls)

    @classmethod
    def __save_resource(cls, url: str, resource_list: list):
        """
        description: 保存解析到的resource_list到本地
        param url: 抓取的原始url
        param resource_list: 资源列表
        return {*}
        """
        for resource in resource_list:
            if not str(resource).startswith('http'):
                resource = urllib.parse.urljoin(url, resource)
            if resource in cls.__requested_resource_list:
                continue
            file_name = urllib.parse.quote(resource, 'utf-8')
            ext_name = resource.split('.')[-1]
            res = cls.__request_url(resource)
            if res is None or res.status_code != 200:
                cls.__logger.error('url = %s , reuqest fail')
                continue
            file_path = os.path.join(cls.__out_put_dir, file_name)
            # 通过二进制方式打开文件
            with open(file_path, 'wb') as resource_file:
                if ext_name in WEB_FILE_EXT_NAMES:
                    resource_file.write(res.text.encode('utf-8'))
                # 对于图片等资源，通过 res.content获取
                else:
                    resource_file.write(res.content)
            cls.__requested_resource_list.append(resource)


if __name__ == '__main__':
    UrlCrawl.read_from_conf('conf/spider.conf')
    UrlCrawl.crawl_url('https://www.jd.com/')

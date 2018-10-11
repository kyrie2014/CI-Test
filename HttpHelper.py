# -*-coding:utf-8 -*-
import urllib2
import threading


class Singleton(type):
    mutex = threading.Lock()

    def __init__(cls, name, bases, dicts):
        super(Singleton, cls).__init__(name, bases, dicts)
        cls.instance = None

    def __call__(cls, *args, **kw):
        if cls.instance is None:
            Singleton.mutex.acquire()
            if cls.instance is None:
                cls.instance = super(Singleton, cls).__call__(*args, **kw)
            Singleton.mutex.release()
        return cls.instance


class HttpHelper:
    __metaclass__ = Singleton

    name = 'Http Helper'
    __req_header  =  {'Content-Type': r'application/x-www-form-urlencoded'}
    __req_url     =  r'http://tpm.unisoc.com/projectmanage/project/submitbug_testcenter'
    __req_timeout =  0
    __status      =  'STATUS OK'

    def __init__(self):
        pass

    def __build_get_request(self):
        """
        构建Get请求
        :return: request
        """
        return urllib2.Request(self.__req_url) \
            if len(self.__req_header) \
            else urllib2.Request(self.__req_url, headers=self.__req_header)

    def __build_ppd_request(self, data):
        """
        构建post,put,delete请求
        :param data:
        :return:
        """
        # params = HttpHelper.parser_data(data)
        return urllib2.Request(self.__req_url, data=data) \
            if len(self.__req_header) == 0 \
            else urllib2.Request(self.__req_url, headers=self.__req_header, data=data)

    def headers(self, headers):
        """
        添加header
        :param headers:
        :return:
        """
        self.__req_header = headers
        return self

    def url(self, url):
        """
        添加url
        :param url:
        :return:
        """
        print url
        self.__req_url = url
        return self

    def timeout(self, time):
        """
        添加超时
        :param time:
        :return:
        """
        self.__req_timeout = time
        return self

    def debug(self):
        """
        是否debug
        :return:
        """
        urllib2.install_opener(urllib2.build_opener(
            urllib2.HTTPHandler(debuglevel=1),
            urllib2.HTTPSHandler(debuglevel=1)
        ))
        return self

    def __handle_response(self, request):
        """
        处理response
        :param request:
        :param func:
        :return:
        """
        try:
            res = urllib2.urlopen(request) \
                if self.__req_timeout == 0 \
                else urllib2.urlopen(request, self.__req_timeout)
            if self.__status in res.read():
                return True
        except urllib2.HTTPError, e:
            print e.code
        return False

    def get(self):
        """
        get请求
        :return:
        """
        request = self.__build_get_request()
        return self.__handle_response(request)

    def post(self, data):
        """
        post请求
        :param data:
        :return: 响应结果
        """
        request = self.__build_ppd_request(data=data)
        return self.__handle_response(request)

    def put(self, data):
        """
        put请求
        :param data:
        :return:响应结果
        """
        request = self.__build_ppd_request(data=data)
        request.get_method = lambda: 'PUT'
        return self.__handle_response(request)

    def delete(self, data):
        """
        delete请求
        :param data:
        :return:响应结果
        """
        request = self.__build_ppd_request(data=data)
        request.get_method = lambda: 'DELETE'
        return self.__handle_response(request)

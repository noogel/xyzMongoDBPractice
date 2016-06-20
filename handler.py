#! /data/sever/python/bin/python
# -*- coding:utf-8 -*-
"""
@author: 'root'
@date: '6/20/16'
"""
__author__ = 'root'

import logging

import tornado


class BaseHandler(tornado.web.RequestHandler):
    """
    basehandler
    """
    def get(self, module):
        """
        get
        :param module:
        :return:
        """
        self._exec(module)

    def post(self, module):
        """
        post
        :return:
        """
        self._exec(module)

    def _exec(self, module):
        """
        exec
        :param module:
        :return:
        """
        method = getattr(self, module or 'index')
        if method and module not in ('get', 'post'):
            try:
                method()
            except Exception, e:
                logging.error("Error %s" % (str(e)), exc_info=True)
        else:
            raise tornado.web.HTTPError(404)


class MainHandler(BaseHandler):

    def get(self):
        self.render("index.html")


class MapHandler(BaseHandler):
    """
    map
    """
    def index(self):
        """
        map
        :return:
        """
        self.render("map.html")

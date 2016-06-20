#! /data/sever/python/bin/python
# -*- coding:utf-8 -*-
"""
@author: 'root'
@date: '6/20/16'
"""
__author__ = 'root'
import os
import sys
import logging

import tornado.ioloop
import tornado.web

import handler

logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s %(filename)s:%(lineno)d] %(levelname)s %(message)s',
    datefmt='%Y%m%d %H:%M:%S'
)


application = tornado.web.Application(
    handlers=[
        (r"/", handler.MainHandler),
        (r"/map(/[a-zA-Z_/]*)?", handler.MapHandler),
    ],
    **{
        'static_path': os.path.join(sys.path[0], 'static'),
        'template_path': os.path.join(sys.path[0], 'template'),
        'xsrf_cookies': False,
        'debug': True
    }
)

if __name__ == "__main__":
    application.listen(1234)
    tornado.ioloop.IOLoop.instance().start()

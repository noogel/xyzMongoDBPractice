#! /data/sever/python/bin/python
# -*- coding:utf-8 -*-
"""
@author: 'root'
@date: '6/21/16'
"""
__author__ = 'root'

import pymongo

DB_URI = "mongodb://localhost:27017"
DB_NAME = "map_test"


class MongoClient(object):
    """
    mongoclient
    """
    _CLIENT = pymongo.MongoClient(DB_URI)

    @property
    def client(self):
        """
        client
        :return:
        """
        return self._CLIENT

    @property
    def db(self):
        """
        db
        :return:
        """
        return self._CLIENT[DB_NAME]

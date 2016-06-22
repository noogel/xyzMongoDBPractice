#! /data/sever/python/bin/python
# -*- coding:utf-8 -*-
"""
@author: 'root'
@date: '6/20/16'
"""
__author__ = 'root'


import ujson as json
import logging

import tornado
from bson import ObjectId

from lib.mongoclient import MongoClient


class BaseHandler(tornado.web.RequestHandler, MongoClient):
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
        module = module[1:]
        method = getattr(self, module or 'index')
        if method and module not in ('get', 'post'):
            try:
                response = method()
            except Exception, e:
                logging.error("Error %s" % (str(e)), exc_info=True)
                response = self.ajax_error()
            if not self._finished:
                self.send_json(response)
        else:
            raise tornado.web.HTTPError(404)

    def get_all_arguments(self, ext=[]):
        """
        """
        return {k: v[0] for k, v in self.request.arguments.iteritems() if k not in ext}

    def get_argument(self, name, default=None):
        """
        """
        return self.request.arguments.get(name, [default])[0]

    def ajax_ok(self, body=[]):
        """
        """
        return {"code": 200, "msg": "操作成功！", "body": body}

    def ajax_error(self):
        """
        """
        return {"code": 300, "msg": "操作失败！", "body": None}

    def send_json(self, res):
        """
        write json
        """
        self.write(json.dumps(res))


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

    def insert_point(self):
        """
        insert
        :return:
        """
        x_point, y_point = self.get_argument("point", "").split(",")
        self.db.point.insert({"x": float(x_point), "y": float(y_point)})
        return self.ajax_ok()

    def remove_point(self):
        """
        remove
        :return:
        """
        # m_id = self.get_argument("m_id", "")
        x_point = self.get_argument("x_point", "")
        y_point = self.get_argument("y_point", "")
        self.db.point.remove({"x": float(x_point), "y": float(y_point)})
        return self.ajax_ok()

    def update_point(self):
        """
        update
        :return:
        """
        m_id = self.set_argument("m_id", "")
        x_point, y_point = self.get_argument("point", "").split(",")
        self.db.point.update({"_id": ObjectId(m_id)}, {"$set", {"x": float(x_point), "y": float(y_point)}})
        return self.ajax_ok()

    def find_point(self):
        """
        find
        :return:
        """
        m_id = self.get_argument("m_id", "")
        x_point, y_point = self.get_argument("point", ",").split(",")
        find_dict = {}
        if m_id:
            find_dict["_id"] = ObjectId(m_id)
        if x_point and y_point:
            find_dict["x"] = float(x_point)
            find_dict["y"] = float(y_point)
        count = self.db.point.find(find_dict).count()
        result = [{"_id": str(val["_id"]), "x": val["x"], "y": val["y"]} for val in self.db.point.find(find_dict)]
        body = {"count": count, "data": result}
        return self.ajax_ok(body=body)

    def point_indexes(self):
        """
        point_indexes
        :return:
        """
        indexes = self.db.point.indexes.find()
        return self.ajax_ok(body=indexes)
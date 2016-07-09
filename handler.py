#! /data/sever/python/bin/python
# -*- coding:utf-8 -*-
"""
@author: 'root'
@date: '6/20/16'
"""
__author__ = 'root'

import logging

import tornado
import ujson as json
from bson import ObjectId, Code

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
        self.db.point.insert({
            "x": float(x_point), "y": float(y_point),
            "local": {'type': "Point", 'coordinates': [float(x_point), float(y_point)]}
        })
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

    def update_point_ui(self):
        """
        update_point_ui
        :return:
        """
        x_point = self.get_argument("x_point", "")
        y_point = self.get_argument("y_point", "")
        point = self.db.point.find_one({"x": float(x_point), "y": float(y_point)})
        point["_id"] = str(point["_id"])
        self.render("update_point_ui.html", point=point)

    def update_point(self):
        """
        update
        :return:
        """
        m_id = self.set_argument("m_id", "")
        x_point = self.get_argument("x_point", "")
        y_point = self.get_argument("y_point", "")
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

    def distinct_x_ui(self):
        """
        x坐标去重
        :return:
        """
        distinct_x = self.db.point.distinct("x")
        self.render("distinct_x.html", distinct_x=distinct_x)

    def group_ui(self):
        """
        X轴坐标分类统计
        mongodb client example:
        db.test.group({key:{age:true},initial:{num:0},$reduce:function(doc,prev){
            prev.num++
        },
        condition:{$where:function(){
                return this.age>2;
            }
            }
        });

        arguments:
            initial: 初始对象
            key: 按其分组的字段
            reduce: 一个函数，管理如何输出值
            condition: 相当于where，筛选结果
        :return:
        """
        reducer = Code("""
            function (doc, prev){
                prev.num++
            }
        """)
        group = self.db.point.group(
            key={"x": True},
            initial={"num": 0},
            condition={"x": {"$gt": 91}},
            reduce=reducer
        )
        self.render("modal_tpl.html", info=group, title="X轴坐标分类统计")

    def map_reduce_ui(self):
        """
        map_reduce_ui
        map和reduce都是一个javascript的函数； map_reduce 方法会将统计结果保存到一个临时的数据集合中。
        :return:
        """
        mapper = Code("""
            function () {
                emit(this.x, 1);
            }
        """)

        reducer = Code("""
            function (key, values) {
                var total = 0;
                for (var i = 0; i < values.length; i++) {
                    total += values[i];
                }
                return total;
            }
        """)

        result = self.db.point.map_reduce(mapper, reducer, "num").find()
        result = [val for val in result]
        self.render("modal_tpl.html", info=result, title="X轴Map/Reduce练习")

    def find_near_ui(self):
        """
        地理空间索引查询
        make index:
        db.point.ensureIndex({"local.coordinates": "2d"})

        find near point:
        db.places.find( { loc :
                            { $near :
                              { $geometry :
                                 { type : "Point" ,
                                   coordinates : [ <longitude> , <latitude> ] } ,
                                $maxDistance : <distance in meters>
                         } } } )
        ps: 这种查询只能在不分片的集合上查询
        :return:
        """
        x_point, y_point = self.get_argument("point", ",").split(",")
        result = self.db.point.find({
            "local.coordinates": {
                '$near': [float(x_point), float(y_point)]
            }
        }).limit(5)
        info = []
        for item in result:
            item.pop("_id")
            info.append(item)
        self.render("modal_tpl.html", info=info, title="地理空间查询")

    def find_within_ui(self):
        """
        半径范围内查询
        :return:
        """
        x_point, y_point = self.get_argument("point", ",").split(",")
        result = self.db.point.find({
            "local.coordinates": {
                '$within': {
                    "$center": [[float(x_point), float(y_point)], 0.01]
                }
            }
        })
        info = []
        for item in result:
            item.pop("_id")
            info.append(item)
        self.render("modal_tpl.html", info=info, title="地理空间查询")

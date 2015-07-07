#########################
# Classes for Display and Edit of JSON to HTML
#########################

import json
import re
import string
import web
import bson
from bson.objectid import ObjectId

fundamentals = ['name', 'sn']

def isObjectId(test_key):
    seperate = test_key.split("_")
    if seperate[len(seperate)-1] == "id":
        return True
    else:
        return False

def getValue(key, value):
    ret_val = value
    if isObjectId(key):
        try:
            ret_val = ObjectId(value)
        except:
            ret_val = ""
    return ret_val

class element:

    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.label = self.decodeLabel()
        self.id_dis = ""
    
    def decodeLabel(self, format="underscore"):
        pretty = []
        if format == "underscore":
            seperate = self.key.split("_")
            for word in seperate:
                pretty.append(word.capitalize())
            return " ".join(pretty)
    def crossCollection(self, format="underscore"):
        parts = []
        if format == "underscore":
            parts = self.key.split("_")
            length = len(parts)
            if length > 0 and parts[length-1] == "id":
                if length > 2:
                    web.debug("Coss with Different Database")
                    return False
                else:                    
                    if len(parts[0]) > 0:
                        return "%ss" % (parts[0])
            else:
                return False
    def getFundamentalField(self, dbob):
        for fun in fundamentals:
            try:
                temp = dbob[fun]
                web.debug(temp)
                return temp
            except:
                pass
        return dbob['_id']


    def displayView(self, htmlClass="element", level=0):
        view = "<div style=\"padding-left:%dpx;\" class=\"%s label\" id=%s-label name=%s-label>%s</div>" % (level*10, htmlClass, self.key, self.key, self.label)
    
        if type(self.value) is dict:
            nested = []
            for x_c,y_c in self.value.iteritems():
                emb_index = "%s.%s" % (self.key, x_c)
                nested.append(element(emb_index, y_c).displayView(htmlClass, level+1))
                web.debug("found dict")
            web.debug("joing nested dict")
            view = "%s%s" % (view, "".join(nested))
        elif type(self.value) is list:
            web.debug("found list")
            view = "%s<ol>" % (view)
            for el in self.value:
                nested = []
                if type(el) is dict:
                    for x_c,y_c in el.iteritems():
                        emb_index = "%s.%s" % (self.key, x_c)
                        nested.append(element(emb_index, y_c).displayView(htmlClass, level+1))
                        web.debug("found dict %d" % (level))
                else:
                    web.debug("straight list")
                    nested.append(str(el))
                web.debug("joing nested list")
                view = "%s<li>%s</li>" % (view, "".join(nested))
            view = "%s</ol>" % (view)
        else:
            web.debug("reggs")
            view = "%s<div style=\"padding-left:%dpx;\" class=\"%s value\" id=%s-value name=%s-value>%s</div>" % (view, level*10, htmlClass, self.key, self.key, self.value)
        return view

    def submitView(self, DB, new=False):
        if new and self.key == "_id":
            return ""
        else:
            view = "<label for=\"%s\">%s</label>" % (self.key, self.label)
            cross = self.crossCollection()
            if cross:
                select = "<select name=\"%s\" id=\"%s\">" % (self.key, self.key)
                crosset = DB[cross].find()
                select = "%s<option value=\"0\">None</option>" % (select)
                for x in crosset:
                    if bson.objectid.ObjectId.is_valid(self.value) and self.value == x['_id']:
                        select = "%s<option value=\"%s\" selected=\"selected\">%s</option>" % (select, x["_id"], self.getFundamentalField(x))
                    else:
                        select = "%s<option value=\"%s\">%s</option>" % (select, x["_id"], self.getFundamentalField(x))
                select = "%s</select>" % (select)
                return "%s%s" % (view, select)
            else:
                return "%s<input type=\"text\" name=\"%s\" id=\"%s\" value=\"%s\" class=\"text ui-widget-content ui-corner-all\">" % (view, self.key, self.key, self.value)

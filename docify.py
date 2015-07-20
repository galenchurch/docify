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
    def overView(self, addr):
        return "<a href=\"%s\">%s</a>" % (addr, self.value)

class Document:
    def __init__(self, doc):
        self.elements = []

        for x, y in doc.iteritems():
            self.elements.append(element(x, y))
            if x == "_id":
                self.objId = y
                web.debug(y)

        self.time = self.objId.generation_time
        web.debug(self.elements)

class Collection:
    def __init__(self, coll, link, important=["_id"]):
        self.coll = []
        self.imp_els = important
        self.loc = link
        self.count = 0
        for x in coll:
            self.coll.append(Document(x))

    def elementalCol(self, element, num_els):
        
        viewcol = "<div class=\"collumn-%d\">" % (self.count)
        self.count = self.count + 1
        viewcol = "%s - <input type=text id=\"search-%s\" value=\"%s\"></input>" % (viewcol, element, element)
        for doc in self.coll:
            if num_els < 0:
                break
            else:
                num_els = num_els - 1
                found = False
                for el in doc.elements:
                    if el.key == element:
                        found = True
                        viewcol = "%s - %s" % (viewcol, el.overView("%s/%s" % (self.loc, doc.objId)))
                if not found:
                    viewcol  = "%s - N/A" % viewcol
        return viewcol

    def overHeader(self):
        viewhead = "<table><tr class=\"search-header\">"
        viewhead = "%s<td><input type=text class=\"search\" id=\"search-date\" value=\"date\"></input></td>"% (viewhead)
        for k in self.imp_els:
            # view = "%s%s" % (view, self.elementalCol(k, num_els))
            viewhead = "%s<td><input type=text class=\"search\" id=\"search-%s\" value=\"%s\"></input></td>" % (viewhead, k, k)
        viewhead = "%s</tr>" % (viewhead)
        web.debug(viewhead)
        return viewhead

    def overData(self, view_curr):
        view_curr  = "%s<tr><td><a href=\"%s/%s\">%s</a></td>" % (view_curr, self.loc, doc.objId, doc.time.date().isoformat())
                
        for el in doc.elements:
            for k in self.imp_els:
                if el.key == k:
                    view_curr = "%s<td>%s</td>" % (view_curr, el.overView("%s/%s" % (self.loc, doc.objId)))
                    
        view_curr = "%s<tr>" % (view_curr)
        return view_curr

    def overView(self, header=True, num_els=5):
        #create header/search bar

        if header:
            view = self.overHeader()
        else:
            view = "<table>"

        for doc in self.coll:
            if num_els < 0:
                break
            else:
                num_els = num_els - 1
                view = self.overData(view)
                
        view = "%s</table>" % view
        web.debug(view)
        return view



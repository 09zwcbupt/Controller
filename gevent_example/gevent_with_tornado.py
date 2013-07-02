#!/usr/bin/python
 
 
import tornado.httpclient
import tornado.ioloop
import gevent
 
 
def on_complete(data):
    print data.body[0:10]
 
def print_head(url):
    print ('Starting %s' % url)
    http = tornado.httpclient.AsyncHTTPClient()
    http.fetch("http://friendfeed.com", on_complete)
 
jobs = [gevent.spawn(print_head, url) for url in range(0, 50)]
gevent.joinall(jobs)
 
tornado.ioloop.IOLoop.instance().start()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'hubble2webb <hubble2webb@users.noreply.github.com>'
__copyright__ = 'Copyright 2015 hubble2webb'
__license__ = """Eclipse Public License - v 1.0 (http://www.eclipse.org/legal/epl-v10.html)"""

import urllib2
import base64

try:
    import json
except ImportError:
    import simplejson as json


def plugin(srv, item):
    # item.addrs is an array with three or more elements:
    # 0 is the Ionic appid
    # 1 is the Ionic appsecret (private key)
    # 2..N are the push tokens returned by Ionic push service

    srv.logging.debug("*** MODULE=%s: service=%s, target=%s", __file__, item.service, item.target)

    if len(item.addrs) < 3:
        srv.logging.error("appid, appsecret and atleast one devicetoken is required")
        return False

    appid = item.addrs[0]
    appsecret = item.addrs[1]
    devicetokens = item.addrs[2:]

    if not appid or appid.isspace():
        srv.logging.error("appid is missing or empty")
        return False
    if not appsecret or appsecret.isspace():
        srv.logging.error("appsecret is missing or empty")
        return False
    if len(devicetokens) == 0:
        srv.logging.error("atleast one devicetoken is required")
        return False

    devicetokens = filter(None, devicetokens)
    devicetokens = filter(lambda name: name.strip(), devicetokens)
    appid = appid.strip()
    appsecret = appsecret.strip()


    data = {"tokens": devicetokens}
    notification = {"alert": item.message}
    data["notification"] = notification

    resource = "https://push.ionic.io/api/v1/push"

    try:
        handler = urllib2.HTTPHandler()
        opener = urllib2.build_opener(handler)

        request = urllib2.Request(resource, data=json.dumps(data))
        request.add_header('X-Ionic-Application-Id', appid)
        request.add_header("Authorization", "Basic %s" % base64.encodestring('%s:' % appsecret).replace('\n', ''))
        request.add_header("Content-Type", 'application/json')

        connection = opener.open(request, timeout=5)
        srv.logging.info("Server reply: %s" % str(connection.read()))

    except urllib2.HTTPError, e:
        srv.logging.warn("Failed to send POST request to ionic using %s: %s" % (resource, str(e.read())))
        return False

    return True

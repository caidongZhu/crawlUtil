#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import dpkt
import pcap
import re
import socket
import time
from struct import unpack

pc = pcap.pcap('enp2s0')
pc.setfilter("port 80")
tracker={}
for ts, pkt in pc:
    try:
        #ethernet=dpkt.ethernet.Ethernet(pkt)
        ethernet = dpkt.ssl.SSL(pkt)
        ip=ethernet.data
        tcp=ip.data
        data=tcp.data
        print '++++++'
        #print data


        dst=socket.inet_ntoa(ip.dst)
        src=socket.inet_ntoa(ip.src)
        try:

            response = dpkt.http.Response(tcp.data)
            print '===='
            # file =open (str(ts)+'.txt',"wb")
            # file.write(response.body)
            # file.close()
            #print response.data
            print response.body
            #print response.headers


        except dpkt.dpkt.UnpackError:
            print "Encounted an unpacking error"
    except socket.error:
        continue
    ltuple=(src,tcp.sport,dst,tcp.dport)
    rtuple=(dst,tcp.dport,src,tcp.sport)
    try:
        tracker[ltuple]
        try:
            tracker[ltuple]['out']+=data
        except KeyError:
            tracker[ltuple]['out']=data
        tracker[ltuple]['lastseen']=time.time()
    except KeyError:
        try:
            tracker[rtuple]
            tracker[rtuple]['in']+=data
        except KeyError:
            tracker[rtuple]={
                'in'        : data,
                'complete'  : False,
                'firstseen' : time.time()
                }
        tracker[rtuple]['lastseen']=time.time()

    for connection in tracker.keys():
        if time.time()-tracker[connection]['lastseen']>600:
            del tracker[connection]
            continue
        if tracker[connection]['complete']==True:
            if time.time()-tracker[connection]['lastseen']>60:
                del tracker[connection]
            continue
        try:
            if tracker[connection]['in'] and tracker[connection]['out']:
                data=tracker[connection]['in']
                data+=tracker[connection]['out']
                uri=re.search("(GET|POST) ([^\r\n]*)",data,re.IGNORECASE)
                host=re.search("Host: ([^\r\n]*)",data,re.IGNORECASE)
                response=re.search("(HTTP/[\d\.]+) (\d+) ([^\r\n]+)",data,re.IGNORECASE)
                if uri and host and response:
                    # print "%-8d [%16s:%-6d => %16s:%-6d ] [ %s %s %-16s ] %6s http://%s%s" % (
                    #     len(tracker),
                    #     connection[0],
                    #     connection[1],
                    #     connection[2],
                    #     connection[3],
                    #     response.group(1),
                    #     response.group(2),
                    #     response.group(3),
                    #     uri.group(1),
                    #     host.group(1),
                    #     uri.group(2)
                    #     )
                    tracker[connection]['complete']=True
        except KeyError:
           pass

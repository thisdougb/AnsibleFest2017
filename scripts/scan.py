#!/usr/bin/env python
#
# simple proxy scanner for the Ansible Fest London demo
#
#

import requests
import time
import json
from datetime import datetime

def state_colour(current_state):
    if current_state:
        return '\033[1;33m' # YELLOW
    else:
        return '\033[1;34m' # WHITE

nodes = {}
header_idx = 0

try:
    while True:
        if len(nodes) > 0:
            node_count = len(nodes)
        else:
            node_count = 1
    
        for idx in range(node_count):
            try:
                r = requests.get('http://proxy')
                data = r.json()
                this_host = data['host']
    
                # if something change then flag for a new print colour
                if this_host in nodes:
                    if nodes[this_host]['password'] != data['password']:
                        data['state'] = not nodes[this_host]['state']
                    else:
                        data['state'] = nodes[this_host]['state']
                else:
                    data['state'] = False
    
                nodes[this_host] = data
    
            except Exception as e:
                #time_now = datetime.now().strftime("%H:%M:%S")
                #print('{0:10} *** {1} ***'.format(time_now, e))
                #nodes = {}
                pass
    
        for node in nodes:
            format_string = "    {0:10} {1:5} {2:15} {3:15} {4:8} {5}"
            header_idx += 1
            if header_idx == 1 or (header_idx % 20) == 0:
                print
                print(format_string.format('time', 'node', 'username', 'password', 'ssl', 'cert valid from'))
    
            time_now = datetime.now().strftime("%H:%M:%S")
            host = nodes[node]['host']
            user = nodes[node]['user']
            password = nodes[node]['password']
            ssl_version = nodes[node]['ssl_version']
            cert_date = nodes[node]['cert_date']
            color = state_colour(nodes[node]['state'])
            endcolor = '\033[0m'
            print(color + format_string.format(time_now, host, user, password[-14:], ssl_version, cert_date[:-9], color) + endcolor)
    
        time.sleep(1)
    
except KeyboardInterrupt:
    pass

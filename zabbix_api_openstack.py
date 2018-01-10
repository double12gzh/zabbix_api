import argparse
import json
from oslo_log import log as logging
import sys
import urllib2
from urllib2 import URLError

LOG = logging.getLogger(__name__)


class ZabbixAPI(object):
    def __init__(self, url="http://ip:port/zabbix/api_jsonrpc.php"):
        self.url = url
        self.authID = None
        self.hostgroupID = None
        self.templateID = None
        self.header = {"Content-Type": "application/json"}

    def user_login(self, username="admin", password="yourpass"):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": username,
                "password": password
            },
            "id": 0
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to log with ERROR: %s", e.code)
        else:
            response = json.loads(result.read())
            result.close()
            self.authID = response["result"]
            return self.authID

    def host_get(self, hostname=""):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.get",
            "params": {
                "output": "extend",
                "filter": {"host": hostname}
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)

        for key in self.header:
            request.add_header(key, self.header[key])

        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            if hasattr(e, "reason"):
                LOG.error("Failed to reach the server with ERROR: %s",
                          e.reason)
            elif hasattr(e, "code"):
                LOG.error("Failed to fulfill the request with ERROR: %s",
                          e.code)
        else:
            response = json.loads(result.read())
            result.close()

            LOG.info("number of vms: %s", len(response["result"]))

            for host in response["result"]:
                status = {"0": "OK", "1": "Disabled"}
                available = {
                    "0": "Unknown",
                    "1": "available",
                    "2": "Unavailable"
                }
                if len(hostname) == 0:
                    LOG.info("HostID: %(hostID)s, HostName: %(hostname)s, "
                             "Status: %(status)s, Available: %(available)s",
                             {
                                 "hostID": host["hostid"],
                                 "hostname": host["name"],
                                 "status": status[host["status"]],
                                 "available": available[host["available"]]
                             })
                else:
                    LOG.info("HostID: %(hostID)s, HostName: %(hostname)s, "
                             "Status: %(status)s, Available: %(available)s",
                             {
                                 "hostID": host["hostid"],
                                 "hostname": host["name"],
                                 "status": status[host["status"]],
                                 "available": available[host["available"]]
                             })

                    return host['hostid']

    def hostgroup_get(self, hostgroupname=''):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": hostgroupname
                }
            },
            "auth": self.user_login(),
            "id": 1,
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to get host group: %s", e)
        else:
            response = json.loads(result.read())
            result.close()
            for group in response['result']:
                if len(hostgroupname) == 0:
                    LOG.info("hostgroup: %s, groupid: %s",
                             group["name"], group["groupid"])
                else:
                    LOG.info("hostgroup: %s, groupid: %s",
                             group["name"], group["groupid"])
                    self.hostgroupID = group["groupid"]
                    return group["groupid"]

    def template_get(self, templatename=""):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.get",
            "params": {
                "output": "extend",
                "filter": {
                    "name": templatename
                }
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to get template with ERROR: %s", e)
        else:
            response = json.loads(result.read())
            result.close()
            for template in response['result']:
                if len(templatename) == 0:
                    LOG.info("template: %s, id: %s",
                             template["name"], template["templateid"])
                else:
                    self.templateID = response['result'][0]['templateid']
                    LOG.info("Template Name: %s", templatename)
                    return response['result'][0]['templateid']

    def hostgroup_create(self, hostgroupname):
        if self.hostgroup_get(hostgroupname):
            print "hostgroup  %s is exist !"%hostgroupname
            sys.exit(1)
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostgroup.create",
            "params": {
                "name": hostgroupname
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to create hostgroup with error %s.", e)
        else:
            response = json.loads(result.read())
            result.close()
            LOG.info("add host group: %s, hostgroupID: %s",
                     hostgroupname, response["result"]["groupids"])

            return response['result']['groupids']

    def host_create(self, hostip, hostgroupname, templatename):
        if self.host_get(hostip):
            LOG.error("The host already exists.")
            sys.exit(1)
        group_list = []
        template_list = []

        for i in hostgroupname.split(','):
            var = dict()
            var['groupid'] = self.hostgroup_get(i)
            group_list.append(var)
        for i in templatename.split(','):
            var = dict()
            var['templateid'] = self.template_get(i)
            template_list.append(var)

        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": hostip,
                "interfaces": [
                    {
                        "type": 1,
                        "main": 1,
                        "useip": 1,
                        "ip": hostip,
                        "dns": "",
                        "port": "10050"
                        }
                    ],
                "groups": group_list,
                "templates": template_list,
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to create host with error: %s", e)
        else:
            response = json.loads(result.read())
            result.close()
            LOG.info("add host: %s, tid: %s",
                     hostip, response["result"]["hostids"])

    def host_disable(self, hostip):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.update",
            "params": {
                "hostid": self.host_get(hostip),
                "status": 1
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "Error as ", e
        else:
            response = json.loads(result.read())
            result.close()
            LOG.info("The current status of vm: %s", self.host_get(hostip))

    def host_delete(self, hostid):
        hostid_list = []
        for i in hostid.split(','):
            var = dict()
            var['hostid'] = self.host_get(i)
            hostid_list.append(var)

        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": hostid_list,
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception, e:
            LOG.error("Failed to delete host with ERROR: %s", e)
        else:
            result.close()
            LOG.info("the host %s has already been deleted.", hostid)

    def template_create(self):
        import uuid
        host_group_name = "heat_" + uuid.uuid4().hex
        hg_id = self.hostgroup_create(host_group_name)[0]

        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.create",
            "params": {
                "host": "zenghuiHA",
                "groups": {"groupid": hg_id}
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception, e:
            LOG.error("Failed to create template with ERROR: %s", e)
        else:
            response = json.loads(result.read())
            result.close()

            return response["result"]["templateids"]

    def hostinterface_get(self, hostid=""):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "hostinterface.get",
            "params": {
                "hostids": hostid,
                "output": "extend"
                },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            LOG.error("Failed to get host interface with Error: %s", e)
        else:
            response = json.loads(result.read())
            result.close()
            host_interface_pair = []
            for result in response["result"]:
                host_interface_pair.append((result["hostid"],
                                            result["interfaceid"]))
                LOG.info("hostid: %(hostid)s, interfaceid: %(interfaceid)s",
                         {
                             "hostid": result["hostid"],
                             "interfaceid": result["interfaceid"]
                         })

            return host_interface_pair

    def item_get(self, item_id, key="general_cpu_util_", output="extend"):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "item.get",
            "params": {
                "output": output,
                "hostids": item_id,
                "search": {
                    "key_": key
                },
            },
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except Exception, e:
            LOG.error("Failed to get item values: %s.", e)
        else:
            response = json.loads(result.read())
            result.close()
            LOG.info("The item's value are: %s", response)
            return response


if __name__ == "__main__":
    zabbix = ZabbixAPI()

    parser = argparse.ArgumentParser(description='zabbix  api ',
                                     usage='%(prog)s [options]')
    parser.add_argument('-H', '--host', nargs='?', dest='listhost',
                        default='host',
                        help='get host')
    parser.add_argument('-G', '--group', nargs='?', dest='listgroup',
                        default='group',
                        help='get host group')
    parser.add_argument('-T', '--template', nargs='?', dest='listtemp',
                        default='template',
                        help='get template')
    parser.add_argument('-A', '--add-group', nargs=1, dest='addgroup',
                        help='add host group')
    parser.add_argument('-C', '--add-host', dest='addhost', nargs=3,
                        metavar=('192.168.2.1',
                                 'test01,test02',
                                 'Template01,Template02'),
                        help='add host, multi hosts are splited with comma.')
    parser.add_argument('-d', '--disable', dest='disablehost', nargs=1,
                        metavar=('192.168.2.1'),
                        help='disable host')
    parser.add_argument('-D', '--delete', dest='deletehost', nargs='+',
                        metavar=('192.168.2.1'),
                        help='delete hosts, multi hosts are splited with comma')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-i','--get-item', nargs=1, dest='getitem',
                        help='get items value')

    if len(sys.argv) == 1:
        print parser.print_help()
    else:
        args = parser.parse_args()
        if args.listhost != 'host':
            if args.listhost:
                zabbix.host_get(args.listhost)
            else:
                zabbix.host_get()
        if args.listgroup != 'group':
            if args.listgroup:
                zabbix.hostgroup_get(args.listgroup)
            else:
                zabbix.hostgroup_get()
        if args.listtemp != 'template':
            if args.listtemp:
                zabbix.template_get(args.listtemp)
            else:
                zabbix.template_get()
        if args.addgroup:
            zabbix.hostgroup_create(args.addgroup[0])
        if args.addhost:
            zabbix.host_create(args.addhost[0], args.addhost[1],
                               args.addhost[2])
        if args.disablehost:
            zabbix.host_disable(args.disablehost)
        if args.deletehost:
            zabbix.host_delete(args.deletehost[0])
        if args.getitem:
            zabbix.item_get(args.getitem[0])

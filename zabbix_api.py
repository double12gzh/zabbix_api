#coding:utf-8
import json
import urllib2
from urllib2 import URLError
import sys
import argparse


class ZabbixAPI(object):
    def __init__(self, url="http://ipaddress:8090/zabbix/api_jsonrpc.php",
                 username="admin", password="password",
                 header={"Content-Type": "application/json"}):
        self.url = url
        self.username = username
        self.password = password
        self.header = header

    def user_login(self):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "user.login",
            "params": {
                "user": self.username,
                "password": self.password
            },
            "id": 0
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "用户认证失败，请检查 !", e.code
        else:
            response = json.loads(result.read())
            result.close()
            authid = response["result"]
            return authid

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
            print "Failed to get host interface with Error: %s" % e
        else:
            response = json.loads(result.read())
            result.close()
            for result in response["result"]:
                print "hostid: %s, interfaceid: %s" % \
                      (result["hostid"], result["interfaceid"])

    def host_get(self, hostname=''):
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
                print "We failed to reach a server."
                print "Reason: ", e.reason
            elif hasattr(e, "code"):
                print "The server could not fulfill the request."
                print "Error code: ", e.code
        else:
            response = json.loads(result.read())
            result.close()
            print "主机数量: %s" % (len(response["result"]))
            for host in response["result"]:
                status = {"0": "OK", "1": "Disabled"}
                available = {"0": "Unknown", "1": "available",
                             "2": "Unavailable"}
                if len(hostname) == 0:
                    print "HostID : %s HostName : %s Status :%s " \
                          "Available :%s" % (host["hostid"], host["name"],
                                             status[host["status"]],
                                             available[host["available"]])
                else:
                    print "HostID : %s HostName : %s Status :%s " \
                          "Available :%s" % (host["hostid"], host["name"],
                                             status[host["status"]],
                                             available[host["available"]])
                    return host["hostid"]

    def host_delete_by_hostid(self, host_id):
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.delete",
            "params": [host_id],
            "auth": self.user_login(),
            "id": 1
        })
        request = urllib2.Request(self.url, data)
        for key in self.header:
            request.add_header(key, self.header[key])
        try:
            result = urllib2.urlopen(request)
        except URLError as e:
            print "Failed to delete host with error %s" % e
        else:
            response = json.loads(result.read())
            result.close()
            print response

    def hostgroup_get(self, hostgroupname=""):
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
            print "Error as ", e
        else:
            response = json.loads(result.read())
            result.close()
            for group in response["result"]:
                if len(hostgroupname) == 0:
                    print "hostgroup:  %s groupid : %s" %\
                          (group['name'], group['groupid'])
                else:
                    print "hostgroup:  %s groupid : %s" % \
                          (group["name"], group["groupid"])
                    hostgroup_id = group["groupid"]
                    return hostgroup_id

    def template_get(self, templatename=''):
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
            "id": 1,
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
            for template in response["result"]:
                if len(templatename) == 0:
                    print "template : %s id : %s" % (template["name"],
                                                     template["templateid"])
                else:
                    template_id = response["result"][0]["templateid"]
                    print "Template Name :  %s " % templatename
                    return template_id

    def hostgroup_create(self, hostgroupname):
        if self.hostgroup_get(hostgroupname):
            print "hostgroup  %s is exist !" % hostgroupname
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
            print "Error as ", e
        else:
            response = json.loads(result.read())
            result.close()
            print "添加主机组:%s  hostgroupID : %s" % \
                  (hostgroupname, response["result"]["groupids"])
            return response["result"]["groupids"]

    def host_create(self, hostip, host_uuid, hostgroupname, templatename):
        if self.host_get(hostip):
            print "该主机已经添加!"
            sys.exit(1)
        group_list = []
        template_list = []
        for i in hostgroupname.split(","):
            var = dict()
            var['groupid'] = self.hostgroup_get(i)
            group_list.append(var)
        for i in templatename.split(","):
            var = dict()
            var["templateid"] = self.template_get(i)
            template_list.append(var)
        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "host.create",
            "params": {
                "host": host_uuid,
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
            print "Error as ", e
        else:
            response = json.loads(result.read())
            result.close()
            print "添加主机 : %s tid :%s" % \
                  (hostip, response["result"]["hostids"])

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
            print '----主机现在状态------------'
            print self.host_get(hostip)

    def host_delete(self, hostid):
        hostid_list = []
        for i in hostid.split(","):
            var = dict()
            var["hostid"] = self.host_get(i)
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
            print e
        else:
            result.close()
            print "主机 %s  已经删除 !" % hostid

    def template_create(self, name="heat_"):
        import uuid
        host_group_name = name + "_" + uuid.uuid4().hex
        hg_id = self.hostgroup_create(host_group_name)[0]

        data = json.dumps({
            "jsonrpc": "2.0",
            "method": "template.create",
            "params": {
                "host": host_group_name,
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
            print e
        else:
            response = json.loads(result.read())
            result.close()
            print "templateid = %s" % response["result"]["templateids"]
            return response["result"]["templateids"]

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
            print e
        else:
            response = json.loads(result.read())
            result.close()
            print response

if __name__ == "__main__":
    zabbix = ZabbixAPI(url="http://ipaddress:8090/zabbix/api_jsonrpc.php",
                       username="admin", password="password")


    parser = argparse.ArgumentParser(description='zabbix  api ',
                                     usage='%(prog)s [options]')
    parser.add_argument('-H', '--host', nargs='?', dest='listhost',
                        default='host', help='查询主机')
    parser.add_argument('-G', '--group', nargs='?', dest='listgroup',
                        default='group', help='查询主机组')
    parser.add_argument('-T', '--template', nargs='?', dest='listtemp',
                        default='template', help='查询模板信息')
    parser.add_argument('-A', '--add-group', nargs=1, dest='addgroup',
                        help='添加主机组')
    parser.add_argument('-C', '--add-host', dest='addhost', nargs=4,
                        metavar=('192.168.2.1',
                                 '8ed69b37-7019-4022-9b25-5822909bed1b',
                                 'test01,test02',
                                 'Template01,Template02'),
                        help='添加主机,多个主机组或模板使用分号. 第一个参数是主机的IP，'
                        '第二个参数是主机的UUID，第三个参数是hostgroup名字，第四个参数是'
                        '模板的名字。')
    parser.add_argument('-d', '--disable', dest='disablehost', nargs=1,
                        metavar=('192.168.2.1'), help='禁用主机')
    parser.add_argument('-v', '--version', action='version',
                        version='%(prog)s 1.0')
    parser.add_argument('-i', '--get-item', nargs=1, dest='getitem',
                        help='get items value. Please offer the host id.')
    parser.add_argument('-t', '--create-template', nargs=1, dest='createtemplate',
                        help='create template. Please offer a template name')
    parser.add_argument('-DD', '--delete-host', nargs=1, dest='deletehost',
                        help='delete host. please offer the hostid to be deleted.')
    parser.add_argument('-D', '--delete', dest='deletehost', nargs='+',
                        metavar=('192.168.2.1'), help='删除主机,多个主机之间用分号')

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
            zabbix.host_create(args.addhost[0], args.addhost[1],args.addhost[2],
                               args.addhost[3])

        if args.disablehost:
            zabbix.host_disable(args.disablehost)

        if args.deletehost:
            zabbix.host_delete(args.deletehost[0])

        if args.getitem:
            zabbix.item_get(args.getitem[0])

        if args.createtemplate:
            zabbix.template_create(args.createtemplate[0])

        if args.deletehost:
            zabbix.host_delete_by_hostid(args.deletehost[0])


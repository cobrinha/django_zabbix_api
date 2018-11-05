#importa api do Zabbix  
from zabbix_api import ZabbixAPI
import sys, json

# importa lib local
#from lib.error import raiseError

ZABBIX_USRGRPID = '8'

'''
    Aqui vem o controlador do ZabbixAPI     
'''
class Zabbix():
    zapi     = ""
    server    = ""
    user     = ""
    password = ""
    host_id     = ""
    logged   = False

    def __init__(self):
        pass

### set/get
    def setHost(self, host=""):
        self.server = str(host)
        return True

    def setUser(self, user=""):
        self.user = str(user)
        return True

    def setPassword(self, password=""):
        self.password= str(password)
        return True

    def getHost(self):
        return self.server

    def getUser(self):
        return self.user

    def getPassword(self):
        return self.password

### login
    def login(self, user="", password=""):
        try:
            self.zapi = ZabbixAPI(str(self.server))
            self.zapi.login(self.user, self.password)
            #self.zapi.trigger.get({"expandExpression": "extend", "triggerids": range(0, 100)})
            if self.zapi.auth:
                self.logged = True
                return True
            else:
                return False
        except Exception,error:
            return False
   
### logout
    def logout(self):
        try:
            self.zapi.logout() 
            self.logged = False
            return True
        except Exception,error:
            return False

### list users
    def getUsers(self):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.get",
                "params": {
                    "output":  "extend",
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            users = self.zapi.do_request(data)
            return json.dumps(users)
        except Exception,error:
            return False

    def massAddUserGroup(self, user_group_id, host_group_id):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "usergroup.massadd",
                "params": {
                    "usrgrpids": user_group_id,
                    "rights": {
                        "permission": 2,
                        "id": host_group_id
                    }
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            massadd = self.zapi.do_request(data)
            return json.dumps(massadd)
        except Exception,error:
            return str(error)

### inclui um novo grupo de usuarios
    def createUserGroup(self, alias):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "usergroup.create",
                "params": {
                    "name":  alias,
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### inclui um novo grupo de usuarios
    def createHostGroup(self, alias):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "hostgroup.create",
                "params": {
                    "name":  alias
                },
                 "auth": self.zapi.auth,
                 "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### list grupos
    def getGroups(self):
        try:
            groups = self.zapi.hostgroup.get({"output": "extend", "sortfield": "name"}) 
            return  json.dumps(groups)
        except Exception,error:
            return False

### list hosts
    def getHosts(self):
            try:
                hosts = self.zapi.host.get({"output":  "extend", "sortfield": "name"}) 
                return hosts
            except Exception,error:
                return False

### lista itens de um determinado host
    def getItems(self, host_id):
        if host_id:
            try:
                items = self.zapi.item.get({"output":  "extend",  "hostids": host_id}) 
                return  json.dumps(items)
            except Exception,error:
                return False
        else:
            return False

### lista templates
    def getTemplates(self):
        try:
            templates = self.zapi.template.get({"output":  "extend"}) 
            return json.dumps(templates) 
        except Exception,error:
            return False

### lista triggers de um determinado host
    def getTriggers(self, host_id):
        if host_id:
            try:
                triggers = self.zapi.trigger.get({"output":  "extend",  "hostids": host_id}) 
                return json.dumps(triggers)
            except Exception,error:
                return False
        else:
            return False

### inclui um novo usuario
    def createUser(self, alias, passwd, usrgrpid = ZABBIX_USRGRPID):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.create",
                "params": {
                    "alias":  str(alias),
                    "passwd": str(passwd),
                    "type": "1",
                    "usrgrps": [
                        {
                            "usrgrpid":  int(usrgrpid)
                        }
                    ],
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### inclui um novo action ###
    def createPingAction(self, nome, usrgrpid, host_group_id):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "action.create",
                "params": {
                    "name": str(nome),
                    "eventsource": 0,
                    "status": 0,
                    "esc_period": 120,
                    "def_shortdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}",
                    "def_longdata": "{TRIGGER.NAME}: {TRIGGER.STATUS}\r\n{ITEM.NAME1} ({HOST.NAME1}:{ITEM.KEY1}): {ITEM.VALUE1}\r\n {ITEM.LASTVALUE}\r\n\r\n{TRIGGER.URL}",
                    "filter": {
                        "evaltype": 0,
                        "conditions": [ 
                                { "conditiontype": 3, "operator": 2, "value": str(nome)}
                        ]
                     },
                    "operations": [
                            {"operationtype": 0, "esc_period": 0, "esc_step_from": 1, "esc_step_to": 2, "evaltype": 0, "opmessage_grp": [{ "usrgrpid": int(usrgrpid) }], "opmessage": { "default_msg": 1, "mediatypeid": "1"}},
                    ]
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### altera usuario ###
    def updateUser(self, userid, alias, passwd, usrgrpid = ZABBIX_USRGRPID):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.update",
                "params": {
                    "userid":  str(userid),
                    "alias":  str(alias),
                    "passwd": str(passwd),
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### cria media para usuario
    def createMedia(self, user_id, email):
        try:
            data = json.dumps({
                "jsonrpc": "2.0",
                "method": "user.addmedia",
                "params": {
                    "users": [ {
                            "userid":  str(user_id)
                        } ],
                    "medias": {
                        "mediatypeid": "1",
                        "sendto": email,
                        "active": 0,
                        "severity": 63,
                        "period": "1-7,00:00-24:00"
                    }
                },
                "auth": self.zapi.auth,
                "id": self.zapi.id
            })
            resp = self.zapi.do_request(data)
            return json.dumps(resp)
        except Exception,error:
           return False

### inclui um novo host
    def createHost(self, nome,  dictInterfaces,  dictGroups):
        try:
            resp = self.zapi.host.create({
                 "host" : nome, 
                 "interfaces": [dictInterfaces],
                 "groups": [dictGroups]
            })
            return json.dumps(resp) 
        except Exception,error:
           return str(error)

### exclui um host
    def deleteHost(self, host_id):
        try:
            resp = self.zapi.host.delete({"hostid": host_id})
            return json.dumps(resp) 
        except Exception,error:
           return False

### ativa/desativa monitoracao do host
    def updateHost(self, host_id, status=1):
        try:
            resp = self.zapi.host.update({"hostid": host_id, "status": status})
            return json.dumps(resp) 
        except Exception,error:
           return False

### retorna o uptime do host
    def getHostUptime(self, host_id):
        try:
            uptime = self.zapi.item.get({'output': "extend", 'hostids': host_id, 'search': {'key_':'system.uptime'}})
            return uptime[0]['lastvalue']
        except Exception,error:
           return False

### retorna o ID da interface um item
    def getHostInterface(self, host_id):
        try:
            host_interface = self.zapi.hostinterface.get({"hostid": host_id} )
            return host_interface
            interface = host_interface[0]["interfaceid"]
            return interface
        except Exception,error:
           return False

### inclui um novo item ###
    def createPingItem(self, nome, host_id, interface_id):
        try:
            resp = self.zapi.item.create({
                'hostid' : host_id,
                'interfaceid' : interface_id,
                'name' : str(nome),
                'key_' : 'icmpping['+nome+',100,20,256,60]',
                'delay' : 3600,
                'type' : 3,
                'value_type' : 1 
            }) 
            return json.dumps(resp) 
        except Exception,error:
           return False

    ##incluir uma nova trigger ###
    def createPingTrigger(self, host_id, nome, endereco):
            try:
                resp = self.zapi.trigger.create({
                        'hostid': host_id,
                        'description': 'Equipamento '+str(endereco)+' sem responder PING',
                        'status' : 0,
                        'type' : 3,
                        'priority' : 3,
                        'expression' : '{'+str(nome)+':icmpping['+str(endereco)+',100,20,256,60].last()}=0'
                 })
                return json.dumps(resp) 
            except Exception,error:
               return str(error)

if __name__ == "__main__": 
    zab = Zabbix()
    zab.setHost('http://zabbix.brfibra.com.br')
    zab.setUser('diego')
    zab.setPassword('diego')
    if zab.login() == True:
        print "Logou-se"
        useip = 1
        dns = ''
        interfaces =   { 
            "type":  1, 
            "main":  1, 
            "useip":  useip, 
            "ip":  '200.215.208.199', 
            "dns":  dns, 
            "port":  0
        }   
        groups = {
            "groupid" :  4
        }
        print(str(zab.createHost("Teste Host 12345",  interfaces,  groups)))

        #print zab.getUsers()
        #print zab.updateUser('4', 'joao2@joao.com', 'novasenha')

    else:
        print "erro ao logar-se"

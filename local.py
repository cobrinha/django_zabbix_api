DEBUG = True

ALLOWED_HOSTS = ['*']

#banco AZABBIX
DATABASE_NAME = "azabbix"
DATABASE_USER = "aemail"
DATABASE_PASSWORD = "password_here"
DATABASE_HOST = "localhost"

#banco azabbix_logs
DATABASE_LOG_NAME = "azabbix_logs"
DATABASE_LOG_USER = "aemail"
DATABASE_LOG_PASSWORD = "password_here"
DATABASE_LOG_HOST = "localhost"

#tabela de Servidores Zabbix
SERVER_ZABBIX = {}

SERVER_ZABBIX_DEFAULT = 'server_host'
SERVER_ZABBIX['server_host']   = {'usuario':'Admin', 'senha':'databasepwd'}

#Zabbix - defaults
ZABBIX_ADMGRPID = "7" #default admin group id
ZABBIX_USRGRPID = "8" #default users group id
ZABBIX_GRPID = "8" #default hosts group id

#LOG
LOG_PATH = "azabbix.log"
PID_PATH =  "azabbix/azabbix.pid"

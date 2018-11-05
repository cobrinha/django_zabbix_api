from django.db import models

# Create your models here.

class ApiErrors(models.Model):    
    code = models.CharField(max_length=30)
    message = models.CharField(max_length=255)    
    class Meta:
        db_table = u"api_errors"

class ApiUsers(models.Model):    
    name = models.CharField(max_length=32)
    api_key = models.CharField(max_length=32)
    data_update = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u"api_users"

class ApiTipo(models.Model):    
    nome = models.CharField(max_length=30)
    tabela = models.CharField(max_length=60)
    campo = models.CharField(max_length=60)
    class Meta:
        db_table = u"api_tipo"

class ApiAction(models.Model):
    nome = models.CharField(max_length=60)
    alias = models.CharField(max_length=60)
    data_criacao = models.DateTimeField()
    data_alteracao = models.DateTimeField(auto_now=True)
    class Meta:
        db_table = u"api_action"

class ApiLogs(models.Model):
    user = models.ForeignKey(ApiUsers,null=True)
    error = models.ForeignKey(ApiErrors,null=True)
    referencia_id = models.IntegerField(null=True,blank=True)
    tipo = models.ForeignKey(ApiTipo,null=True,blank=True)
    action = models.ForeignKey(ApiAction,null=True,blank=True)
    usuario = models.CharField(max_length=50,null=True,blank=True)
    remote_addr = models.CharField(max_length=25)
    path = models.CharField(max_length=50)
    get_params = models.TextField()
    post_params = models.TextField()
    result = models.TextField(blank=True,null=True)
    obs = models.CharField(max_length=50,blank=True,null=True)
    data_create = models.DateTimeField()
    class Meta:
        db_table = u"api_logs"

## models do azabbix ##
class Status(models.Model):  
    nome = models.CharField(max_length=255)      
    label = models.CharField(max_length=255)      
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"status"

class Servidor(models.Model):  
    nome = models.CharField(max_length=255)      
    label = models.CharField(max_length=255)      
    endereco = models.CharField(max_length=255)   
    status = models.ForeignKey(Status,null=True)
    data_criacao = models.DateTimeField()
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"servidor"

class Usuario(models.Model):  
    status = models.ForeignKey(Status,null=True)
    servidor  = models.ForeignKey(Servidor,null=True)
    nome = models.CharField(max_length=255)    
    label = models.CharField(max_length=255)    
    email = models.CharField(max_length=255)    
    usuario = models.CharField(max_length=255)    
    tentativa = models.IntegerField(default=0,blank=True)
    zabbix_id = models.IntegerField(default=0,blank=True)
    zabbix_grupo_id = models.IntegerField(default=0,blank=True)
    contrato = models.CharField(max_length=255)    
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"usuario"

class Host(models.Model):  
    status = models.ForeignKey(Status,null=True)
    usuario = models.ForeignKey(Usuario,null=True)
    nome = models.CharField(max_length=255)   
    label = models.CharField(max_length=255)   
    endereco = models.CharField(max_length=255)   
    tipo = models.CharField(default='IP')   
    porta = models.IntegerField(default=80)    
    zabbix_id = models.IntegerField(default=0,blank=True)
    zabbix_grupo_id = models.IntegerField(default=0,blank=True)
    tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"host"

class Item(models.Model):  
    status = models.ForeignKey(Status,null=True)
    host = models.ForeignKey(Host,null=True)
    nome = models.CharField(max_length=255)   
    label = models.CharField(max_length=255)   
    zabbix_id = models.IntegerField(default=0,blank=True)
    tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"item"

class Trigger(models.Model):  
    status = models.ForeignKey(Status,null=True)
    host = models.ForeignKey(Host,null=True)
    nome = models.CharField(max_length=255)   
    label = models.CharField(max_length=255)   
    zabbix_id = models.IntegerField(default=0,blank=True)
    tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"trigger"

class Action(models.Model):  
    status = models.ForeignKey(Status,null=True)
    host = models.ForeignKey(Host,null=True)
    nome = models.CharField(max_length=255)  
    label = models.CharField(max_length=255)   
    zabbix_id = models.IntegerField(default=0,blank=True)
    tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"action"

class Host(models.Model):  
    status = models.ForeignKey(Status,null=True)
    usuario = models.ForeignKey(Usuario,null=True)
    nome = models.CharField(max_length=255)   
    label = models.CharField(max_length=255)   
    endereco = models.CharField(max_length=255)   
    tipo = models.CharField(default='IP')   
    porta = models.IntegerField(default=80)    
    zabbix_id = models.IntegerField(default=0,blank=True)
    tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"host"

class Teste(models.Model):  
    status = models.ForeignKey(Status,null=True)
    nome = models.CharField(max_length=255)   
    label = models.CharField(max_length=255)   
    porta = models.IntegerField(default=80)    
    #tentativa = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"teste"

class HostTeste(models.Model):  
    teste = models.ForeignKey(Teste,null=True)
    host = models.ForeignKey(Host,null=True)
    porta = models.IntegerField(default=80)    
    tentativa = models.IntegerField(null=True,blank=True)
    zabbix_item_id = models.IntegerField(null=True,blank=True)
    zabbix_trigger_id = models.IntegerField(null=True,blank=True)
    data_criacao = models.DateTimeField()     
    data_atualizacao = models.DateTimeField(auto_now=True)     
    data_exclusao = models.DateTimeField(null=True)     
    class Meta:
        db_table = u"host_teste"

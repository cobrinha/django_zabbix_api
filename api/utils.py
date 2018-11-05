# -*- coding: utf-8 -*-
# importa outras lib
import local, json, re, datetime, copy, string, random

class ZabbixUtils:
    def __init__(self):
        #nada aqui
        pass

    def validarEmail(self, email):
        match = re.search(r'[\w.-]+@[\w.-]+.\w+', email)
        if match:
            return True
        else:
            return False
        
    def validarIP(self, ip):
        a = ip.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True

    def validarContrato(self, word):
        pattern = re.compile(r'\s+')
        word = re.sub(pattern, '', word)
        total = len(word) - word.count(' ')
        if(int(total) == 10):
            return True
        else:
            return False



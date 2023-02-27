from logs import log, dbg
from json import loads, dumps
from pprint import pprint
from requests import session


class credManager(object):
    def __init__(self, config=None, label=None, value=None, type=None, uuid=None):
        self.config    = config
        self.label = label
        self.value = value
        self.type = type
        self.uuid  = uuid

        self.prepareSession()


    def prepareSession(self):
        self.session = session()
        self.session.headers["Authorization"] = self.config.token


    def newCred(self):
        params = {
            "label": self.label,
            "type" : self.type,
            "value": self.value,
        }

        if (r:= self.session.post(self.config.url + "/api/credentials", json=params)).status_code == 200:
            log("credManager.newCred", "Succesfully created new cred")
            pprint(loads(r.text))
            return True
        else:
            log("credManager.newCred", "Could not create new cred")
            dbg("credManager.newCred", "CODE: {}".format(r.status_code))
            dbg("credManager.newCred", r.text)
            return False


    def delCred(self):

        if (r:= self.session.delete(self.config.url + "/api/credentials/" + self.uuid)).status_code == 200:
            log("credManager.delCred", "Succesfully deleted cred")
            return True
        else:
            log("credManager.delCred", "Could not delete cred")
            dbg("credManager.delCred", "CODE: {}".format(r.status_code))
            dbg("credManager.delCred", r.text)
            return False


    def updateCred(self):
        params = {}

        updated = False
        for (v, k) in enumerate(self.__dict__):
            if self.__dict__[k] is not None and k not in ["uuid", "config", "session"]:
                params[k] = self.__dict__[k]
                updated = True

        if not updated:
            log("credManager.updateCred", "No value to update")
            return False

        if (r:= self.session.put(self.config.url + "/api/credentials/" + self.uuid, json=params)).status_code == 200:
            log("credManager.updateCred", "Successfully updated cred")
            return True
        else:
            log("credManager.updateCred", "Could not update cred")
            dbg("credManager.updateCred", "CODE: {}".format(r.status_code))
            dbg("credManager.updateCred", r.text)
            return False


    def listCred(self):
        if (r:= self.session.get(self.config.url + "/api/credentials")).status_code == 200:
            log("credManager.listCred", "Successfully retrieved cred list:")
            pprint(loads(r.text))
            return True
        else:
            log("credManager.listCred", "Could not list cred, check your config")
            dbg("credManager.listCred", "CODE: {}".format(r.status_code))
            dbg("credManager.listCred", r.text)
            return False
            



    
            

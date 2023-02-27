from logs import log, dbg
from os import urandom
from string import ascii_letters, digits
from requests import session
from pprint import pprint
from json import loads, dumps


printable = ascii_letters + digits


class tokenManager(object):
    def __init__(self, config=None, tokenUuid=None, tokenLabel=None):
        self.config = config
        self.tokenUuid = tokenUuid
        self.tokenLabel = tokenLabel
        self.prepareSession()


    def prepareSession(self):
        self.session = session()
        self.session.headers["Authorization"] = self.config.token


    def generateRandomSeed(self, size=8):
        seed = ""
        while len(seed) != size:
            try:
                b = urandom(1).decode('ascii')
                if b in printable:
                    seed += b
            except UnicodeDecodeError:
                pass
        return seed


    def newToken(self):
        label = self.tokenLabel if self.tokenLabel else "zenscannercli_{}".format(self.generateRandomSeed())
        params = {
            "label": label,
        }

        if (r:= self.session.post(self.config.url + "/api/access_tokens", json=params)).status_code == 200:
            log("tokenManager.newToken", "Succesfuly created access token:")
            pprint(loads(r.text))
            return True
        else:
            log("tokenManager.newToken", "Something went wrong ! Check your config")
            dbg("tokenManager.newToken", "CODE: {}".format(r.status_code))
            dbg("tokenManager.newToken", r.text)
            return False


    def delToken(self):

        if (r:= self.session.delete(self.config.url + "/api/access_tokens/"+ self.tokenUuid)).status_code == 200:
            log("tokenManager.delToken", "Succesfully deleted token!")
            return True
        else:
            log("tokenManager.delToken", "Could not delete token")
            dbg("tokenManager.delToken", "CODE: {}".format(r.status_code))
            dbg("tokenManager.delToken", r.text)
            return False
            

    def checkToken(self):
        s = session()
        s.headers["Authorization"] = "Bearer {}".format(self.tokenUuid)

        if s.get(self.config.url + "/api/access_tokens").status_code == 200:
            log("tokenManager.checkToken", "Token is valid")
            return True
        else:
            log("tokenManager.checkToken", "Invalid token")
            return False


    def listToken(self):
        if (r:= self.session.get(self.config.url + "/api/access_tokens")).status_code == 200:
            log("tokenManager.listToken", "Succesfully retrieved access tokens:")
            pprint(loads(r.text))
            return True
        else:
            log("tokenManager.listToken", "Could not retrieve token list")
            dbg("tokenManager.listToken", "CODE: {}".format(r.status_code))
            dbg("tokenManager.listToken", r.text)
            return False

from os.path import exists, expanduser
from requests import session
from logs import log, dbg
from getpass import getpass, getuser
from sys import platform
from json import loads, dumps
from os import urandom



class localAuth(object):
    def __init__(self, config=None, configHandler=None, firstLogin=False, verify=False):
        self.config = config
        self.configHandler = configHandler

        if firstLogin:
            # firstlogin, ignore username & password
            self.firstLogin()

        if verify:
            self.verify()

    
    def verify(self):
        s = session()
        s.headers["Authorization"] = self.config.token

        if (r := s.get(self.config.url + "/api/access_tokens")).status_code == 200:
            log("localAuth.verify", "Token is valid")
            return True
        else:
            log("localAuth.verify", "Token is not valid, you need to reauth !")
            dbg("localAuth.verify", "Code: {}".format(r.status_code))
            dbg("localAuth.verify", r.text)
            return False


    def firstLogin(self):
        username = input("Login: ")
        password = getpass()
        url = input("URL: ")

        if url[-1] != "/":
            # append a trailing / if not present
            url += "/"

        s = session()

        params = {
            "username": username,
            "password": password
        }
        login = s.post(url + "/api/auth/login", json=params)
        if login.status_code == 200:
            dbg("localAuth.firstLogin", "Login Successful")
            
            params = {
                "label": "{}-{}-{}".format(username, platform, getuser())
            }
            tokenCreate = s.post(url + "/api/access_tokens", json=params, headers={"Authorization": "Bearer " + login.json()['access_token']})

            if tokenCreate.status_code == 200:
                data = loads(tokenCreate.text)
                token = "Bearer {}".format(data["token"])
                self.config = self.configHandler.createEmptyConfig()
                self.config.token = token
                self.config.url = url

                if self.configHandler.putConfig():
                    log("localAuth.firstLogin", "config file successfully created")
                    return True
                else:
                    log("localAuth.firstLogin", "Token was created successfuly but we could not save config file")
            else:
                log("localAuth.firstLogin", "Could not generate token")
                dbg("localAuth.firstLogin", "Code: {}".format(tokenCreate.status_code))
                dbg("localAuth.firstLogin", tokenCreate.text)
        else:
            log("localAuth.firstLogin", "Login was not successful")
        return False

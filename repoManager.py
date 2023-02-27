from logs import log, dbg
from requests import session
from pprint import pprint
from prettytable import PrettyTable
from json import loads, dumps
from paginationHandler import paginationHandler


class repoManager(object):
    def __init__(self, name=None, url=None, credUuid=None, repoUuid=None, branch=None, task_id=None, keyword=None, config=None, source_control="git"):
        self.name     = name
        self.url      = url
        self.credUuid = credUuid
        self.config   = config
        self.repoUuid = repoUuid
        self.branch   = branch
        self.task_id  = task_id
        self.keyword  = keyword
        self.source_control = source_control
        self.prepareSession()
    
    
    def prepareSession(self):
        self.session = session()
        self.session.headers["Authorization"] = self.config.token


    def newRepo(self):

        params = {
            "url"        : self.url,
            "name"       : self.name,
            "source_control": self.source_control
        }
        if self.credUuid:
            params["credential"] = self.credUuid

        if (r:= self.session.post(self.config.url + "/api/repositories", json=params)).status_code == 200:
            log("reposManager.newRepo", "repo succesfully created:")
            pprint(loads(r.text))
            return True
        else:
            log("reposManager.newRepo", "Could not add repo")
            dbg("repoManager.newRepo", "CODE: {}".format(r.status_code))
            dbg("repoManager.newRepo", r.text)
            return False


    def delRepo(self):
        if (r:= self.session.delete(self.config.url + "/api/repositories/" + self.repoUuid)).status_code == 200:
            log("repoManager.delRepo", "Repo successfuly deleted")
            return True
        else:
            log("repoManager.delRepo", "Could not del repo")
            dbg("repoManager.delRepo", "CODE: {}".format(r.status_code))
            dbg("repoManager.delRepo", r.text)
            return False


    def getRepo(self):
        
        params = {
            "search": self.keyword
        }

        p = paginationHandler(
            self.session, 
            self.config.url + "/api/repositories", 
            params=params
        )

        repos = p.get()
        if not repos is False and len(repos) > 0:
            log("repoManager.getRepo", "Got {} results".format(len(repos)))
            for repo in repos:
                pprint(repo)
        else:
            log("repoManager.getRepo", "Could not get repo")
            return False


    def listResults(self):

        params = {}

        p = paginationHandler(
            self.session, 
            self.config.url + "/api/repositories/{}/scans".format(self.repoUuid),
            params=params
        )

        results = p.get()
        if not results is False: 
            if len(results) > 0:
                log("repoManager.listResults", "Results:")
                for result in results:
                    pprint(result)
            else:
                log("repoManager.listResults", "No results for this repo")
            return True
        else:
            log("repoManager.getResult", "Could not get result for this repo")
            return False


    def getResult(self):

        if (r:= self.session.get(self.config.url + "/api/scans/{}".format(self.task_id))).status_code == 200:
            result = loads(r.text)
            if (status:= result["status"]) == "SUCCESS":
                # success
                if (r:= self.session.get(self.config.url + "scans/{}/result".format(self.task_id))).status_code == 200:
                    # result
                    data = loads(r.text)
                    details = data["details"]
                    vulnerabilities = data["vulnerabilities"]
                    count = 0
                    for key, value in vulnerabilities.items():
                        count += value if "NEW" not in key else 0
                    dbg("repoManager.getResult", data)
                    log("repoManager.getResult", "Result for scan ({} vulnerabilities were found):".format(count))
                    for detail in details:
                        pprint(detail)
                    return True

            else:
                log("repoManager.getResult", "Scan is not finished or revoked ({} != SUCCESS)".format(status))
                dbg("repoManager.getResult", "CODE: {}".format(r.status_code))
                dbg("repoManager.getResult", r.text)
                return False
        else:
            log('repoManager.getResult', "Could not retrieve scan status")
            dbg("repoManager.getResult", "CODE: {}".format(r.status_code))
            return False


    def scanRepo(self):

        params = {}
        
        if self.branch:
            params["branch"] = self.branch

        if (r:= self.session.post(self.config.url + "/api/repositories/{}/scan".format(self.repoUuid), json=params)).status_code == 200:
            log("repoManager.scanRepo", "Scan successfuly started")
            return True
        else:
            log("repoManager.scanRepo", "Could not start scan")
            dbg("repoManager.scanRepo", "CODE: {}".format(r.status_code))
            dbg("repoManager.scanRepo", r.text)
            return False


    def listRepo(self):
        
        p = paginationHandler(self.session, self.config.url + "/api/repositories", params={})
        repos = p.get()
        if not repos is False and len(repos) > 0:
            log("repoManager.listRepo", "Succesfuly got repos info:")
            
            tbl = PrettyTable()
            tbl.field_names = ["name", "uuid"]
            count = 0
            for repo in repos:
                if not self.keyword or self.keyword in repo["name"] or self.keyword in repo["url"]:
                    count += 1
                    tbl.add_rows([[repo["name"], repo["uuid"]]])
                    
            print(tbl if count else "Could not find repo matching \"{}\"".format(self.keyword))
            return True
        else:
            log("repoManager.listRepo", "Could not list repo")
            return False

    
    def updateRepo(self):
        
        params = {
            "uuid" : self.repoUuid,
        }

        updated = False
        for (v, k) in enumerate(self.__dict__):
            if self.__dict__[k] is not None and k not in ["uuid", "config", "session"]:
                params[k] = self.__dict__[k]
                updated = True

        if not updated:
            log("repoManager.updateRepo", "No value to update")
            return False

        if (r:= self.session.put(self.config.url + "repositories", json=params)).status_code == 200:
            log("repoManager.updateRepo", "Successfuly updated repo")
            return True
        else:
            log("repoManager.updateRepo", "Could not update repo")
            dbg("repoManager.updateRepo", "CODE: {}".format(r.status_code))
            dbg("repoManager.updateRepo", r.text)
            return False

        
    
        

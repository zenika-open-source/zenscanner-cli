from requests import session
from json import loads, dumps
from localrepos import repo
from logs import log, dbg
from time import sleep
from prettytable import PrettyTable


class client(object):
    def __init__(self, authkey, host):
        self.host = host
        self.authkey = authkey
        self.prepareSession()


    def prepareSession(self):
        self.session = session()
        self.session.headers["Repository"] = self.authkey
        dbg("client.prepareSession", "Repository: {}".format(self.session.headers["Repository"]))


    def getUploadInfo(self):

        if (r := self.session.get(self.host + "/api/repositories/{}/upload".format(self.repo.uuid))).status_code == 200:
            data = loads(r.text)
            log("client.getUploadInfo", "type: {}, url: {}".format(data["type"], data["url"]))
            return data
        else:
            log("client.getUploadInfo", "Something went wrong")
            dbg("client.getUploadInfo", "CODE: {}".format(r.status_code))
            dbg("client.getUploadInfo", r.text)
            raise Exception("Check parameters")
        return None


    def doUpload(self, uploadInfo):
        r = self.session.put(uploadInfo["url"], data=self.repo.getReadHandle())
        data = loads(r.text)
        log("client.doUpload", data)
        return data["task_id"]


    def _checkStatus(self, taskid):
        r = self.session.get(self.host + "/api/scans/{}".format(taskid))
        dbg("client._checkStatus", r.text)
        data = loads(r.text)
        return data["status"]


    def waitUntilScanIsDone(self, taskid):
        while (status := self._checkStatus(taskid)) not in ["SUCCESS", "FAILURE", "REVOKED"]:
            log("client.waitUntilScanIsDone", "waiting..")
            sleep(1)
        return status

        
    def getScanResult(self, taskid):
        r = self.session.get(self.host + "/api/scans/{}/result".format(taskid))
        dbg("client.getScanResult", r.text)
        return r.text


    def runscan(self, path, uuid):
        self.repo = repo(path, uuid)
        self.repo.createTar()
        
        status = "FAILURE"
        try:
            uploadInfo = self.getUploadInfo()

            taskid = self.doUpload(uploadInfo)

            status = self.waitUntilScanIsDone(taskid)

        except Exception as e:
            dbg("client.runscan", "Got exception {} during scan".format(e))

        finally:
            self.repo.deleteTar()

        if status != "SUCCESS":
            log("client.runscan", "Could not run scan, check your parameters or API logs")
            return False, None

        else:
            data = loads(self.getScanResult(taskid))
            vulnerabilities = data["vulnerabilities"]
            count = 0
            for vuln in vulnerabilities:
                print(vuln['tool'], vuln['details'])
            log("client.runscan", "Result for scan ({} vulnerabilities were found):".format(count))
            tbl = PrettyTable()
            tbl.field_names = ["Level", "Count", "New Count"] 
            for level in ['ERROR', 'WARNING', 'NOTE', 'NONE']:
                tbl.add_row([level, data[level.lower()+"_count"], data["new_"+level.lower()+"_count"]])
            print(tbl)
            return True, data

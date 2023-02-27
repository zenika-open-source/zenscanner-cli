import tarfile
from os import remove, path, chdir, getcwd

class repo(object):
    def __init__(self, path, uuid):
        self.path = path
        self.uuid = uuid


    def createTar(self):
        self.tarname = "{}.tar.gz".format(self.uuid)
        tar = tarfile.open(self.tarname, "w:gz")
        current_dir = getcwd()
        chdir(path.dirname(self.path))
        tar.add(".")
        tar.close()
        chdir(current_dir)


    def getReadHandle(self):
        return open(self.tarname, "rb")


    def deleteTar(self):
        remove(self.tarname)


        

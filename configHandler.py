from os.path import exists, expanduser
from sys import path
from json import loads, dumps
from os import makedirs

class metaConfig:
    def __init__(self, **entries):
        self.__dict__.update(entries)


class configHandler(object):
    def __init__(self, configPath=None, configName=None):
        if not configPath:
            self.configPath = expanduser('~/.config/zenscannercli/')
        else:
            self.configPath = configPath

        if not configName:
            self.configName = "config.json"
        else:
            self.configName = configName

        self.fullPath = self.configPath + self.configName


    def doesConfigExists(self):
        if exists(self.fullPath):
            return True
        return False

    
    def createEmptyConfig(self):
        self.configRaw = "{}"
        self.config = metaConfig(**{})
        return self.config


    def getConfig(self):
        if self.doesConfigExists():
            with open(self.fullPath, 'rb') as fd:
                content = fd.read()

            try:
                self.configRaw = loads(content)
            except Exception as e:
                self.config = None
            else:
                self.config = metaConfig(**self.configRaw)
        else:
            self.config = None
        return self.config


    def putConfig(self):
        try:
            if not exists(self.fullPath):
                if not exists(self.configPath):
                    makedirs(self.configPath)
                    
            with open(self.fullPath, 'w') as fd:
                fd.write(dumps(self.config.__dict__))
            return True
        except Exception as e:
            raise
            return False

    

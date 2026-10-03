import pygame,os,json,ast,sys


class Configs():
    def __init__(self):

        self.loadedConfigs = {}
       
    # add a config json file
    def add_config(self,filePath:str):
        
        # the dict key will be the name of the config file without config_
        suffix = filePath.split('/')[-1].lstrip('config_').rstrip('.json')
        
        with open(filePath,'r') as config:
            self.loadedConfigs[suffix] = json.load(config)  
            
            
configData = Configs()
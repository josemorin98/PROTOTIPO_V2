from re import S


class NodeWorker():
    def __init__(self, *args, **kwargs):
        self.nodeId = kwargs.get('nodeId',None)
        self.ip = kwargs.get('ip','127.0.0.1')
        self.publicPort = kwargs.get('publicPort',5000)
        self.dockerPort = kwargs.get('dockerPort',5000)

    def getInfoNode(self):
        return 'nodeId = {} \nip = {} \npublicPort = {} \ndockerPort = {}'.format(self.nodeId,
                                            self.ip,
                                            self.publicPort,
                                            self.dockerPort)
    
    def getURL(self,mode='DOCKER'):
        if (mode=='DOCKER'):
            return 'http://{}:{}/workers'.format(self.nodeId,self.dockerPort)
        else:
            return 'http://{}:{}/workers'.format(self.ip,self.publicPort)
    
    def toJSON(self):
        return  {"nodeId"    : self.nodeId,
                "ip"         : self.ip,
                "publicPort" : self.publicPort,
                "dockerPort" : self.dockerPort}

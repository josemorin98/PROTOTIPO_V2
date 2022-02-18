from urllib3 import Retry


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

    def getURL(self,mode='DOCKER',endPoint='workers'):
        if (mode=='DOCKER'):
            return 'http://{}:{}/{}'.format(self.nodeId,self.dockerPort,endPoint)
        else:
            return 'http://{}:{}/{}'.format(self.ip,self.publicPort,endPoint)
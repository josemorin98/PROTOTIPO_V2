import configparser
import socket
import yaml


class NodeContainer():
    # Constructor de los nodos
    def __init__(self, hostname, image, context, 
                    dockerFile, volumes):
        self.hostname = hostname
        self.image = image
        self.volumes = self.volumesArray(volumes) # debde de ser un array
        # Si es falso no tiene contexto, es decir, la imagen estaa en docker hub
        if (context==False):
            self.context = False
        else:
            self.context = context
            self.dockerFile = dockerFile

    def volumesArray(self,volumes):
        # split de los volumenes
        jsonVolumes = {}
        jsonVolumes[volumes] = "/app/data/"
        jsonVolumes["{}/logs/".format(volumes)] = "/app/data/logs/"
        return jsonVolumes

    # Genrador de json paraa yml
    def toJSON(self,id, environment, network, ports):
        hostName = self.hostname+'_'+str(id)
        json_result = {
                'image': self.image,
                'hostname': hostName,
                'environment':environment,
                'volumes': self.volumes,
                'networks': [network],
                'ports': [ports]
            }

        if (self.context != False):
            json_result[hostName]['context'] = {'build':
                            {
                            'context': self.context,
                            'dockerfile': self.dockerFile }}
        return json_result

    def getHostname(self,id):
        return self.hostname+'_'+str(id)



def varEnvironment(vars):
    jsonResult = {}
    jsonAux = {}
    for key in vars:
        jsonAux[key.upper()] = vars[key]
    jsonResult= jsonAux
    return jsonResult

def freePort( port=1024, max_port=65535,setPorts=set({})):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    while port <= max_port:
        try:
            if (setPorts.__contains__(port)):   
                port += 1
            else:
                sock.bind(('', port))
                sock.close()
                return port
        except OSError:
            port += 1
    raise IOError('NO FREE PORTS')

def cantNodes(nodeUsr):
    if (nodeUsr.__contains__('WORKERS')):
        return int(nodeUsr['WORKERS'])
    else:
        return 1

def getNodes(cant,listNodes):
    nodesDes = list()
    for node in range(int(cant)):
        nodesDes.append(listNodes.pop(0))
    return listNodes,",".join(nodesDes)

# configuracion del parser
config = configparser.ConfigParser(strict=False)
# config.read('config.txt')
print('READ MODULES ... ')
# leemos los modulos
config.read('./modulos.ini')
print('SAVED MODULES ... ')
# Modulos disponibles
modulos = config
modulos_names = config.sections()
# leemos las declaraciones
print('READ DECLARATIVES ... ')
# Cremos los objetos
listModules = {}
for modulo in modulos_names:
    # create object
    mod = modulos[modulo]
    if (mod.__contains__('context')):
        listModules[modulo] = NodeContainer(hostname = mod['hostname'],
                                            image=mod['image'],
                                            context=mod['context'], 
                                            dockerFile=mod['dockerfile'],
                                            volumes=mod['volumes'])
    else:
        listModules[modulo] = NodeContainer(hostname = mod['hostname'],
                                            image=mod['image'],
                                            context=False, dockerFile='',
                                            volumes=mod['volumes'])

print(len(listModules))
# leemos las delcarativas del usuario
print('READ DECLARATIVES ... ')
declarativesConfig = configparser.ConfigParser(strict=False)
declarativesConfig.read('./declaratives.ini')

listServices = {}
worker_service = 1
setServicesDes = {}
setPorts = set({})
for container in declarativesConfig.sections():
    # verificamos si el contenedor existe en el catalogo
    nodeUsr = declarativesConfig[container] # node config user
    modul = listModules[container] # node preconfig

    # worker_service = cantNodes(nodeUsr=nodeUsr)

    if (container in modulos_names):
        
        # si el usuario pide n
        cantNodesDes = worker_service * cantNodes(nodeUsr=nodeUsr)
        print('cantNodesDes=',cantNodesDes)
        nameNode = nodeUsr['NODES']
        setServicesDes = [listModules[nameNode].getHostname(x) for x in range(cantNodesDes)]
        print(setServicesDes)

        for work in range (worker_service):
            # toJSON(self,id, environment, network, ports):
            # nombre de los contenedores destino
            setServicesDes, nodeUsr['NODES'] = getNodes(cantNodes(nodeUsr=nodeUsr),setServicesDes)
            environment = varEnvironment(nodeUsr)
            port = freePort(setPorts=setPorts)
            ports = str(port)+':5000'
            setPorts.add(port)
            listServices[modul.getHostname(work)] = modul.toJSON(id=work, environment=environment,
                            network='prot_net', ports=ports)
        worker_service = cantNodesDes
    else:
        print('Module not found'.upper)

net ={}
net['prot_net'] = None
endJson = {'version':'3',
                'services': listServices,
                'networks':net}
print('Yaml')
ymlFile = yaml.dump(endJson, sort_keys=False)
print(ymlFile)
f = open("docker-compose.yml", "w")
f.write(ymlFile)
f.close()


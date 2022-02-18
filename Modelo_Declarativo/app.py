import configparser        

def create_microservice(usr,precon,wrk,workers):
    # nombre de la imagen
    compose  = "    image: "+precon['image']+'\n'
    compose += "    enviroment:\n"
    
    compose += "    build:\n"
    compose += "      context: "+ precon['context']+"\n"
    compose += "      dockerfile: "+ precon['dockerfile']+"\n"
    compose += "    volumes:\n      - "+ precon['volumes']+"\n"
    compose += "    networks:\n      - prot_net\n"
    compose += "    ports:\n      - "+ str(int(usr['PORT'])+wrk)+":5000"+"\n"
    if (workers == False):
        compose += "    command: " + precon['command'] + ' ' + usr['ip'] + ' ' + usr['destination']
    elif (workers == True):
        compose += "    command: " +  precon['command'] + ' ' + str(usr['WORKERS']) + ' ' + usr['ip'] + ' ' + usr['destination']
    return compose


# configuramoes el parser
config = configparser.ConfigParser(strict=False)
# config.read('config.txt')
print('READ MODULES ... ')
# leemos los modulos
config.read('./modulos.ini')
print('SAVED MODULES ... ')
docker_compose = "version: '3'\n"
docker_compose += "services:\n\n"
# Modulos disponibles
modulos = config
modulos_names = config.sections()
# leemos las declaraciones
print('READ DECLARATIVES ... ')
config2 = configparser.ConfigParser(strict=False)
config2.read('./declaratives.ini')

workers = 1
for container in config2.sections():
    print(' - ' +container)
    # saber si se encuentra en los modlulos registrados
    if (container in modulos_names):
        # si se encuentra leera los apartados de container y de modulos
        # nombre del contenedor
        for wrk in range(workers):
            # Colocamos el nombre
            if(workers==1):
                docker_compose += "  "+modulos[container]['name'] + ':\n'
            else:
                docker_compose += "  "+modulos[container]['name'] +'_' +str(wrk) +':\n'
            # Generamos la estructura del container            
            if (container == 'FUENTES'):
                docker_compose += create_microservice(usr=config2[container],
                                                precon=modulos[container],
                                                wrk=wrk, workers=False)
            else:
                docker_compose += create_microservice(usr=config2[container],
                                                precon=modulos[container],
                                                wrk=wrk, workers=True)
            docker_compose += '\n\n'
        # verificamos si contiene trabajadores
        if ('workers' in config2[container]):
            # guardamos el numero de trabajadores
            workers = int(config2[container]['WORKERS'])
        else:
            workers=1
    else:
        print('MODULO NO ENCONTRADO')
docker_compose+="networks:\n  prot_net:\n"
# print(docker_compose)
f = open("docker-compose.yml", "w")
f.write(docker_compose)
f.close()

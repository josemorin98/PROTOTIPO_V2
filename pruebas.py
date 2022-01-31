# import logging

# FORMAT = '%(created).0f %(levelname)s %(message)s'
# formatter = logging.Formatter(FORMAT)
# logging.basicConfig(format=FORMAT, filename='./Volumen/prueba.csv', level=logging.INFO, filemode='w')

# console = logging.StreamHandler()
# console.setLevel(logging.INFO)
# console.setFormatter(fmt=formatter)
# # add the handler to the root logger
# logging.getLogger().addHandler(console)
# logging.info('time levelname opertion type')

import pandas as pd 
import loadBalanceGeneric.methods as mtd

df = pd.read_csv('test.csv', index_col=False)

# espacial no porque ya tiene una columna
df = df.set_index(['Espacial','Temporal'])

# get all items in index
indexlist = df.index.get_level_values('Espacial').tolist()

algorithm = ['RR','TC','PR']
worker = 3
# hacemos el round roubin
for algo in algorithm:
    # inicializamos las cajas de balanaceo
    initWorkers = mtd.init_workres(workers=worker)
    if (algo == 'RR'):
        # ROund Robin
        balanceData = mtd.RaoundRobinV2(cargas=initWorkers, traza=indexlist)

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

df = pd.read_csv('test.csv')
print(df)

# espacial no porque ya tiene una columna
df.set_index('Espacial')
df.set_index('Temporal')
print(df)



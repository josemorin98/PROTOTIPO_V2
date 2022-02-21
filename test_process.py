from enum import unique
from sklearn.linear_model import LinearRegression
import pandas as pd
import datetime

# df = pd.read_csv("/test/files/rezago/IRS_mpios_2000.csv")
df = pd.read_csv("/test/prototipoTest/TasaD_pre.csv")

# datetime.strptime(aux[x], '%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])


# df['cause'] = pd.to_datetime(df["anio_ocur"],format='%Y')
# df['anio_ocur'] = df['anio_ocur'].dt.strftime('%Y-%m-%d %H:%M:%S')
# print(df['anio_ocur'])
# df.to_csv("./TasaD_preV2.csv",index=False)
uniqueV = df['causasuic'].unique()
print(uniqueV)
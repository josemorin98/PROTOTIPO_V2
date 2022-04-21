from statistics import mean
import pandas as pd
import numpy as np
df = pd.read_csv("./suic_new/Suic_Medio_Derhab_tasasporsexo.csv")
df_global = pd.read_csv("./suic_new/deb3fd6e-1512-42d5-96c6-d5db8bfbe62e_Data.csv")

Mexico = df_global.loc[df_global["Country Name"]=="México"].transpose()
Mexico["anio"] = Mexico.index
Mexico=Mexico[2:]
Mexico = Mexico.replace("..",None)
Mexico["anio"] =Mexico["anio"].astype(int)
print(Mexico)
df_mergeMex = df.merge(Mexico, how="inner", left_on=["anio"], right_on=["anio"])
df_mergeMex.to_csv("mergeGlobal.csv", index=False)

anios=list()
for x in range(2000,2021):
    anios.append(str(x))

# df_concatMex = pd.concat([df,Mexico],axis=1)
df_global[anios] = df_global[anios].replace("..",np.nan)
print(df_global)
menasGloal=df_global[anios].astype(float).mean().to_frame("Referencia_Mundial")
menasGloal["anio"] = menasGloal.index.astype(int)
df_global = df_mergeMex.merge(menasGloal, how="inner", left_on=["anio"], right_on=["anio"])
df_global.to_csv("defuncionesReferencias.csv",index=False)  
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def corr(corr,nameSource):
    f, ax = plt.subplots(figsize=(15, 9))
    ax = sns.heatmap(corr, linewidths=.5, vmin=-1, vmax=1, cbar_kws={'label': 'CORRELATION'})
    plt.title('CORRELATION \n {}'.format(nameSource))
    plt.savefig(nameSource)
    plt.cla()
    plt.close()

# Fuente OH
OH = pd.read_csv("./Defunciones_Set_OH.csv")
suic = pd.read_csv("./Defunciones_Set_suic.csv")

columnsOH = list(OH.columns)
columnsOH.remove("NOMGEO")

# cve_ent_mun
# anio_regis
# Normalizar los dataset
# scaler = StandardScaler()
# OH.merge()
result = OH.merge(suic, how="inner", left_on=["cve_ent_mun","anio_regis"], right_on=["cve_ent_mun","anio_regis"])
result.to_csv("result.csv", index=False)
print(suic.shape)
print(OH.shape)
print(list(result.columns))
# corr(corrOH,"SET OH-suic")

# cronograma de activadedes mi firma, doctora Martha, tutore VOBO
# comision
# solictud de apoyo
# YO - generar un oficio


# carta de invitacion - la genera la doc martha
from itertools import count
from matplotlib import pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

def corr(corr,nameSource):
    f, ax = plt.subplots(figsize=(15, 9))
    ax = sns.heatmap(corr, linewidths=.5, vmin=0, vmax=1, cbar_kws={'label': 'CORRELATION'})
    plt.title('CORRELATION \n {}'.format(nameSource))
    plt.savefig("./suic_new/{}".format(nameSource))
    plt.cla()
    plt.close()

# Fuente OH
suic = pd.read_csv("./suic_new/Suic_Medio_Derhab_tasasporsexo.csv")
ecnomi = pd.read_csv("./suic_new/Variables Macroeconomicas.csv")
suic = suic.fillna(0)
columnsSuic = list(suic.columns)
# print(columnsSuic)
# cve_ent_mun
# anio_regis
# Normalizar los dataset
# scaler = StandardScaler()
# OH.merge()
columns = ['suicAhogamiento', 'suicAhorcamiento', 'suicArma_fuego', 'suicEnvenenamiento', 'suicOtro', 'suicderhabNE', 'suicSinDerhab', 'suicDerehab', 'suic10_14', 'suic15_19', 'suic20_24', 'suic25_29', 'suic30_34', 'suic35_39', 'suic40_44', 'suic45_49', 'suic50_54', 'suic55_59', 'suic5_9', 'suic60_64', 'suicNE_NA', 'pob_00_04', 'pob_05_09', 'pob_10_14', 'pob_15_19', 'pob_20_24', 'pob_25_29', 'pob_30_34', 'pob_35_39', 'pob_40_44', 'pob_45_49', 'pob_50_54', 'pob_55_59', 'pob_60_64', 'pob_65_mm', 'cve_ent', 'cve_mun', 'tasa_suic5_9', 'tasa_suic10_14', 'tasa_suic15_19', 'tasa_suic20_24', 'tasa_suic25_29', 'tasa_suic30_34', 'tasa_suic35_39', 'tasa_suic40_44', 'tasa_suic45_49', 'tasa_suic50_54', 'tasa_suic55_59', 'tasa_suic60_64', 'suic65_mas', 'tasa_suic65_mas', 'tot_pob', 'total_suic', 'tasa_suic']

result = suic.merge(ecnomi, how="inner", left_on=["cve_ent_mun"], right_on=["cve_ent_mun"])
result.to_csv("merge.csv", index=False)

print(suic.shape)
print(ecnomi.shape)
print(result.shape)
resultColumns = set(result.columns)
print(len(resultColumns))
countL = 0

corrs = result.corr()
corrs = corrs[columns]
corrs = corrs.drop(columns, axis=0)

# print(len(corrs.index),len(corrs.columns))  
corr(corrs,"prueba")
# for column in columns:
#     countL = countL + 1
#     print("{} - {}".format(countL, column))
#     only = set([column])
#     # print(only)
#     setColumns = set(columns).difference(only)
#     # print(len(setColumns))
#     selectColumns = resultColumns.difference(setColumns)
#     # print(len(selectColumns))
#     corrs = result[list(selectColumns)].corr()
#     corr(corrs,"Suicidios (X) - Macroeconomicas (Y) --- {}".format(list(only)[0]))  
    # break
    
# resultCor = result.corr()
# corr(resultCor,"Suicidios (X) - Macroeconomicas (Y)")



# cronograma de activadedes mi firma, doctora Martha, tutore VOBO
# comision
# solictud de apoyo
# YO - generar un oficio


# carta de invitacion - la genera la doc martha
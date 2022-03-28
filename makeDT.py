import pandas as pd
import time

def conteo(nameSource,conteoData,conteoVariables,grupoBY,group_by):
    arrivalTime = time.time()
    try:
        # loggerError.error("------------------------------ FLAG 2.1")
        DF_data = conteoData
        columns = DF_data.columns
        # variables para el conteo
        variables = list(conteoVariables)
        # varaible a agrupar / clave entidad
        group_columns = grupoBY
        query_str = "CVE_ENT"
        # --------------------------------
        columns= set(columns) - set(variables) #remove columns that are going to be group
        columns= set(columns) - set(group_columns) 
        applied_dict=dict()
        # loggerError.error("------------------------------ FLAG 2.2 {}".format(columns))
        for x in columns:
            applied_dict[x]="first"
        for x in variables:
            applied_dict[x]=group_by

        #print(DF_data)
        if (group_by == "count"):
            DF_data=DF_data[group_columns]
            DF_data['count'] = 0
            DF_data = DF_data.groupby(group_columns,as_index=False)['count'].count()
        else:
            DF_data = DF_data.groupby(group_columns,as_index=False).agg(applied_dict)
        # ==============================================================
        if query_str != "":
            try:
                DF_data = DF_data.query(query_str)
            except Exception as e:
                print(e)

        nameFile = "./{}_COUNT.csv".format(nameSource)
        
        DF_data.to_csv(nameFile,index=False)
        endTime = time.time()
        counttime = endTime-arrivalTime
        print("---------------------------- Select {}".format(counttime))
        return 1
    except Exception as e:
        print(e)
        return 0

sources = ["def_2000_2019_fin.csv","z_class_2019.csv"]

# lectura
initRead = time.time()
df = pd.read_csv('./{}'.format(sources[0]))
endRead = time.time()
readTime = endRead - initRead
print("---------------------------- Lectura {}".format(readTime))

# group by
initBy = time.time()
df = df.groupby(['anio_regis'])
endBy = time.time()
groupBy = endBy-initBy
print("---------------------------- GroupBy {}".format(groupBy))

# select 2019
initSelect =time.time()
df_2019 = df.get_group(2019)
endSelect = time.time()
selectTime = endSelect-initSelect
print("---------------------------- Select {}".format(selectTime))
df_2019.to_csv("2019_.csv",index=False)
dF_2019 = pd.read_csv("./2019_.csv")
end2019 = time.time()
time2019 =end2019- endSelect
print("---------------------------- 2019 {}".format(time2019))
# conteo
resp = conteo(nameSource="2019", conteoData=dF_2019, conteoVariables=["ent_regis"], grupoBY=["ent_regis"], group_by="count")
print("---------------------------- Count {}".format(resp))

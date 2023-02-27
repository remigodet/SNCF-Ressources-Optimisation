from gurobipy import *
import data


taches_df = data.taches_df
chantiers_df = data.chantiers_df
machines_df = data.machines_df
sillons_ds = data.sillons_df
correspondances_df = data.correspondances_df

machines_dico = {"Débranchement" : 0,
                 "Formation" : 1,
                 "Dégarage" : 2}



dico = { _ : { _ : _}}
m = Model("GARE WPY")

##### Anti-Parallélisme des tâches machines #####

for machine in dico.keys():
    for sillon_i in dico[machine].keys():
        for sillon_j in dico[machine].keys():
            m.addConstr(dico[machine][sillon_i] - dico[machine][sillon_j] >= machines_df.iloc[machines_dico[machine]]["Duree"])


##### Respect des créneaux #####

for machine in dico.keys():
    for sillon in dico[machine].keys():
        m.addConstr(dico[machine][sillon] % machines_df.iloc[machines_dico[machine]]["Duree"] == 0)

##### Indisponibilités #####

indisp_dico = {}
for machine in dico.keys():
    strTot = machines_df.iloc[machines_dico[machine]]["Indisponibilites"]
    strBis = strTot.split(";")
    strTer = []
    for str in strBis:
        str1, str2 = str[1:-1].split(", ")
        strTer.append((str1, str2))
    strQuad = []
    for (strA, strB) in strTer:
        str3, str4 = strB.split("-")
        strQuad.append(strA, str3, str4)

    strQuint = []
    for (strA, strC, strD) in strQuad:
        strC1, strC2 = strC.split(":")
        strC3 = int(strC1)*60 + int(strC2)
        strD1, strD2 = strD.split(":")
        strD3 = int(strD1)*60 + int(strD2)
        strQuint.append(int(strA), strC3, strD3)

    indispList = []
    for (a, b, c) in strQuint:
        debut = a*60*24 + b
        if c<=b:
            fin = (a+1)*60*24 + c
        else:
            fin  = a*60*24 + c

        indispList.append((debut, fin))

    indisp_dico[machine] = indispList


    


for machine in dico.keys():
    for sillon in dico[machine].keys():
        for indispTuple in indisp_dico[machine]:
            debut = dico[machine][sillon]
            fin = debut + machines_df.iloc[machines_dico[machine]]["Duree"]
            m.addConstr((debut<=indispTuple[0] and fin<=indispTuple[0]) or (debut>=indispTuple[1] and fin>=indispTuple[1]))




        


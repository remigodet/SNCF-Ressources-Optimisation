from gurobipy import *
import data

def generate_contraintes(m, dataframes, dico):
    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]

    machines_dico = {"DEB" : 0,
                 "FOR" : 1,
                 "DEG" : 2}

    ##### helper funcs
    M = 1000000
    def add_constr_abs_sup(m,t2, t1, d):
        '''
        Adds a constraints to model m equal to representing |t2-t1|>=d.
        '''
        v = m.addVar(vtype = GRB.BINARY, name = f'helper var')
        m.addConstr((v==1)>>(t2-t1<=0)) # pas necessaire
        m.addConstr(t2-t1>=d-M*v)
        m.addConstr(t2-t1<=-d+M*(1-v))
        
    ##### Anti-Parallélisme des tâches machines #####
    anti_parallel_constrs = []
    for machine in machines_dico.keys(): #3
        for sillon_i in dico[machine].keys(): # 
            for sillon_j in dico[machine].keys():
                if sillon_i!=sillon_j:
                    # print(sillon_i, sillon_j)
                    add_constr_abs_sup(m, dico[machine][sillon_i], dico[machine][sillon_j], machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] <= dico[machine][sillon_j]) >>((dico[machine][sillon_j] - dico[machine][sillon_i]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] >= dico[machine][sillon_j]) >>((dico[machine][sillon_i] - dico[machine][sillon_j]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] - dico[machine][sillon_j] <= -machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
    
    print("Number of anti-parallel constraints : ", len(anti_parallel_constrs))
    
    ##### Respect des créneaux #####

    # for machine in machines_dico.keys():
    #     for sillon in dico[machine].keys():
    #         m.addConstr(dico[machine][sillon] % machines_df["Duree "].iloc[machines_dico[machine]] == 0)

    ##### Indisponibilités #####

    # indisp_dico = {}
    # for machine in machines_dico.keys():
    #     strTot = machines_df["Indisponibilites"].iloc[machines_dico[machine]]
    #     if strTot!=0:
    #         strBis = strTot.split(";")
    #         strTer = []
    #         for str in strBis:
    #             print(str[1:-1].split(","))
    #             [str1, str2] = str[1:-1].split(", ")
    #             strTer.append((str1, str2))
    #         strQuad = []
    #         for (strA, strB) in strTer:
    #             [str3, str4] = strB.split("-")
    #             strQuad.append(strA, str3, str4)

    #         strQuint = []
    #         for (strA, strC, strD) in strQuad:
    #             [strC1, strC2] = strC.split(":")
    #             strC3 = int(strC1)*60 + int(strC2)
    #             [strD1, strD2] = strD.split(":")
    #             strD3 = int(strD1)*60 + int(strD2)
    #             strQuint.append(int(strA), strC3, strD3)

    #         indispList = []
    #         for (a, b, c) in strQuint:
    #             debut = a*60*24 + b
    #             if c<=b:
    #                 fin = (a+1)*60*24 + c
    #             else:
    #                 fin  = a*60*24 + c

    #             indispList.append((debut, fin))

    #         indisp_dico[machine] = indispList

    # for machine in machines_dico.keys():
    #     for sillon in dico[machine].keys():
    #         for indispTuple in indisp_dico[machine]:
    #             debut = dico[machine][sillon]
    #             fin = debut + machines_df["Duree "].iloc[machines_dico[machine]]
    #             m.addConstr((debut<=indispTuple[0] and fin<=indispTuple[0]) or (debut>=indispTuple[1] and fin>=indispTuple[1]))

    ##### Antécedents #####
    ##### Wagons tous présent avant assemblage du sillon #####
    ##### taches humaines (chaines et debut synchro avec les taches machines) #####
    ##### Heure de depart du train respectée #####
    ##### heure d'arrivée du train respectée  #####
    ##### Indisponibilités ##### 
    ##### Respect du nombre de voies de chantier #####



    






    




            

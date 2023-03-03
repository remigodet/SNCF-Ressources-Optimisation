from gurobipy import *
import data
from tqdm import tqdm


def generate_contraintes(m, dataframes, var_dict):
    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]
    chantiers_df = dataframes["chantiers_df"]

    machines_dico = {"DEB": 0,
                     "FOR": 1,
                     "DEG": 2}

    # helper funcs
    M = 1000000

    def add_constr_abs_sup(m, t2, t1, d):
        '''
        Adds a constraints to model m equal to representing |t2-t1|>=d.
        '''
        v = m.addVar(vtype=GRB.BINARY, name=f'helper var')
        m.addConstr((v == 1) >> (t2-t1 <= 0))  # pas necessaire
        m.addConstr(t2-t1 >= d-M*v)
        m.addConstr(t2-t1 <= -d+M*(1-v))

    ##### Anti-Parallélisme des tâches machines #####
    # anti_parallel_constrs = []
    # for machine in machines_dico.keys():  # 3
    #     for sillon_i in dico[machine].keys():
    #         for sillon_j in dico[machine].keys():
    #             if sillon_i != sillon_j:
    #                 # print(sillon_i, sillon_j)
    #                 add_constr_abs_sup(m, dico[machine][sillon_i], dico[machine][sillon_j],

        #    machines_df[machines_df["Machine"] == machine]["Duree "].iloc[0])
    #                 # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] <= dico[machine][sillon_j]) >>((dico[machine][sillon_j] - dico[machine][sillon_i]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
    #                 # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] >= dico[machine][sillon_j]) >>((dico[machine][sillon_i] - dico[machine][sillon_j]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
    #                 # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] - dico[machine][sillon_j] <= -machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))

    # print("Number of anti-parallel constraints : ", len(anti_parallel_constrs))

    ##### Respect des créneaux #####

    # for machine in machines_dico.keys():
    #     for sillon in dico[machine].keys():
    #         m.addConstr(dico[machine][sillon] % machines_df["Duree "].iloc[machines_dico[machine]] == 0)


##### Indisponibilités #####

    indisp_dico = {}
    for machine in list(machines_df["Machine"]):
        strTot = machines_df[machines_df["Machine"]
                            == machine]["Indisponibilites"].iloc[0]
        if strTot != "0":
            strBis = strTot.split(";")
            strTer = []
            for str in strBis:
                split = str[1:-1].split(",")
                [str1, str2] = split
                strTer.append((str1, str2))
            strQuad = []
            for (strA, strB) in strTer:
                [str3, str4] = strB.split("-")
                strQuad.append((strA, str3, str4))

            strQuint = []
            for (strA, strC, strD) in strQuad:
                [strC1, strC2] = strC.split(":")
                strC3 = int(strC1)*60 + int(strC2)
                [strD1, strD2] = strD.split(":")
                strD3 = int(strD1)*60 + int(strD2)
                strQuint.append((int(strA), strC3, strD3))

            indispList = []
            for (a, b, c) in strQuint:
                debut = (a-1)*60*24 + b
                if c <= b:
                    fin = a*60*24 + c
                else:
                    fin = (a-1)*60*24 + c

                indispList.append((debut, fin))

            indisp_dico[machine] = indispList

    # for machine in machines_dico.keys():
    #     for sillon in dico[machine].keys():
    #         for indispTuple in indisp_dico[machine]:
    #             debut = dico[machine][sillon]
    #             fin = debut + machines_df["Duree "].iloc[machines_dico[machine]]
    #             m.addConstr((debut<=indispTuple[0] and fin<=indispTuple[0]) or (debut>=indispTuple[1] and fin>=indispTuple[1]))

    ##### Antécedents #####
    temp = []
    for tache in var_dict.keys():
        for sillon in var_dict[tache].keys():
            # on ne teste que les taches humaines
            if tache in list(taches_df["Type de tache humaine"]):
                ordre = taches_df[taches_df["Type de tache humaine"]
                                  == tache]["Ordre"].iloc[0]  # on stocke l'ordre de la tache
                type_train = taches_df[taches_df["Type de tache humaine"]
                                       == tache]["Type de train"].iloc[0]  # on stocke le type de train pour faire matcher plus tard avec celui de la tache precedante
                if ordre > 1:
                    tache_precedante = taches_df[taches_df["Ordre"] == ordre -
                                                 1][taches_df["Type de train"] == type_train]["Type de tache humaine"].iloc[0]
                    temp.append(m.addConstr(var_dict[tache][sillon] == var_dict[tache_precedante][sillon] +
                                taches_df[taches_df["Type de tache humaine"] == tache_precedante]["Durée"].iloc[0]))  # == car on les enchaîne sinon >=
    # print(len(temp))
    ##### Wagons tous présent avant assemblage du sillon #####

    ##### taches humaines (chaines et debut synchro avec les taches machines) #####

    for tache in var_dict.keys():
        for sillon in var_dict[tache].keys():
            ## Débranchement ##
            if tache == "Débranchement":
                tache_collee = taches_df[taches_df["Lien machine"]
                                        == "DEB="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])
                ## Dégarage ##
            elif tache == "Dégarage":
                tache_collee = taches_df[taches_df["Lien machine"]
                                        == "DEG="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])
                ## Formation ##
            elif tache == "Formation":
                tache_collee = taches_df[taches_df["Lien machine"]
                                        == "FOR="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])

    ##### Heure de depart du train respectée #####
    ##### heure d'arrivée du train respectée  #####
    ##### Indisponibilités #####
    ##### Respect du nombre de voies de chantier #####
    chantier_cycles = {}
    for chantier in set(taches_df["Chantier"].values):
        chantier_cycles[chantier, "start"] = taches_df[taches_df["Chantier"] == chantier][taches_df.Ordre ==
                                                                                          taches_df[taches_df["Chantier"] == chantier].Ordre.max()]["Type de tache humaine"].iloc[0]
        chantier_cycles[chantier, "end"] = taches_df[taches_df["Chantier"] == chantier][taches_df.Ordre ==
                                                                                        taches_df[taches_df["Chantier"] == chantier].Ordre.min()]["Type de tache humaine"].iloc[0]

    def get_all_tasks_by_name(name):
        return var_dict[name].values()

    def add_occupation_constr(chantier, tache_debut):
        def b(minute_i, minute_j):
            b = m.addVar(vtype=GRB.BINARY, name="helper")
            m.addConstr((b == 1) >> (minute_i <= minute_j),
                        name="indicator_constr1")
            m.addConstr((b == 0) >> (minute_i >= minute_j + 0.5),
                        name="indicator_constr2")
            return b

        occupation = quicksum([b(minute_i=tache_chantier, minute_j=tache_debut)
                               for tache_chantier in get_all_tasks_by_name(chantier_cycles[chantier, "start"])])
        duree = taches_df[taches_df["Type de tache humaine"]
                          == chantier_cycles[chantier, "end"]]["Durée"].iloc[0]
        occupation = occupation - quicksum([b(minute_i=tache_chantier+duree,
                                              minute_j=tache_debut)
                                            for tache_chantier in get_all_tasks_by_name(chantier_cycles[chantier, "end"])])
    for chantier in set(chantiers_df["Chantier"].values):
        print(f"Adding occupation constrainst for: {chantier}...")
        for tache_debut in get_all_tasks_by_name(chantier_cycles[chantier, "start"]):
            add_occupation_constr(chantier, tache_debut)

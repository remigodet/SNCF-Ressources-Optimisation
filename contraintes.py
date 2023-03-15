from gurobipy import *
import data
import utils
from tqdm import tqdm


def generate_contraintes(m, dataframes, var_dict):

    #tqdm 
    NB_CONTRAINTES = 8
    p_bar = tqdm(range(NB_CONTRAINTES), desc="BUILDING CONSTRAINTS")


    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]
    chantiers_df = dataframes["chantiers_df"]
    sillons_df = dataframes["sillons_df"]
    correspondances_df = dataframes["correspondances_df"]

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
    for machine in machines_df["Machine"]:  # 3
        for sillon_i in var_dict[machine].keys():
            for sillon_j in var_dict[machine].keys():
                if sillon_i != sillon_j:
                    add_constr_abs_sup(m, var_dict[machine][sillon_i], var_dict[machine][sillon_j],

           machines_df[machines_df["Machine"] == machine]["Duree "].iloc[0])
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] <= dico[machine][sillon_j]) >>((dico[machine][sillon_j] - dico[machine][sillon_i]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] >= dico[machine][sillon_j]) >>((dico[machine][sillon_i] - dico[machine][sillon_j]) >= machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))
                    # anti_parallel_constrs.append(m.addConstr((dico[machine][sillon_i] - dico[machine][sillon_j] <= -machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0])))

    # print("Number of anti-parallel constraints : ", len(anti_parallel_constrs))
    p_bar.update(1)
    p_bar.refresh()
    #### Respect des créneaux #####
    for machine in ["DEB", "FOR", "DEG"]: #ALL MACHINES
        duree = machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0]
        i = 0
        for sillon in var_dict[machine].keys():
            i += 1
            m.addConstr(var_dict[machine][sillon] == m.addVar(vtype = GRB.INTEGER, name=f"helper-creneau-{machine}-{sillon}") * duree)
    # for machine in ["DEB","FOR","DEG"]: # DEBUG 
        # duree = machines_df[machines_df["Machine"]==machine]["Duree "].iloc[0]
        # i = 0
        # for sillon in var_dict[machine].keys():
        #     i += 1
            
        #     if machine in  ["DEB"]:
        #         m.addConstr(var_dict[machine][sillon] == m.addVar(vtype = GRB.INTEGER, name=f"helper-creneau-{machine}-{sillon}") * duree)
        #     elif machine=="DEG" and i <= 35:
        #         print(sillon)
        #         m.addConstr(var_dict[machine][sillon] == m.addVar(vtype = GRB.INTEGER, name=f"helper-creneau-{machine}-{sillon}") * duree)
        #     else:
        #         pass
    p_bar.update(1)
    p_bar.refresh()
    ##### Indisponibilités #####

    mach_indisp_dico = {}
    for machine in list(machines_df["Machine"]):
        strTot = machines_df[machines_df["Machine"]
                             == machine]["Indisponibilites"].iloc[0]
        if strTot != 0:
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

            mach_indisp_dico[machine] = indispList

    chan_indisp_dico = {}
    for chantier in list(chantiers_df["Chantier"]):
        strTot = chantiers_df[chantiers_df["Chantier"]
                              == chantier]["Indisponibilites"].iloc[0]
        if strTot != 0:
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

            chan_indisp_dico[chantier] = indispList

    def no_overlap_indisp(x1, x2, t1, t2, m):
        A = m.addVar(vtype=GRB.INTEGER, ub=1, lb=0)
        M = 2000000
        m.addConstr(M*A+x1-x2-t2 >= 0)
        m.addConstr(M*(1-A)+x2-x1 - t1 >= 0)

    def indisponnibilites(m):
        machine_lenght = {'DEB': 20, 'FOR': 15, 'DEG': 15}
        tache_chantier = {'WPY_REC': ['arrivée Reception', 'préparation tri', 'débranchement'],
                          'WPY_FOR': ['appui voie + mise en place câle', 'attelage véhicules'],
                          'WPY_DEP': ['dégarage / bouger de rame', 'essai de frein départ']}
        humaine_lenght = {'arrivée Reception': 15, 'préparation tri': 45, 'débranchement': 20,
                          'appui voie + mise en place câle': 15, 'attelage véhicules': 149,
                          'dégarage / bouger de rame': 15, 'essai de frein départ': 20}

        for machine in mach_indisp_dico.keys():
            for indisp in mach_indisp_dico[machine]:
                for tache in var_dict[machine]:
                    x1 = var_dict[machine][tache]
                    t1 = machine_lenght[machine]
                    x2 = indisp[0]
                    t2 = indisp[1]-indisp[0]
                    # print(x1, x2, t1, t2)
                    no_overlap_indisp(x1, x2, t1, t2, m)

        for chantier in chan_indisp_dico.keys():
            for indisp in chan_indisp_dico[chantier]:
                for type_de_tache in tache_chantier[chantier]:
                    for tache in var_dict[type_de_tache]:
                        x1 = var_dict[type_de_tache][tache]
                        t1 = humaine_lenght[type_de_tache]
                        x2 = indisp[0]
                        t2 = indisp[1]-indisp[0]
                        no_overlap_indisp(x1, x2, t1, t2, m)
    indisponnibilites(m)

    p_bar.update(1)
    p_bar.refresh()
            
        

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
                    temp.append(m.addConstr(var_dict[tache][sillon] >= var_dict[tache_precedante][sillon] +
                                taches_df[taches_df["Type de tache humaine"] == tache_precedante]["Durée"].iloc[0]))  # == car on les enchaîne sinon >=
    # print(len(temp))
    p_bar.update(1)
    p_bar.refresh()
    ##### Wagons tous présent avant assemblage du sillon #####
    for sillon in var_dict["FOR"].keys():
        list_wagons = list(correspondances_df[correspondances_df["train_id"] ==
                                              sillon][correspondances_df["LDEP"] == "WPY"]["id_wagon"])
        for wagon in list_wagons:
            sillon_arr = correspondances_df[correspondances_df["id_wagon"] ==
                                            wagon][correspondances_df["LARR"] == "WPY"]["train_id"].iloc[0]
            m.addConstr(var_dict["DEB"][sillon_arr] + machines_df[machines_df["Machine"]
                       == "DEB"]["Duree "] <= var_dict["FOR"][sillon])
    p_bar.update(1)
    p_bar.refresh()
    ##### Taches humaines (chaines et debut synchro avec les taches machines) #####

    for tache in var_dict.keys():
        for sillon in var_dict[tache].keys():
            ## Débranchement ##
            if tache == "DEB":
                tache_collee = taches_df[taches_df["Lien machine"]
                                         == "DEB="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])
                ## Dégarage ##
            elif tache == "DEG":
                tache_collee = taches_df[taches_df["Lien machine"]
                                         == "DEG="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])
                ## Formation ##
            elif tache == "FOR":
                tache_collee = taches_df[taches_df["Lien machine"]
                                         == "FOR="]["Type de tache humaine"].iloc[0]
                # on colle la tache machine a la tache humaine en parallele
                m.addConstr(var_dict[tache][sillon] ==
                            var_dict[tache_collee][sillon])
    p_bar.update(1)
    p_bar.refresh()
    #### Horaires respectés #### 
    compteur = 0
    
    for sillon in var_dict["essai de frein départ"].keys():
        ##### Heure de depart du train respectée #####
        LDEP = sillons_df[sillons_df["train_id"] == sillon]["LDEP"].iloc[0]
        LARR = sillons_df[sillons_df["train_id"] == sillon]["LARR"].iloc[0]
        if LDEP in ["WPY_DEP", "WPY"]:
            compteur += 1
            jour = sillons_df[sillons_df["train_id"]
                                == sillon]["JDEP"].iloc[0]
            jour = jour[0:2]
            str = sillons_df[sillons_df["train_id"]
                                == sillon]["HDEP"].iloc[0]
            [heure, minute] = str.split(":")
            h_dep = (int(jour)-8)*60*24 + int(heure)*60 + int(minute)
            # on respecte l'horaire de depart : la derniere tache doit se terminer avant que le train ne parte
            m.addConstr(var_dict["essai de frein départ"][sillon] +
                        taches_df[taches_df["Type de tache humaine"] == "essai de frein départ"]["Durée"].iloc[0] <= h_dep)

    ###### Heure d'arrivée du train respectée  #####
    for sillon in var_dict["arrivée Reception"].keys():
        LDEP = sillons_df[sillons_df["train_id"] == sillon]["LDEP"].iloc[0]
        LARR = sillons_df[sillons_df["train_id"] == sillon]["LARR"].iloc[0]
        if LARR in ["WPY_REC", "WPY"]:
            compteur += 1
            jour = sillons_df[sillons_df["train_id"]
                                == sillon]["JARR"].iloc[0]
            jour = jour[0:2]
            str = sillons_df[sillons_df["train_id"]
                                == sillon]["HARR"].iloc[0]
            [heure, minute] = str.split(":")
            h_arr = (int(jour)-8)*60*24 + int(heure)*60 + int(minute)
            # on respecte l'horaire d'arrivee : la 1ere tache ne peut commencer que lorsque le train est arrivé
            m.addConstr(var_dict["arrivée Reception"][sillon] >= h_arr)
    # print("compteur for horaires", compteur)

    p_bar.update(1)
    p_bar.refresh()
    ##### Respect du nombre de voies de chantier #####
    # chantier_cycles = {}
    # for chantier in set(taches_df["Chantier"].values):
    #     chantier_cycles[chantier, "end"] = taches_df[taches_df["Chantier"] == chantier][taches_df.Ordre ==
    #                                                                                       taches_df[taches_df["Chantier"] == chantier].Ordre.max()]["Type de tache humaine"].iloc[0]
    #     chantier_cycles[chantier, "start"] = taches_df[taches_df["Chantier"] == chantier][taches_df.Ordre ==
    #                                                                                     taches_df[taches_df["Chantier"] == chantier].Ordre.min()]["Type de tache humaine"].iloc[0]

    # def get_all_tasks_by_name(name):
    #     return var_dict[name].keys()
    # B = {}
    # def b(tache_i, tache_j, tache_i_name, duree=0):
    #             if (tache_i_name,tache_i,tache_j) in B.keys():
    #                 bb = B[tache_i_name,tache_i,tache_j]
    #                 return 1-bb
    #             else:
    #                 bb = m.addVar(vtype=GRB.BINARY, name=f"HELPER {tache_i_name},{tache_i},{tache_j}")
    #                 B[tache_i_name,tache_j,tache_i]= bb
                
    #                 m.addConstr((bb == 1) >> (var_dict[tache_i_name][tache_i]+duree <= var_dict[chantier_cycles[chantier, "start"]][tache_j]),
    #                             name="indicator_constr1")
    #                 m.addConstr((bb == 0) >> (var_dict[tache_i_name][tache_i]+duree >= var_dict[chantier_cycles[chantier, "start"]][tache_j] + 0.5),
    #                             name="indicator_constr2")
    #                 return bb
    
    # OCCUPATIONS = []
    # def add_occupation_constr(chantier, tache_debut):
        

    #     occupation = quicksum([b(tache_chantier,
    #                              tache_debut,
    #                              chantier_cycles[chantier, "start"])
    #                            for tache_chantier in get_all_tasks_by_name(chantier_cycles[chantier, "start"])])
    #     duree = taches_df[taches_df["Type de tache humaine"]
    #                       == chantier_cycles[chantier, "end"]]["Durée"].iloc[0]
    #     occupation = occupation - quicksum([b(tache_chantier,
    #                                           tache_debut,
    #                                           chantier_cycles[chantier, "end"],
    #                                           duree= duree)
    #                                         for tache_chantier in get_all_tasks_by_name(chantier_cycles[chantier, "end"])])
    #     OCCUPATIONS.append(occupation)
    #     m.addConstr(occupation<=chantiers_df[chantiers_df["Chantier"]==chantier]["Nombre de voies"].iloc[0])
    #     m.addConstr(occupation>=1)
    # for chantier in set(chantiers_df["Chantier"].values):
    #     print(f"Adding occupation constrainst for: {chantier}...")
    #     for tache_debut in get_all_tasks_by_name(chantier_cycles[chantier, "start"]):
    #         add_occupation_constr(chantier, tache_debut)
    
    
    # OCCUPATIONS V 2.0 
    
    def get_all_tasks_by_name(name):
        return var_dict[name].keys()
    B = {}
    def b(tache_i, tache_j, tache_i_name, tache_j_name, duree=0):
        '''
        Creates or gets the variable indicating that tache_i <= tache_j
        With a potential duree after tache_i
        None name is for constants
        '''
        # print(tache_j, tache_i, tache_j_name, tache_i_name)
        # print("=====================")
        if duree!=0:
            #no need to check dict
            pass
        elif (tache_j, tache_i, tache_j_name, tache_i_name) in B.keys():
            bb = B[tache_j, tache_i, tache_j_name, tache_i_name]
            return 1-bb
        # has not returned
        bb = m.addVar(vtype=GRB.BINARY, name=f"HELPER {tache_i},{tache_j}")
        B[tache_i, tache_j, tache_i_name, tache_j_name]= bb
        #  some have to be derived from the gurobi variables, others are directly constants 
        if tache_i_name != None:
            tache_i_var = var_dict[tache_i_name][tache_i]
        else:
            tache_i_var = m.addVar(vtype=GRB.INTEGER, name=f"HELPER2 {tache_i},{tache_j}")
            m.addConstr(tache_i_var==tache_i, name="var_const")
        if tache_j_name != None:
            tache_j_var = var_dict[tache_j_name][tache_j]
        else:
            tache_j_var = m.addVar(vtype=GRB.INTEGER, name=f"HELPER2 {tache_i},{tache_j}")
            m.addConstr(tache_j_var==tache_j, name="var_const")
        m.addConstr((bb == 1) >> (tache_i_var+duree <= tache_j_var),
                    name="indicator_constr1")
        m.addConstr((bb == 0) >> (tache_i_var+duree >= tache_j_var+ 0.5),
                    name="indicator_constr2")
        return bb
    
    OCCUPATIONS = {"DEB":[], "FOR":[], "DEG":[]}
    # adding occupations 
    ### DEB ###
    # getting all sillons to loop over and add constrs 
    for sillon_target in var_dict["arrivée Reception"].keys():
        # postive sum on HARR : 
        pos_sum = quicksum([
            b(utils.get_min_from_sillonid("ARR", sillon_dep, sillons_df),
              utils.get_min_from_sillonid("ARR", sillon_target, sillons_df),
              None,
              None
              ) 
            for sillon_dep in var_dict["arrivée Reception"].keys()    
            ])
        duree = taches_df[taches_df["Type de tache humaine"]
                          == "débranchement"]["Durée"].iloc[0]
        neg_sum = quicksum([
            b(sillon_dep,
              utils.get_min_from_sillonid("ARR", sillon_target, sillons_df),
              "débranchement",
              None, 
              duree=duree
              ) 
            for sillon_dep in var_dict["arrivée Reception"].keys()    
        ])
        occupation = pos_sum - neg_sum
        OCCUPATIONS["DEB"].append(occupation)
        m.addConstr(occupation<=chantiers_df[chantiers_df["Chantier"]=="WPY_REC"]["Nombre de voies"].iloc[0])
        
    ### FOR ###
    # as we have to find the wagons the positive sum has +1 depth, so we defien the following fucntion : 
    def has_some_wagon_arrived_yet(sillon_deb_target, sillon_for):
        # compute antecedants 
        antecedents_sillon_for = [correspondances_df[correspondances_df["id_wagon"] == wagon]["train_id"].iloc[0] 
                                  for wagon in list(correspondances_df[correspondances_df["train_id"] == sillon_for]["id_wagon"])]
        duree = taches_df[taches_df["Type de tache humaine"]
                          == "débranchement"]["Durée"].iloc[0]
        # sum of all antecedants that managed to arrive before this one train
        n = quicksum([
            b(sillon_deb,
              sillon_deb_target,
              "débranchement",
              "débranchement",
              ) 
            for sillon_deb in antecedents_sillon_for    
        ])
        # bb = 1 if at least one wagon has arrived
        bb = m.addVar(vtype=GRB.BINARY, name=f"HELPER WAGON FOR")
        m.addConstr((bb == 1) >> (n>=1),
                    name="indicator_constr1")
        m.addConstr((bb == 0) >> (n <= 0),
                    name="indicator_constr2")
        return bb
    
    for sillon_deb_target in var_dict["débranchement"].keys():
        # postive sum on HARR : 
        pos_sum = quicksum([
            has_some_wagon_arrived_yet(sillon_deb_target, sillon_for)
            for sillon_for in var_dict["appui voie + mise en place câle"].keys()    
            ])
        duree = taches_df[taches_df["Type de tache humaine"]
                          == "débranchement"]["Durée"].iloc[0]
        duree -= taches_df[taches_df["Type de tache humaine"]
                          == "dégarage / bouger de rame"]["Durée"].iloc[0]
        neg_sum = quicksum([
            b(sillon_deg,
              sillon_deb_target,
              "dégarage / bouger de rame",
              "débranchement", 
              duree=duree
              ) 
            for sillon_deg in var_dict["dégarage / bouger de rame"].keys()    
        ])
        occupation = pos_sum - neg_sum
        OCCUPATIONS["FOR"].append(occupation)
        m.addConstr(occupation<=chantiers_df[chantiers_df["Chantier"]=="WPY_FOR"]["Nombre de voies"].iloc[0])
    
    ### DEG ###
    for sillon_target in var_dict["dégarage / bouger de rame"].keys():
        # postive sum on HARR : 
        pos_sum = quicksum([
            b(sillon_deg,
              sillon_target,
              "dégarage / bouger de rame",
              "dégarage / bouger de rame"
              ) 
            for sillon_deg in var_dict["dégarage / bouger de rame"].keys()    
            ])
        duree = -taches_df[taches_df["Type de tache humaine"]
                          == "dégarage / bouger de rame"]["Durée"].iloc[0]
        neg_sum = quicksum([
            b(utils.get_min_from_sillonid("DEP", sillon_dep, sillons_df),
              sillon_target,
              None,
              "dégarage / bouger de rame",
              duree=duree
              ) 
            for sillon_dep in var_dict["dégarage / bouger de rame"].keys()    
        ])
        occupation = pos_sum - neg_sum
        OCCUPATIONS["DEG"].append(occupation)
        m.addConstr(occupation<=chantiers_df[chantiers_df["Chantier"]=="WPY_DEP"]["Nombre de voies"].iloc[0])
    
    p_bar.update(1)
    p_bar.refresh()
    print()
    ##### Horaires de debuts des taches (modulo truc) #####
    #debug info
    # print("B= ",B)
    return B,OCCUPATIONS

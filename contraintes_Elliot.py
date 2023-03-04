##### Antécedents #####
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
                m.addConstr(var_dict[tache][sillon] == var_dict[tache_precedante][sillon] +
                            taches_df[taches_df["Type de tache humaine"] == tache_precedante]["Durée"].iloc[0])  # == car on les enchaîne sinon >=

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


# PAS ENCORE OPERATIONNEL IL FAUT ATTENDRE LE LABEL DES VARIABLES SILLONS
ordre_max_dep = 4  # on fixe le numéro de la derniere tache pour le DEP au cas ou cela change suivant les instances
ordre_min_arr = 1  # on fixe le numéro de la premiere tache pour l'ARR au cas ou cela change suivant les instances

for tache in var_dict.keys():
    for sillon in var_dict[tache].keys():
        # on teste si la tache est bien la derniere avant le depart
        if tache == taches_df[taches_df["Ordre"] == ordre_max_dep][taches_df["Type de train"] == DEP]["Type de tache humaine"].iloc[0]:
            duree_tache = taches_df[taches_df["Type de tache humaine"]
                                    == tache]["Durée"].iloc[0]
            heure_dep_sillon = sillon_df[]
            m.addConstr(var_dict[tache][sillon] +
                        duree_tache <= var_dict[tache_collee][sillon])
    ##### heure d'arrivée du train respectée  #####


for sillon var_dict["FOR"].keys():
    list_wagons = list(correspondances_df[correspondances_df["train_id"] ==
                       sillon][correspondances_df["LDEP"] == "WPY"]["id_wagon"])
    for wagon in list_wagon:
        sillon_arr = correspondances_df[correspondances_df["id_wagon"] ==
                                        wagon][correspondances_df["LARR"] == "WPY"]["train_id"].iloc[0]
        m.addConst(var_dict["DEB"][sillon_arr] + machines_df[machines_df["Machine"]
                   == "DEB"]["Duree"] <= var_dict["FOR"][sillon])

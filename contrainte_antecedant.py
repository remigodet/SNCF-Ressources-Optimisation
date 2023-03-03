# Définition des autres contraintes
for tache in dico.keys():
    for sillon in dico[tache].keys():
        # on ne teste que les taches humaines
        if tache in list(taches_df["Type de tache humaine"]):
            ordre = taches_df[taches_df["Type de tache humaine"]
                              == tache]["Ordre"].iloc[0]  # on stocke l'ordre de la tache
            type_train = taches_df[taches_df["Type de tache humaine"]
                                   == tache]["Type de train"].iloc[0]  # on stocke le type de train pour faire matcher plus tard avec celui de la tache precedante
            if ordre > 1:
                tache_precedante = taches_df[taches_df["Ordre"] == ordre -
                                             1][taches_df["Type de train"] == type_train]["Type de tache humaine"].iloc[0]
                m.addConstr(dico[tache][sillon] == dico[tache_precedante][sillon] +
                            taches_df[taches_df["Type de tache humaine"] == tache_precedante]["Durée"].iloc[0])  # == car on les enchaîne sinon >=
        ## Débranchement ##
        if tache == "Débranchement":
            m.addConstr(dico[tache][sillon] >= dico["préparation tri"][sillon] +
                        taches_df[taches_df["Type de tache humaine"] == "préparation tri"]["Durée"].iloc[0])  # on ajoute les contraintes pour les taches machines a la main
        ## Dégarage ##
        if tache == "Dégarage":
            m.addConstr(dico[tache][sillon] >= dico["préparation tri"][sillon] +
                        taches_df[taches_df["Type de tache humaine"] == "préparation tri"]["Durée"].iloc[0])

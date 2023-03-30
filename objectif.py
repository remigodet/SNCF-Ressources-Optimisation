from gurobipy import *
import utils 
from tqdm.notebook import tqdm



def get_objectif(m, var_dict, links_dict, dataframes):
    roulements_df = dataframes["roulements_df"]
    taches_df = dataframes["taches_df"]
    taches_humaines =  taches_df["Type de tache humaine"]
    objectif = 0
    # horizon de temps cf CONTRAINTES J1
    
    # objectif primaire : minimiser le nombre de JdS
    all_active_jds = {}
    temp = []
    jour_to_dispo = lambda j: "7" if j%7==0 else str(j%7)
    for roulement in tqdm(roulements_df["Roulement"], "Create JdS objective"):
        for a in range(1, roulements_df[roulements_df["Roulement"]==roulement]["Nombre agents"].iloc[0]+1):
            for jour in range(1,len(set(dataframes["sillons_df"]["JDEP"]))+1):
                nb_cycles = len(roulements_df[roulements_df["Roulement"]==roulement]["Cycles horaires"].iloc[0].split(";"))
                for c in range(1,nb_cycles+1):
                    if jour_to_dispo(jour) in roulements_df[roulements_df["Roulement"]==roulement]["Jours de la semaine"].iloc[0].split(";"):
                        taches_of_jds = []
                        for chantier_tache in taches_humaines:
                            for tache in var_dict[chantier_tache].keys():
                                if (chantier_tache,tache,roulement,a,jour,c) in links_dict.keys():
                                    taches_of_jds.append((tache, chantier_tache))
                        count_var = m.addVar(vtype=GRB.BINARY, name=f"HELPER OBJECTIVE")
                        m.addConstr(count_var == max_(taches_of_jds))
                        temp.append(count_var)
                        all_active_jds[roulement,a,jour,c] = count_var
    objectif += quicksum(temp)
    
    # objectif secondaire : minimiser la somme des minutes de départ des derniers trains
    final_train_task = dataframes["sillons_df"].copy()
    final_train_task = final_train_task[final_train_task["LDEP"]=="WPY"]
    final_train_task = final_train_task[final_train_task["JARR"]==final_train_task["JARR"].max()]
    final_train_task = quicksum([var_dict["essai de frein départ"][temp] for temp in list(final_train_task["train_id"])])
    
    
    objectif += final_train_task/1000000
    
    
    return all_active_jds, objectif
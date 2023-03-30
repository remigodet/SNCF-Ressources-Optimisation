
from gurobipy import *
from tqdm.notebook import tqdm
import utils 

def generate_variablesJ1(m: Model, dataframes):
    variables = {}
    # create variables structure
    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]

    def add_arrival_tasks(sillon):
        # humain
        for idx in range(len(taches_df)):
            if taches_df.iloc[idx]["Type de train"] == "ARR":
                variables[taches_df.iloc[idx]["Type de tache humaine"]][sillon["train_id"]] = m.addVar(
                    vtype=GRB.INTEGER, name=str(idx) + "_"+sillon["train_id"])
        # machine
        for idx in range(len(machines_df)):
            if machines_df.iloc[idx]["Machine"] in ["DEB"]:
                variables[machines_df.iloc[idx]["Machine"]][sillon["train_id"]] = m.addVar(
                    vtype=GRB.INTEGER, name=f'{machines_df.iloc[idx]["Machine"]}-{sillon["train_id"]}')

    def add_departure_tasks(sillon):
        for idx in range(len(taches_df)):
            if taches_df.iloc[idx]["Type de train"] == "DEP":
                variables[taches_df.iloc[idx]["Type de tache humaine"]][sillon["train_id"]] = m.addVar(
                    vtype=GRB.INTEGER, name=str(idx) + "_"+sillon["train_id"])
        # machine
        for idx in range(len(machines_df)):
            if machines_df.iloc[idx]["Machine"] in ["FOR", "DEG"]:
                try:
                    variables[machines_df.iloc[idx]["Machine"]][sillon["train_id"]]
                    print("NOT NONE")
                    print(machines_df.iloc[idx]["Machine"])
                    print(sillon["train_id"])
                except: pass
                variables[machines_df.iloc[idx]["Machine"]][sillon["train_id"]] = m.addVar(
                    vtype=GRB.INTEGER, name=f'{machines_df.iloc[idx]["Machine"]}-{sillon["train_id"]}')

    for idx in range(len(taches_df)):
        variables[taches_df.iloc[idx]["Type de tache humaine"]] = {}
    for idx in range(len(machines_df)):
        if machines_df.iloc[idx]["Machine"]:
            variables[machines_df.iloc[idx]["Machine"]] = {}

    sillons_df = dataframes["sillons_df"]
    for idx in tqdm(range(len(sillons_df)), desc = "Initialising variables"):
        sillon = sillons_df.iloc[idx]
        # print(sillon["n°TRAIN"])
        if sillon["LDEP"] == "NC":
            # add all taches arrival
            add_arrival_tasks(sillon)
        elif sillon["LDEP"] in ["WPY_DEP", "WPY"]:
            # add all taches departure
            add_departure_tasks(sillon)
        else:
            raise Exception(f"LDEP: '{sillon['LDEP']}' of sillon not recognized ! ")
    print()
    return variables
def generate_variablesJ2(m: Model, var_dict, dataframes):
    REDUCTION_PARAM = 2*24*60
    roulements_df = dataframes["roulements_df"]
    taches_df = dataframes["taches_df"]
    sillons_df = dataframes["sillons_df"]
    jour_to_dispo = lambda j: "7" if j%7==0 else str(j%7)
    variables = {}
    for roulement in tqdm(roulements_df["Roulement"], "Link variables"):
        for a in range(1, roulements_df[roulements_df["Roulement"]==roulement]["Nombre agents"].iloc[0]+1):
            for jour in range(1,len(set(dataframes["sillons_df"]["JDEP"]))+1):
                nb_cycles = len(roulements_df[roulements_df["Roulement"]==roulement]["Cycles horaires"].iloc[0].split(";"))
                for c in range(1,nb_cycles+1):
                    if jour_to_dispo(jour) in roulements_df[roulements_df["Roulement"]==roulement]["Jours de la semaine"].iloc[0].split(";"):
                        jds_start, jds_end = utils.get_min_from_rajc(roulement, jour, c, roulements_df)
                        for chantiers in roulements_df[roulements_df["Roulement"]==roulement]["Connaissances chantiers"]:
                            for chantier in chantiers.split(";"):
                                for tache_name in taches_df[taches_df["Chantier"]==chantier]["Type de tache humaine"]:
                                    for tache in var_dict[tache_name].keys():
                                        # debug
                                        debug = False
                                        # if tache == "4424909/08/202203:0723:5909/08/2022" and tache_name=="appui voie + mise en place câle":
                                        #     print(tache_name, tache)
                                        #     print(roulement,a,jour,c)
                                        #     print("start, end: ", jds_start, jds_end)
                                        #     print(jds_end)
                                        #     debug = True
                                        # peut mieux faire avec tache_name et order des tache !! 
                                        ok = False
                                        if chantier == "WPY_REC":
                                            sillon_arrives = utils.get_min_from_sillonid("ARR",tache,sillons_df)
                                            # le sillon peut arriver en cours de jds 
                                            ok = (sillon_arrives <= jds_end) and (sillon_arrives + REDUCTION_PARAM >= jds_start)
                                        elif chantier in ["WPY_FOR", "WPY_DEP"]:
                                            sillon_departs= utils.get_min_from_sillonid("DEP",tache,sillons_df)
                                            # if debug: print("DEPQRTS: ",sillon_departs)
                                            # le sillon peut partir en cours de jds 
                                            ok = (jds_start <= sillon_departs) and (jds_start >= sillon_departs-REDUCTION_PARAM)
                                        else:
                                            raise Exception("Chantier not found:", chantier)
                                        # if debug: print(ok)
                                        if ok:
                                            # if debug or (tache=="5400315/08/202203:5923:5915/08/2022" and tache_name=="essai de frein départ"):
                                            #     print("===========================")
                                            #     print(chantier)
                                            #     print(sillon_departs)
                                            #     print("Created tache_name,tache,roulement,a,jour,c",tache_name,tache,roulement,a,jour,c)
                                            #     print(utils.get_min_from_rajc(roulement,jour,c,roulements_df))
                                            variables[tache_name,tache,roulement,a,jour,c] = m.addVar(vtype=GRB.BINARY, 
                                                                                    name=f'Link of {tache_name} {tache} TO {roulement}-{a}-{jour}-{c}')
    m.update()
    return variables

if __name__ == "__main__":
    m = Model()
    import data
    dataframes = data.get_all_pandas()
    var_dict = generate_variablesJ1(m, dataframes)
    links_dict = generate_variablesJ2(m, var_dict, dataframes)
    print(len(links_dict))

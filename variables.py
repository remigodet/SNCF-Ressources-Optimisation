
from gurobipy import *


def add_arrival_tasks(variables, sillon,dataframes):
    machines_df = dataframes["machines_df"]
    
    taches_df = dataframes["taches_df"]

    # humain
    for idx in range(len(taches_df)):
        if taches_df.iloc[idx]["Type de train"] == "ARR":
            variables[taches_df.iloc[idx]["Type de tache humaine"]][sillon["n°TRAIN"]] = m.addVar(vtype = GRB.INTEGER, name = str(idx) +"_"+sillon["n°TRAIN"])
    # machine
    for idx in range(len(machines_df)):
        if machines_df.iloc[idx]["Machine"] in ["DEB"]:
            variables[machines_df.iloc[idx]["Machine"]][sillon["n°TRAIN"]] = m.addVar(vtype = GRB.INTEGER, name = f'{machines_df.iloc[idx]["Machine"]}-{sillon["n°TRAIN"]}')

def add_departure_tasks(variables, sillon,dataframes):
    machines_df = dataframes["machines_df"]
    
    taches_df = dataframes["taches_df"]
    for idx in range(len(taches_df)):
        if taches_df.iloc[idx]["Type de train"] == "DEP":
            variables[taches_df.iloc[idx]["Type de tache humaine"]][sillon["n°TRAIN"]] = m.addVar(vtype = GRB.INTEGER, name = str(idx) +"_"+sillon["n°TRAIN"])
    # machine
    for idx in range(len(machines_df)):
        if machines_df.iloc[idx]["Machine"] in ["FOR","DEG"]:
            variables[machines_df.iloc[idx]["Machine"]][sillon["n°TRAIN"]] = m.addVar(vtype = GRB.INTEGER, name = f'{machines_df.iloc[idx]["Machine"]}-{sillon["n°TRAIN"]}')


def generate_variables(m:Model, dataframes):
    variables = {}
    # create variables structure 

    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]

    for idx in range(len(taches_df)):
        variables[taches_df.iloc[idx]["Type de tache humaine"]] = {}
    for idx in range(len(machines_df)):
            if machines_df.iloc[idx]["Machine"]:
                variables[machines_df.iloc[idx]["Machine"]] = {}

    sillons_df = dataframes["sillons_df"]
    for idx in range(len(sillons_df)):
        sillon = sillons_df.iloc[idx]
        print(sillon["n°TRAIN"])
        if sillon["LDEP"]=="NC":
            # add all taches arrival
            add_arrival_tasks(variables, sillon, dataframes)
        elif sillon["LDEP"]=="WPY":
            #add all taches departure
            add_departure_tasks( variables, sillon, dataframes)
        else: 
            raise Exception("LDEP of sillon not recognized ! ")
    # print(variables)
    return variables

if __name__ == "__main__":
    m = Model()
    import data
    dataframes = data.get_all_pandas()
    variables = generate_variables(m, dataframes)
    print(variables)
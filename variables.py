
from gurobipy import *
from tqdm import tqdm


def generate_variables(m: Model, dataframes):
    variables = {}
    # create variables structure
    taches_df = dataframes["taches_df"]
    machines_df = dataframes["machines_df"]

    def add_arrival_tasks(sillon):
        # humain
        for idx in range(len(taches_df)):
            if taches_df.iloc[idx]["Type de train"] == "ARR":
                variables[taches_df.iloc[idx]["Type de tache humaine"]][str(sillon["n°TRAIN"])+str(sillon["JDEP"])] = m.addVar(
                    vtype=GRB.INTEGER, name=str(idx) + "_"+str(sillon["n°TRAIN"])+str(sillon["JDEP"]))
        # machine
        for idx in range(len(machines_df)):
            if machines_df.iloc[idx]["Machine"] in ["DEB"]:
                variables[machines_df.iloc[idx]["Machine"]][str(sillon["n°TRAIN"])+str(sillon["JDEP"])] = m.addVar(
                    vtype=GRB.INTEGER, name=f'{machines_df.iloc[idx]["Machine"]}-{str(sillon["n°TRAIN"])+str(sillon["JDEP"])}')

    def add_departure_tasks(sillon):
        for idx in range(len(taches_df)):
            if taches_df.iloc[idx]["Type de train"] == "DEP":
                variables[taches_df.iloc[idx]["Type de tache humaine"]][str(sillon["n°TRAIN"])+str(sillon["JDEP"])] = m.addVar(
                    vtype=GRB.INTEGER, name=str(idx) + "_"+str(sillon["n°TRAIN"])+str(sillon["JDEP"]))
        # machine
        for idx in range(len(machines_df)):
            if machines_df.iloc[idx]["Machine"] in ["FOR", "DEG"]:
                variables[machines_df.iloc[idx]["Machine"]][str(sillon["n°TRAIN"])+str(sillon["JDEP"])] = m.addVar(
                    vtype=GRB.INTEGER, name=f'{machines_df.iloc[idx]["Machine"]}-{str(sillon["n°TRAIN"])+str(sillon["JDEP"])}')

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
        elif sillon["LDEP"] == "WPY_DEP":
            # add all taches departure
            add_departure_tasks(sillon)
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

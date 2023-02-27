import pandas as pd
from pandas import read_excel

data = {}
data["taches_df"] = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Taches humaines")
data["chantiers_df"] = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Chantiers")
data["machines_df"] = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Machines")
data["sillons_df"] = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Sillons")
data["correspondances_df"] = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Correspondances")

def get_all_pandas():
    return data

if __name__ == "__main__":
    data_test = get_all_pandas()
    chantiers_df = data_test["chantiers_df"]
    print(chantiers_df.head())
    print(chantiers_df["Chantier"]) # colonne
    print(chantiers_df.iloc[0]) #line
    print(chantiers_df.iloc[0]["Chantier"]) # value
    print(chantiers_df._get_value(0, "Chantier")) #value
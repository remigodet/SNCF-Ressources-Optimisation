import pandas as pd
from pandas import read_excel

taches_df = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Taches humaines")
chantiers_df = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Chantiers")
machines_df = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Machines")
sillons_df = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Sillons")
correspondances_df = pd.read_excel("./Data SNCF/mini_instance.xls", sheet_name="Correspondances")



if __name__ == "__main__":
    print(chantiers_df.head())
    print(chantiers_df["Chantier"]) # colonne
    print(chantiers_df.iloc[0]) #line
    print(chantiers_df.iloc[0]["Chantier"]) # value
    print(chantiers_df._get_value(0, "Chantier")) #value
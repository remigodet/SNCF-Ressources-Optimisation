import pandas as pd
from pandas import read_excel
from tqdm import tqdm
NAME = "instance_WPY_realiste.xls"
data = {}
p_bar = tqdm(range(5), desc="LOADING DATA")
data["taches_df"] = pd.read_excel(f"./Data SNCF/{NAME}", sheet_name="Taches humaines")
p_bar.update(1)
p_bar.refresh()
data["chantiers_df"] = pd.read_excel(f"./Data SNCF/{NAME}", sheet_name="Chantiers")
p_bar.update(1)
p_bar.refresh()
data["machines_df"] = pd.read_excel(f"./Data SNCF/{NAME}", sheet_name="Machines")
p_bar.update(1)
p_bar.refresh()
data["sillons_df"] = pd.read_excel(f"./Data SNCF/{NAME}", sheet_name="Sillons")
p_bar.update(1)
p_bar.refresh()
data["correspondances_df"] = pd.read_excel(f"./Data SNCF/{NAME}", sheet_name="Correspondances")
p_bar.update(1)
p_bar.refresh()

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
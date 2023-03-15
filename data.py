import pandas as pd
from pandas import read_excel
from tqdm import tqdm
# NAME = "mini_instance.xls"
NAME = "instance_WPY_realiste_corrigee3.xls"
data = {}
p_bar = tqdm(range(6), desc="LOADING DATA")
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
# update sillon to unique names :
# print(data["sillons_df"])
def get_id(row):
    if row.LDEP != "NC":
        # print(data["sillons_df"][(data["sillons_df"]["n°TRAIN"] == row["n°TRAIN"]) &
        #                                               (data["sillons_df"]["JDEP"] == row["JDEP"])]["train_id"].iloc[0])
        return data["sillons_df"][(data["sillons_df"]["n°TRAIN"] == row["n°TRAIN"]) &
                                                      (data["sillons_df"]["JDEP"] == row["JDEP"])]["train_id"].iloc[0]
    else:
        try :
            a = data["sillons_df"][(data["sillons_df"]["n°TRAIN"] == row["n°TRAIN"]) &
                                                      (data["sillons_df"]["JARR"] == row["JDEP"])]["train_id"].iloc[0]
        except:
            try : 
                a = data["sillons_df"][(data["sillons_df"]["n°TRAIN"] == row["n°TRAIN"]) &
                                                      (data["sillons_df"]["JDEP"] == row["JDEP"])]["train_id"].iloc[0]
            except:
                try : 
                    a= data["sillons_df"][(data["sillons_df"]["n°TRAIN"] == row["n°TRAIN"])]["train_id"].iloc[0]
                except:
                    print(row["n°TRAIN"])
                    print(row.JDEP)

        return a

p_bar.update(1)
p_bar.refresh()
data["sillons_df"]["HARR"] = data["sillons_df"].apply(lambda row: str(row["HARR"])[:5], axis=1)
data["sillons_df"]["HDEP"] = data["sillons_df"].apply(lambda row: str(row["HDEP"])[:5], axis=1)
data["sillons_df"]["train_id"] = data["sillons_df"].apply(lambda row: str(row["n°TRAIN"])+str(row.JDEP)+str(row.HDEP)+str(row.HARR)+str(row.JARR), axis=1)
data["correspondances_df"]["train_id"] = data["correspondances_df"].apply( lambda row: get_id(row) , axis=1)
p_bar.update(1)
p_bar.refresh()
def get_all_pandas():
    return data

if __name__ == "__main__":
    data_test = get_all_pandas()
    chantiers_df = data_test["chantiers_df"]
    # print(chantiers_df.head())
    # print(chantiers_df["Chantier"]) # colonne
    # print(chantiers_df.iloc[0]) #line
    # print(chantiers_df.iloc[0]["Chantier"]) # value
    # print(chantiers_df._get_value(0, "Chantier")) #value
    print(data["correspondances_df"])
    print(data["sillons_df"])
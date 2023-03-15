# Fichier pour présenter correctement les solutions

def min_to_jour(min):
    mois = "08"
    j = int(min//(60*24) + 8)
    h = int((min - (j-8)*60*24)//60)
    m = int((min - (j-8)*60*24) % 60)
    jour = str(j)
    if len(jour) == 1:
        jour = "0" + jour
    heure = str(h)
    if len(heure) == 1:
        heure = "0" + heure
    minute = str(m)
    if len(minute) == 1:
        minute = "0" + minute
    return (jour + "/" + mois, heure + ":" + minute)

def get_min_from_sillonid(HJCHOICE, sillon_id, sillons_df):
    '''
    HJCHOICE must be DEP or ARR
    '''
    if HJCHOICE not in ["ARR", "DEP"]:
        raise KeyError(HJCHOICE)
    jour = sillons_df[sillons_df["train_id"]== sillon_id][f"J{HJCHOICE}"].iloc[0]
    jour = str(jour)[0:2]
    heure = sillons_df[sillons_df["train_id"]
                        == sillon_id][f"H{HJCHOICE}"].iloc[0]
    [heure, minute] = heure.split(":")
    h_dep = (int(jour)-8)*60*24 + int(heure)*60 + int(minute)
    return h_dep
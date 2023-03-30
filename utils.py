## Fonction pour présenter correctement les solutions
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

## Fonction pour collecter le début et la fin de la journée de service en minutes
def get_min_from_rajc(r,j,c, roulements_df):
    '''
    return:  minute_start, minute_end
    For now, we don't sparse minutes. 
    '''
    try:
        cycle = roulements_df[roulements_df["Roulement"]==r]["Cycles horaires"].iloc[0]
        cycle = cycle.split(";")
        cycle = cycle[c-1]
        cycle = cycle.split("-")
        cycle_start = int(cycle[0][:2])
        cycle_end = int(cycle[1][:2])
        minute_start = (j-1)*24*60 + cycle_start*60
        if cycle_end<=cycle_start:
            minute_end = (j-1)*24*60 + (cycle_end+24)*60
        else :
            minute_end = (j-1)*24*60 + (cycle_end)*60
    except:
        raise Exception("error", r,j,c)
    # print(r,j,c,minute_start, minute_end)
    return minute_start, minute_end
    
    
if __name__ == "__main__":
    import data
    dataframes = data.get_all_pandas()
    roulements_df = dataframes["roulements_df"]
    get_min_from_rajc("roulement_reception",0,1, roulements_df=roulements_df)
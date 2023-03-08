# Fichier avec les fonctions qu'on utilise dans nos codes

# Fonction qui convertit le nombre de minutes en format ("jj/mm", "hh:mm")
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

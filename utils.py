import xml.etree.ElementTree as ET

def hour_to_float(text:str):
    return float(text[0:2])+float(text[3:5])/60

def get_grille_horaire(root, id: str):
    '''

    Returns the hourly grid in the form of a dict. 

    Keywords arguments :

    id -- str the hourly grid id
    '''

    d = {}

    x_path = f'./grillesHoraire/grilleHoraire/[@id="{id}"]/Ouverture'

    res = root.findall(x_path)

    for i in range(len(res)):

        for jour in res[i].attrib["jours"]:

            if jour != ';':

                d[int(jour)] = (hour_to_float(res[i].attrib["heureOuverture"]), hour_to_float(res[i].attrib["heureFermeture"]))

    return d

def get_periode(root, line: str):
    '''
    Reads a one-liner xml segment and
    return a {"jourDebut": date, "jourFin": date, "grilleHoraire": dict} dict.
    '''
    e = ET.fromstring(line)
    d = e.attrib
    d["grilleHoraire"] = get_grille_horaire(root, d["grilleHoraire"])
    return d 
def get_periode(root, e:ET.Element):
    '''
    Reads an ElementTree element and
    return a {"jourDebut": date, "jourFin": date, "grilleHoraire": dict} dict.
    '''
    
    d = e.attrib
    d["grilleHoraire"] = get_grille_horaire(root, d["grilleHoraire"])
    return d 

def get_machines(root):
    '''

    Returns the machine dict in the form of a dict. 
    '''

    d = {}
    for nom in ["machineDEB", "machineFOR", "machineDEG"]:
        # durée 
        x_path = f'./machines/machine/[@nom="{nom}"]'
        res = root.find(x_path)
        
        if "dureeCreneau" in res.attrib.keys():
            res.attrib["dureeCreneau"] = int(res.attrib["dureeCreneau"])
        d[nom] = res.attrib

        # typeTache
        x_path = f'./machines/machine/[@nom="{nom}"]/typeTache'
        res = root.findall(x_path)
        for item in res:
            if "nbCreneau" in item.attrib.keys():
                item.attrib["nbCreneau"] = int(item.attrib["nbCreneau"])
        d[nom]["typeTache"] = [res[i].attrib for i in range(len(res))]

        # periodes 
        x_path = f'./machines/machine/[@nom="{nom}"]/typeTache'
        res = root.findall(x_path)
    return d

def get_services(root):
    '''

    Returns the services dict in the form of a dict. 
    !! nomVoie and longueur is a tuple in Voie!! 
    '''

    d = {}
    x_path = f'./services/'
    res = root.findall(x_path)
    print(res[0])
    for item in res:
        item.attrib["heureDebut"] = hour_to_float(item.attrib["heureDebut"])
        d[item.attrib["nom"]] = item.attrib
    return d

def get_chantier(root, nomSite:str):
    if nomSite == "WPY_REC":
        target = "chantierReception"
    elif nomSite == "WPY_FOR":
         target = "chantierFormation"
    elif nomSite == "WPY_DEP":
         target = "chantierDepart"
    else:
        raise ValueError(nomSite)

    d = {}

    # attributes
    x_path = f'./{target}'
    res = root.find(x_path)
    d[target] = res.attrib
    # periods
    periods = res.findall('./periode')
    d[target]["periodes"] = [get_periode(root, p) for p in periods ]
    # voies 
    voies = res.findall('./Voie')
    d[target]["voies"] = [(v.attrib["nomVoie"], int(v.attrib["longueur"])) for v in voies ]


    # # typeTache
    # x_path = f'./machines/machine/[@nom="{nom}"]/typeTache'
    # res = root.findall(x_path)
    # for item in res:
    #     if "nbCreneau" in item.attrib.keys():
    #         item.attrib["nbCreneau"] = int(item.attrib["nbCreneau"])
    # d[nom]["typeTache"] = [res[i].attrib for i in range(len(res))]

    # # periodes 
    # x_path = f'./machines/machine/[@nom="{nom}"]/typeTache'
    # res = root.findall(x_path)

    return d

    
    



# tests
if __name__ == "__main__":

    # build the tree
    tree = ET.parse('Data-SNCF/geographie_WPY.xml')
    root = tree.getroot()

    # grille horaire
    # print(hour_to_float("21:00"))
    # print(get_grille_horaire(root, "horaires_WPY_FOR"))

    # machines
    # print(get_periode(root, '<periode jourDebut="01/01/2021" jourFin="07/08/2022" grilleHoraire="horaires_WPY_H24"/>'))
    # print(get_machines(root))

    # services
    # print(get_services(root))

    # chantier
    print(get_chantier(root, nomSite="WPY_FOR"))
    get_chantier(root, nomSite="WPY_DEP")
    get_chantier(root, nomSite="WPY_REC")
    # get_chantier(root, nomSite="wefw") # error


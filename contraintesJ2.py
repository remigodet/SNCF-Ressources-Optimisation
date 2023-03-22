import warnings
from gurobipy import *
import gurobipy as gb
import utils
from tqdm.notebook import tqdm


def generate_contraintes(m, dataframes, var_dict, links_dict):
    #tqdm 
    NB_CONTRAINTES = 4
    p_bar = tqdm(range(NB_CONTRAINTES), desc="BUILDING CONSTRAINTS FOR J2")
    
    # data 
    taches_df = dataframes["taches_df"]
    roulements_df = dataframes["roulements_df"]
    taches_humaines =  taches_df["Type de tache humaine"]
    # links_dict = tache_name,tache,roulement,a,jour,c
    
    # ##### c1: 1 JS par tache ####
    for tache_name in taches_humaines:
        for target_tache in var_dict[tache_name].keys():
            temp = []
            for tache_name_key, tache_key, r,a,j,c in links_dict.keys():
                if tache_name_key==tache_name and tache_key==target_tache:
                    # somme des jds sur cette tache unique 
                    temp.append(links_dict[tache_name, target_tache, r,a,j,c])
            # print("TEMP", end="")
            # print(temp)
            # print(len(temp))
            if temp==[]:
                print("ALERT, TEMP =[], pas de JDS !!!")
                print(tache_name, target_tache)
            nb_of_jds = gb.quicksum(temp)
            m.addConstr(nb_of_jds==1)    
    
    p_bar.update(1)
    p_bar.refresh()
    ##### c2 : tache au bon moment ####
    for tache_name in taches_humaines:
        for target_tache in var_dict[tache_name].keys():
            for tache_name_key, tache_key, r,a,j,c in links_dict.keys():
                if tache_name_key==tache_name and tache_key==target_tache:
                    minute_start, minute_end = utils.get_min_from_rajc(r,j,c,roulements_df)
                    m.addConstr(minute_start*links_dict[tache_name_key, tache_key, r,a,j,c] <= var_dict[tache_name][target_tache])
                    duree = int(taches_df[taches_df["Type de tache humaine"]==tache_name]["Durée"].iloc[0])
                    m.addConstr((var_dict[tache_name][target_tache]+duree)*links_dict[tache_name_key, tache_key, r,a,j,c] <= minute_end)
    
    p_bar.update(1)
    p_bar.refresh()
    ##### c3 : 1 cycle par jour par agent ####
    for roulement in roulements_df["Roulement"]:
        for a in range(1, roulements_df[roulements_df["Roulement"]==roulement]["Nombre agents"].iloc[0]+1):
            for j in range(1,len(set(dataframes["sillons_df"]["JDEP"]))):
                # raj
                all_cycle_indicatrices = []
                for c in range(1,4):
                    if str(j%7) in roulements_df[roulements_df["Roulement"]==roulement]["Jours de la semaine"].iloc[0].split(";"):
                        #rajc                        
                        temp = []
                        for chantiers in roulements_df[roulements_df["Roulement"]==roulement]["Connaissances chantiers"]:
                            for chantier in chantiers.split(";"):
                                for tache_name in taches_df[taches_df["Chantier"]==chantier]["Type de tache humaine"]:
                                    for target_tache in var_dict[tache_name].keys():
                                        # all vars 
                                        if (tache_name,target_tache,roulement,a,j,c) in  links_dict.keys():
                                            temp.append(links_dict[tache_name,target_tache,roulement,a,j,c])
                        # indicatrice == sum of JDS of cycle
                        if temp==[]:
                                message = f"temp is null for: {roulement},{a},{j},{c}"
                                warnings.warn(message=message )
                            
                        var = m.addVar(vtype=GRB.BINARY,name= "HELPER with single cycle per worked day")
                        all_cycle_indicatrices.append(var)
                        m.addConstr((var==1)>>(gb.quicksum(temp)>=1))
                        m.addConstr((var==0)>>(gb.quicksum(temp)<=0))       
                # raj                    
                #sum indicatrice  + constraint  
                m.addConstr(gb.quicksum(all_cycle_indicatrices)<=1)     
    p_bar.update(1)
    p_bar.refresh()                    
    # ##### c4 : non superposition  ####
    # print("Starting C4")
    # B = {}
    # def b(tache_i, tache_j, tache_i_name, tache_j_name, duree=0):
    #     '''
    #     Creates or gets the variable indicating that tache_i <= tache_j
    #     With a potential duree after tache_i
    #     None name is for constants
    #     '''
    #     # tt = time.time_ns()
    #     # print(tache_j, tache_i, tache_j_name, tache_i_name)
    #     if (tache_j, tache_i, tache_j_name, tache_i_name, duree) in B.keys():
    #         bb = B[tache_j, tache_i, tache_j_name, tache_i_name, duree]
    #         # print("pop", end="")
    #         return 1-bb
    #     # has not returned
    #     bb = m.addVar(vtype=GRB.BINARY, name=f"HELPER {tache_i},{tache_j}")
    #     B[tache_i, tache_j, tache_i_name, tache_j_name, duree]= bb
    #     #  some have to be derived from the gurobi variables, others are directly constants
    #     try: 
    #         # if tache_i_name != None:
    #         #     
    #         # else:
    #         #     tache_i_var = m.addVar(vtype=GRB.INTEGER, name=f"HELPER2 {tache_i},{tache_j}")
    #         #     m.addConstr(tache_i_var==tache_i, name="var_const")
    #         # if tache_j_name != None:
    #         #     
    #         # else:
    #         #     tache_j_var = m.addVar(vtype=GRB.INTEGER, name=f"HELPER2 {tache_i},{tache_j}")
    #         #     m.addConstr(tache_j_var==tache_j, name="var_const")
    #         # only from dict in J2.C4 
    #         tache_i_var = var_dict[tache_i_name][tache_i]
    #         tache_j_var = var_dict[tache_j_name][tache_j]
    #         m.addConstr((bb == 1) >> (tache_i_var+duree <= tache_j_var),
    #                     name="indicator_constr1")
    #         m.addConstr((bb == 0) >> (tache_i_var+duree >= tache_j_var+ 0.5),
    #                     name="indicator_constr2")
    #     except:
    #         print("ERROR")
    #         print(tache_i, tache_j, tache_i_name, tache_j_name)
    #         raise
    #     # tt2 = time.time_ns()
    #     # if tt2-tt > 1000:
    #     #     print(tache_j, tache_i, tache_j_name, tache_i_name)
    #     # print("time of b in ns", tt2 - tt)
    #     return bb
    # # get task
    # # one constraint per JS
    # # links_dict = tache_name,tache,roulement,a,jour,c
    # import time
    # t = time.time()
    # for tache_name,target_tache,roulement,a,jour,c in tqdm(sorted(links_dict.keys(), key=lambda x:(x[3],x[5],x[4]))): #with tqdm
    # # for tache_name,target_tache,roulement,a,jour,c in links_dict.keys():
    
    #     # Par chantier : 
    #     # chantier = taches_df[taches_df["Type de tache humaine"]==tache_name]["Chantier"].iloc[0]
    #     # # get all others tasks from that chantier in that JDS
    #     # other_tache_list = []
    #     # for chantier_tache in taches_df[taches_df["Chantier"]==chantier]["Type de tache humaine"]:
    #     #     for tache in var_dict[chantier_tache].keys():
    #     #         if  (chantier_tache,tache,roulement,a,jour,c) in links_dict.keys():
    #     #             other_tache_list.append((tache, chantier_tache))
    #     # V2 :
    #     # get all others tasks in that JDS
    #     other_tache_list = []
    #     for chantier_tache in taches_humaines:
    #         for tache in var_dict[chantier_tache].keys():
    #             if  (chantier_tache,tache,roulement,a,jour,c) in links_dict.keys():
    #                 other_tache_list.append((tache, chantier_tache))
    #     # print("KEY", tache_name,target_tache,roulement,a,jour,c)
    #     # print(len(other_tache_list))
    #     # print(other_tache_list)
    #     # t = time.time()
    #     # print("start_sum")
    #     pos_neg_sum = gb.quicksum([
    #         (b(other_tache, target_tache, other_tache_name, tache_name)
    #         -
    #         b(other_tache, 
    #             target_tache,
    #             other_tache_name,
    #             tache_name,
    #             int(taches_df[taches_df["Type de tache humaine"]==other_tache_name]["Durée"].iloc[0])
    #             ))
    #         *
    #         links_dict[other_tache_name,
    #                     other_tache, 
    #                     roulement,a,jour,c]
    #         for other_tache, other_tache_name in other_tache_list
    #     ])
    #     # t2 = time.time()
    #     # print(t2 - t)
    #     # print("end_sum")
    #     m.addConstr(pos_neg_sum<=1)
        
        
    #     # print("---")
    #     # print(tache_name,target_tache,roulement,a,jour,c)
    #     # print(len(other_tache_list))
    #     # print(time.time()-t)
    #     # t=time.time()
    p_bar.update(1)
    p_bar.refresh()    
        # get all other chantier task + links to check
        # add sums
    m.update()
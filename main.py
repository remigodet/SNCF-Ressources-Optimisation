import data
import variables
import contraintes
from gurobipy import *


# create model
m = Model()

# get data from excel
dataframes = data.get_all_pandas()

# generate variables (integers)
var_dict = variables.generate_variables(m, dataframes)
contraintes.generate_contraintes(m, dataframes, var_dict)
print(var_dict)



m.setObjective(lambda x : 1, GRB.MINIMIZE)

m.update()
m.optimize()

print(m.objVal)

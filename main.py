import data
import variables
from gurobipy import *


# create model
m = Model()

# get data from excel
dataframes = data.get_all_pandas()

# generate variables (integers)
var_dict = variables.generate_variables(m, dataframes)
print(var_dict)

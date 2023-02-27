import data

dataframes = data.get_all_pandas()
print(dataframes["chantiers_df"].head())
print(dataframes["correspondances_df"].head())
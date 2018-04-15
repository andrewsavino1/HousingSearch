import pandas as pd

file_loc = "/Users/akshatgoel/Desktop/missing_price.csv"

price_list = pd.read_csv(file_loc)

price_dict = dict(zip(price_list.Neighborhood, price_list.Price))



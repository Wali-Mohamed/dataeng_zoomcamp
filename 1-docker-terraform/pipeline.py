import sys
import pandas as pd

df=pd.DataFrame({"day": [1, 2, 3], "number of passengers": [4, 5, 6]})
month = int(sys.argv[1])
df['month'] = month
df.to_parquet("output.parquet")
print(df.head())

print(f"Running pipeline for day {month}")



# source .venv/Scripts/activate
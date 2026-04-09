import pandas as pd
df = pd.read_csv("student.csv")
print(df)
# print(df.shape)

# print(df.head(7))

# print(df.tail(7))
# print(df.loc[3])
# print(df["gpa"])
# print(df.loc[3, "age"])

# for all rows
# print(df.loc[ :, "age"])

# result = df[df["age"] > 20]
# print(result)
# total_nul_values =  df.isna().sum()
# print(df["age"].isna().sum())
# print(df.loc[4].isna())
# for data cleaning
# print(df.dropna())
# print(df.loc[:, "remarks"].dropna())
# print(df.dropna(subset = ["remarks"]))
# print(df.drop("age" , axis= 1))

# print(df["age"].max())
# print(df["age"].max())
# to fill the empaty cells
print(df["fees"].fillna(df["fees"].mean()))
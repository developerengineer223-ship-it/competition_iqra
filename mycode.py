import pandas as pd
data  = {
    "name" : ["ahmad","hafeez","nadeem"],
    "age" : [22,18,25],
    "city": ["khushab","sargodha","karachi"]
}



df = pd.DataFrame(data)
# print(df)

# df.loc[df["age"] > 18 , "status"] = "adults"

# print(df)


print(df.shape)

print(df.head(7))

print(df.tail(7))


df.rename(columns={"full_name": "Name"},inplace=True)

df.to_csv("studentdata.csv",index=False)

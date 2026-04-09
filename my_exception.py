# Sam for exception handling
# try:
#     age = input("enter age:")
#     print(f"your age = {age + 2}")
# except  TypeError:
#     print(f"please enter valid or correct format age")


# —-----
# try:
#     age = int(input("enter age:"))
#     print(f"your age = {age}")
# except  ValueError:
#     print(f"please enter valid or correct format age")
file = open("filename1.text", 'r')
# file.write("this is my file")
readedata = file.read()
print(readedata)


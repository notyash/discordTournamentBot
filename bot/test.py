list = ['YASH', "NOT YASH"]
a = ', '.join(x for x in list)
print(list[len(list)-1])
for channel in list:
    if list[len(list)-1] == channel:
        print("yes")
        print(f"added channel: {a}")
    else:
        print("no")


list_1=[]
numbers=int(input("how many numbers do you want to enter: "))
for i in range(numbers):
    number=int(input(f"Enter number{i+1} : "))
    list_1.append(number)
bishtarin=max(list_1)
kamtarin=min(list_1)
miangin=sum(list_1)/len(list_1)
print(f"bishtarin : {bishtarin}  kamtarin : {kamtarin}  miangin : {miangin} ")

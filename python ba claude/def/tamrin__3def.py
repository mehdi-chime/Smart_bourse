e=0
o=0
def e(a):
    for item in a:
        if(a%2==0):
            e +=1
        else:
            o +=1
    return a
l=[]
nums = int(input("enter numbers"))
for i in range (nums):
    num = int(input(f"enter number{i+1}"))
    l.append(num)
e(l)


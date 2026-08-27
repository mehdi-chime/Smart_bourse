# in barname baraye hesab kardan inke yek listi az adad begire, bad beshmare chandta zire 10 chanta bala 10 darad
list_1=[]
j=0
k=0
numbers=int(input("how many numbers do you want to enter : "))
for i in range(numbers):
    number=int(input(f"enter your number {i+1}: "))
    list_1.append(number)
    if number>=10:
        j+=1
    else:
        k+=1
print(f"nomarate bala 10 : {j} nomarate kamtar az 10 : {k}")


import random
import numpy as np
def interpre_input():
    nums = numbers = np.random.permutation(9) 
    matran = matran = nums.reshape(3, 3)
    return matran

def otrong(matran):
    for i in range (0,3):
        for j in range(0, 3):
            if matran[i][j] == 0:
                return (i,j)
def rule(x, y):
    rules =[]
    if x > 0:
        rules.append("Move up")
    if x < 2:
        rules.append("Move down")
    if y > 0:
        rules.append("Move left")
    if y <2:
        rules.append("Move right")
    return rules;
def action(rule,matran,row,col):
    choice = random.choice(rule)
    if choice == "Move up":
        matran[row,col] = matran[row - 1, col]
        matran[row - 1, col] = 0
    if choice == "Move down":
        matran[row,col] = matran[row + 1, col]
        matran[row + 1, col] = 0
    if choice == "Move left":
        matran[row,col] = matran[row, col - 1]
        matran[row, col - 1] = 0
    if choice == "Move right":
        matran[row,col] = matran[row, col + 1]
        matran[row, col + 1] = 0  
    print("Dua vao vao luat toi se:",choice)
    print("Ma tran sau khi di chuyen:\n ", matran)
    return matran


matran = interpre_input();
print("ma tran cu:\n", matran)
while(True):
    row, col = otrong(matran)
    rules = rule(row,col)
    action(rules,matran,row,col)
    n = -1
    while(n != 1 and n != 0):
         n = int(input("Ban co muon tiep tuc? 1: yes, 0: no: "))
    if (n == 1):
        continue
    if (n == 0):
        break


import random
import numpy as np
import copy
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
def get_next_state(matran, choice, row, col):
    """Hàm bổ trợ để xem trước ma trận sẽ ra sao nếu chọn choice"""
    temp_matran = copy.deepcopy(matran)
    if choice == "Move up":
        temp_matran[row,col], temp_matran[row-1, col] = temp_matran[row-1, col], 0
    elif choice == "Move down":
        temp_matran[row,col], temp_matran[row+1, col] = temp_matran[row+1, col], 0
    elif choice == "Move left":
        temp_matran[row,col], temp_matran[row, col-1] = temp_matran[row, col-1], 0
    elif choice == "Move right":
        temp_matran[row,col], temp_matran[row, col+1] = temp_matran[row, col+1], 0
    return temp_matran

matran = interpre_input();
lichsu_trangthai = set()
print("ma tran ban dau:\n", matran)
lichsu_trangthai.add(tuple(matran.flatten()))
while(True):
    row, col = otrong(matran)
    rules = rule(row,col)
    valid_rules = []
    for r in rules:
        du_doan_matran = get_next_state(matran, r, row, col)
        if tuple(du_doan_matran.flatten()) not in lichsu_trangthai:
            valid_rules.append(r)
    action(valid_rules,matran,row,col)

    lichsu_trangthai.add(tuple(matran.flatten()))
    print("Số trạng thái đã lưu trong bộ nhớ:", len(lichsu_trangthai))
    n = -1
    while(n != 1 and n != 0):
         n = int(input("Ban co muon tiep tuc? 1: yes, 0: no: "))
    if (n == 1):
        continue
    if (n == 0):
        break


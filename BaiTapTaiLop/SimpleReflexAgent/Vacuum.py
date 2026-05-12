
import random
import numpy as np
def interpre_input():
    x = random.randint(0,3)
    y = random.randint(0,3)
    state = np.random.randint(0,2,(4,4))
    return x,y,state

def PosVacuum(x,y):
    x = random.randint(0,3)
    y = random.randint(0,3)
   
def Pmove(x,y):
    moves = []
    if y < 3: moves.append('R')
    if y > 0: moves.append("L")

    if x < 3: moves.append("D")
    if x > 0: moves.append("U")
    return moves

def rules(state,x,y):
    if state[x][y] == 1:
        state[x][y] = 0
        print("Vi tri",x,y,"da duoc don dep \n",state)
    moves = Pmove(x,y)
    action = random.choice(moves)
    return action
    
def Action(move,x,y):
    if move == "D":
        x += 1
    if move == "U":
        x -= 1
    if move == "R":
        y += 1
    if move == "L":
        y -= 1
    return x,y

def main():
    x,y,state = interpre_input()
    print("Vi tri bat dau cua may hut bui:", x,y ,"\n")
    print("Vi tri cac diem ban dau:\n", state)
    
    while(np.any(state != 0)):
        move = rules(state,x,y)
        print("Tiep theo toi se:",move)
        x, y = Action(move,x,y)
        print("Vi tri hien tai cua toi la:", x,y)

main()





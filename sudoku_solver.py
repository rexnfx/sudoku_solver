
import pandas as pd
import numpy as np
from collections import namedtuple

# Load the CSV file
df = pd.read_csv('sudoku.csv', header=None) # Replace with your actual file name
potential = namedtuple('potential',['r','c','v'])

def get_pod(i):
    if i < 3:
        return 0
    elif i < 6:
        return 1
    else:
        return 2
    
def validate_column(grid, col):
    m = set()
    for r in range(9):
        if len(grid[r][col]) == 1:
            if grid[r][col][0] in m:
                #print('invalid', r, col, grid[r][col][0], m)
                return False
            else:
                m.add(grid[r][col][0])
    return True
            
def validate_row(grid, row):
    m = set()
    for c in range(9):
        if len(grid[row][c]) == 1:
            if grid[row][c][0] in m:
                #print('invalid', row, c, grid[row][c][0], m)
                return False
            else:
                m.add(grid[row][c][0])
    return True
            
def validate_pod(grid, row, col):
    m = set()
    pod_r = get_pod(row)
    pod_c = get_pod(col)
    try:
        for r in range(3):
            for c in range(3):
                pr = r + pod_r * 3
                pc = c + pod_c * 3
                if len(grid[pr][pc]) == 1:
                    if grid[pr][pc][0] in m:
                        #print('invalid', row, col, r, c, pr, pc, grid[row][col][0], m)
                        return False
                    else:
                        m.add(grid[pr][pc][0])
    except:
        print("error", pr, pc, row, col, grid[row][col])
    return True
    
def eliminate(grid):
    invalid = False
    changed = True
    loop = 0
    while changed:
        changed = False
        for r in range(9):
            for c in range(9):
                #check if solved
                if len(grid[r][c]) > 1:
                    #check row
                    for i in range(len(grid[r][c])):
                        v = grid[r][c][i]

                        for col in range(9):
                            if col != c and len(grid[r][col]) == 1:
                                if grid[r][col][0] == v:
                                    changed = True
                                    break
                        if changed:
                            grid[r][c].pop(i)
                            if validate_row(grid, r):
                                #print('removed row', r, c, v, loop)
                                break
                            else:
                                invalid = True
                                #print('invalid row', r, c)
                                return (False, grid, '', invalid)

                if changed:
                    break

                if len(grid[r][c]) > 1:
                    #check column
                    for i in range(len(grid[r][c])):
                        v = grid[r][c][i]
                        for row in range(9):
                            if row != r and len(grid[row][c]) == 1:
                                if grid[row][c][0] == v:
                                    changed = True
                                    break
                        if changed:
                            grid[r][c].pop(i)
                            if validate_column(grid, c):
                                #print('removed col', r,c, v, loop)
                                break
                            else:
                                invalid = True
                                #print('invalid col', r, c)
                                return (False, grid, '', invalid)

                if changed:
                    break
                
                if len(grid[r][c]) > 1:
                    #check pod
                    for i in range(len(grid[r][c])):
                        v = grid[r][c][i]
                        pod_r = get_pod(r)
                        pod_c = get_pod(c)
                        for row in range(3):
                            for col in range(3):
                                pr = row + pod_r * 3
                                pc = col + pod_c * 3
                                if pr != r and pc != c and len(grid[pr][pc]) == 1:
                                    if grid[pr][pc][0] == v:
                                        changed = True
                                        break
                        if changed:
                            grid[r][c].pop(i)
                            if validate_pod(grid, r,c):
                                #print('removed pod', r, c, v, i, loop)
                                break
                            else:
                                invalid = True
                                #print('invalid pod', r, c)
                                return (False, grid, '', invalid)

                if changed:
                    break
            if changed:
                    break

        loop += 1
    #print('not changed')

    #check if solved
    solved = True
    not_solved = ''
    for r in range(9):
        for c in range(9):
            if len(grid[r][c]) > 1:
                #print('cell not solved', r, c, grid[r][c])
                not_solved += str(r)+str(c)
                solved = False
            if len(grid[r][c]) == 0:
                #print('dead cell', r, c)
                solved = False
                invalid = True

    return (solved, not_solved, invalid)

def guess(grid, possibility):
    test_grid = copy_grid(grid)
    test_grid[possibility.r][possibility.c] = [possibility.v]
    for r in range(9):
        if possibility.v in test_grid[r][possibility.c] and r != possibility.r:
            test_grid[r][possibility.c].pop(test_grid[r][possibility.c].index(possibility.v))

    if not validate_column(test_grid, possibility.c):
        return (False, False)

    for c in range(9):
        if possibility.v in test_grid[possibility.r][c] and c != possibility.c:
            test_grid[possibility.r][c].pop(test_grid[possibility.r][c].index(possibility.v))

    if not validate_row(test_grid, possibility.r):
        return (False, False)
    
    for r in range(3):
        for c in range(3):
            pr = get_pod(r)
            pc = get_pod(c)
            if possibility.v in test_grid[pr][pc] and pr != possibility.r and pc != possibility.c:
                test_grid[pr][pc].pop(test_grid[pr][pc].index(possibility.v))

    if not validate_pod(test_grid, possibility.r, possibility.c):
        return (False, False)
    
    done, ns, inval = eliminate(test_grid)
    ps = ns
    if done and not inval:
        return (True, True)
    if inval:
        return (False, False)
    
    while not done and not inval:
        done, ns, inval = eliminate(test_grid)
        if done and not inval:
            return (True, True)
        if inval:
            return (False, False)
        if ns == ps:
            break
        
    return (False, True) #solved is false, possible is true

def copy_grid(grid):
    return [[[ x for x in middle_list] for middle_list in outer_list] for outer_list in grid]

g = [[[0] for _ in range(9)] for _ in range(9)]
for r in range(9):
    for c in range(9):
        value = df.iloc[r, c] 
        if value == 0 or pd.isna(df.iloc[r, c]):
            g[r][c][0] = 1
            for x in range(8):
                g[r][c].append(x+2)
        else:
            g[r][c][0] = int(value)

solved, ns, invalid = eliminate(g)

attempt_count = 0

while not solved:
    print(attempt_count, " elimination attempt not solved")
    prev_ns = ns
    solved, ns, invalid = eliminate(g)
    if ns == prev_ns:
        break
    attempt_count += 1
    if invalid:
        print('elimination attempts',attempt_count, 'not valid')
        break

if not solved:
    extracted_list = [[str(inner_list) for inner_list in outer_list] for outer_list in g]
    df = pd.DataFrame(extracted_list)  
    
    print("elimination approach did not solve")

    potentials = []
    for r in range(9):
        for c in range(9):
            #check if solved
            if len(g[r][c]) > 1:
                for i in range(len(g[r][c])):
                    potentials.append(potential(r, c, g[r][c][i]))

    """
    while not solved:
        not_eliminated = []
        eliminated = []
        pot_count = len(potentials)
        for p in potentials:
            solved, possible = guess(g, p)
            if possible:
                print('not eliminated', p)
                not_eliminated.append(p)
            else:
                print('eliminated', p)
                eliminated.append(p)

         
        for e in eliminated:
            try:
                i = g[e.r][e.c].index(e.v)
                g[e.r][e.c].pop()
                print('popped', e)
            except:
                print('not popped', e)

        for r in range(9):
            for c in range(9):
                #check if solved
                if len(g[r][c]) > 1:
                    for i in range(len(g[r][c])):
                        potentials.append(potential(r, c, g[r][c][i]))

        print('remaining potentials', len(not_eliminated))
        if len(potentials) == pot_count:
            print('no progress')
            break
"""
if solved:
    print("solved")
    extracted_list = [[inner_list[0] for inner_list in outer_list] for outer_list in g]
    df = pd.DataFrame(extracted_list)    
    df.to_excel('solution.xlsx', index=False)
    
else:
    extracted_list = [[str(inner_list) for inner_list in outer_list] for outer_list in g]
    df = pd.DataFrame(extracted_list)  
    df.to_excel('state.xlsx', index=False)

from scipy.optimize import linprog
import numpy as np
import numpy.linalg as la
import itertools
'''
Add a pseudo, cost-free recipe in the matrix for matrix 

matrix: the matrix that needed to be added
raw_idx: the designated idx of the raw_material in the matrix

Returns the new matrix with the pseudo recipe
'''
def AddRaw(matrix: np.array, raw_idx: int) -> np.array:
    new_col = np.zeros((matrix.shape[0], 1)) # row length
    new_col[raw_idx] = 1
    return np.append(matrix, new_col, axis=1)

'''
Add pseudo, cost-only recipes for all item in matrix

matrix: the matrix that needed to be added

Returns the new matrix with the pseudo recipe
'''
def AddWaste(matrix: np.array, waste_idx: int):
    new_col = np.zeros((matrix.shape[0], 1))
    new_col[waste_idx] = -1 
    return np.append(matrix, new_col, axis=1)

'''
Find the recipe in the matrix that have alternate

matrix: the recipe matrix

Returns the col idx of these recieps in a list
'''
def FindAlt(matrix: np.array) -> list:
    res = []
    # iterate each row
    # if there is more than one cell in a row with value > 0
    # that means the corresponding recipe in that col
    # is what we need to find 
    for row in range(matrix.shape[0]):
        potential_res = []
        c = 0
        for col in range(matrix.shape[1]):
            if matrix[row, col] > 0:
                c += 1
                potential_res.append(col)
        if c >= 2:
            res.extend(potential_res)
    
    return list(set(res))

'''
Find the location of resources that needed to be add as waste (result of a recipe that has more than one result)

matrix:

Returns the idx in list
''' 
def FindWaste(matrix:np.array) -> list:
    res = []
    for col in range(matrix.shape[1]):
        potential_res = []
        c = 0
        for row in range(matrix.shape[0]):
            if matrix[row, col] > 0:
                c += 1
                potential_res.append(row)
        if c >= 2:
            res.extend(potential_res) 
    return list(set(res))

'''
---NEED DOCUMENTATION---
'''
def AddTaxes(matrix:np.array):
    new_row = -np.ones((1, matrix.shape[1]))
    matrix = np.append(matrix, new_row, axis=0)
    matrix = AddRaw(matrix, -1)
    return matrix

'''
Compare the two ans using the given priority.

a: ans 1
b: ans 2
priority: a list that contains which element should be compare first; move the next element if the current element is equal

Returns the ans that wins
'''
def CompAns(a:np.array, b:np.array, priority:list) -> np.array:
    for idx in priority:
        if a[idx] < b[idx]:
            return a
        elif a[idx] > b[idx]:
            return b
    return b



'''
A wrapper for 2d numpy array

Can Add and mark raw pseudo recipe
Can Add and mark waste pseudo recipe
Can locate alt recipes
Can calculate
'''
class RecipeMatrix:



    '''
    Initialize the object, add pseduo recipe and locate alt recipes in the matrix

    self:
    matrix: the recipe matrix, or graph matrix
    raw_idxes: the idxes have the elment you want to appoint as raw material
    '''
    def __init__(self, matrix:np.array, raw_idxes:list) -> None:
        self.matrix = np.copy(matrix)

        # self.alt_idxes = FindAlt(matrix) # This is only used for LA, finding recipes that have alternatives

        # self.waste_idxes = [] # This is only used for LA
        # self.original_waste_idxes = FindWaste(matrix) # This is only used for LA

        # for i in self.original_waste_idxes: # dont need this for LP
        #     self.waste_idxes.append(self.matrix.shape[1])
        #     self.matrix = AddWaste(self.matrix ,i)

        self.raw_idxes = []
        for i in raw_idxes:
            self.raw_idxes.append(self.matrix.shape[1])
            self.matrix = AddRaw(self.matrix, i)
        
        # Add taxes to all recipe
        self.matrix = AddTaxes(self.matrix)
        
        
    '''
    Zero out (delete) the combinations of recipes (col) in matrix

    Returns an iterable of the new matrixes
    '''
    def ZeroOut(self) -> list:
        specials = []
        specials.extend(self.alt_idxes)
        specials.extend(self.waste_idxes)
        print(len(specials), self.matrix.shape[1] - self.matrix.shape[0])
        combs = itertools.combinations(specials, self.matrix.shape[1] - self.matrix.shape[0])
        for comb in combs:
            yield (np.delete(self.matrix, comb, axis=1), np.sort(comb)) 

    '''
    Solve Ax = b with the given priority

    matrix: should already have raw pseudo recipe
    target: the desire output, must have the same size as the number of row in matrix
    priority: the priority of the item in a list, item not in list would be not be considered

    Returns the amount needed for each recipe in an array
    '''
    # This function is currently disabled. Calling it WILL cause error.
    def Solve_Old(self, target, priority) -> np.array:
        final_ans = np.zeros(self.matrix.shape[1])
        final_ans.fill(np.inf)
        for z in self.ZeroOut():
            sub_matrix = z[0]
            comb = z[1]
            
            print(comb)
            try:
                ans = la.solve(sub_matrix, target)
            except la.LinAlgError:
                continue
            true_ans = np.zeros(self.matrix.shape[1])
            comb_idx = 0
            ans_idx = 0
            for i in range(self.matrix.shape[1]):
                if comb_idx < len(comb) and i == comb[comb_idx]:
                    comb_idx += 1
                else:
                    true_ans[i] = ans[ans_idx]
                    ans_idx += 1
            # print(true_ans)
            test_flag = True
            for i in range(len(true_ans)):
                if true_ans[i] < 0:
                    print(i, end=" ")
                    test_flag = False
                    break
            if test_flag:
                final_ans = CompAns(final_ans, true_ans, priority)
        return final_ans

    '''
    Constructs the object function with priority list. The item on the higher level would have 10x the "value" of the lower level.

    priority: only one item per level. ITEM IN LIST MUST ALSO BE IN self.raw_idxes
    level_ration: determines the difference between levels; default value = 10.

    Returns the object functon params.
    '''
    def ObjFunc(self, priority:list, level_ratio=10) -> np.array:
        # scipy default set to minimize object function, so no need to inverse sign
        l = len(priority)
        res = np.zeros(self.matrix.shape[1])
        for i in range(l):
            p = priority[i]
            if p not in self.raw_idxes:
                raise KeyError("Item %i not in self.raw_idxes"%p)
            res[p] = pow(level_ratio, l - i)
        # tax
        res[-1] = 1
        return res

    '''
    Construc the left and right inequalities for LP

    target: used to construct right hand inequalities

    Returns two matrix, representing each ineq
    '''
    def Inequalities(self, target) -> np.array:
        # scipy default set to less or equal to, <=, but we want >=
        # so we need to multiply our result by -1
        lhs_ineq = -self.matrix[:-1, :]
        rhs_ineq = -target
        return lhs_ineq, rhs_ineq


    '''
    ---NEED DOCUMENTATION---
    '''
    def Equalities(self) -> np.array:
        # TAXES!
        lhs_eq = [self.matrix[-1, :]]
        rhs_eq = [0]
        return lhs_eq, rhs_eq



    '''
    Solving the problem with linear programming

    target: the desire output in a np.array
    priority: the prioritiy used to construct the object function params

    Returns the amount needed for each recipe in an array
    '''
    def Solve(self, target, priority):
        lhs_ineq, rhs_ineq = self.Inequalities(target)
        lhs_eq, rhs_eq = self.Equalities()
        obj_func = self.ObjFunc(priority)
        # the bound of x_i, are by default 0 - inf
        opt = linprog(c=obj_func, A_ub=lhs_ineq, b_ub=rhs_ineq, A_eq=lhs_eq, b_eq= rhs_eq, method="revised simplex")
        return opt

    def PrintAns(self, ans, recipe_name_list):
        for i in range(len(ans)):
            if ans[i] == 0:
                continue
            if i < len(recipe_name_list):
                print(recipe_name_list[i], ans[i])
            elif i in self.waste_idxes:
                print(i, ans[i])
            elif i in self.raw_idxes:
                print(i, ans[i])
    # '''
    # Debug function
    # '''
    # def ItemIdxToStr(self, i):
    #     if i in self.waste_idxes:
    #         org_i = self.original_waste_idxes(self.waste_idxes.index(i))
    #         return self.items[org_i]
    #     elif i < len(self.items):
    #         return self.items[i]
    #     else:
    #         return "?Not found?"

    # '''
    # Debug function
    # '''
    # def PrintPriority(self, priority):
    #     of = self.ObjFunc(priority)
    #     for i in range(len(of)):
    #         if of[i] == 0:
    #             continue
    #         print(of[i], self.ItemIdxToStr(i))
    #     pass


    







if __name__ == "__main__":

    '''
    This is a test scene toke from the game factrio
    item: heavy, light, gas, water, oil
    raw: water, oil
    recipe:
        40 heavy + 30 water = 30 light
        30 light + 30 water = 20 gas
        100 oil = 30 heavy + 30 light + 40 gas
        100 oil + 50 water = 10 heavy + 45 light + 55 gas

    Multiple recipe for one item
    '''

    A1 = np.array([
        [-40, 0, 30, 10],
        [30, -30, 30, 45],
        [0, 20, 40, 55],
        [-30, -30, 0, -50],
        [0, 0, -100, -100],
    ])
    # 10 heavy and 100 gas
    b = np.array([0, 0, 300, 0, 0])
    p = [5 ,4] # oil > water

    rm = RecipeMatrix(A1, [3, 4])
    print(rm.matrix.shape)

    ans = rm.Solve(b, p)
    print(ans.x)
    print(rm.matrix @ ans.x)

    
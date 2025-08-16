import networkx as nx
import gudhi as gd
from functools import reduce

def neighborComplexSimp(graph):
    simplex_tree_ret = gd.SimplexTree()
    for g in graph.nodes:
        neigCopy = (list(graph.adj[g])).copy()
        neigCopy.append(g)
        neigCopy.sort()
        simplex_tree_ret.insert(neigCopy)

    return simplex_tree_ret

def cliqueComplexSimp(graph):
    simplex_tree_ret = gd.SimplexTree()
    cliques = nx.enumerate_all_cliques(graph)
    #adds a lot of repetitive cliques, but it is fine
    for i in cliques:
        simplex_tree_ret.insert(i)
    return simplex_tree_ret

def independentComplexSimp(graph):
    cG = nx.complement(graph)
    simplex_tree_ret = cliqueComplexSimp(cG)
    return simplex_tree_ret

def acyclicComplexSimp(graph):
    simplex_tree_ret = gd.SimplexTree()
    acyclicComplexSimpBacktrack(graph,[],simplex_tree_ret)
    return simplex_tree_ret

def acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree):
    successes=0
    #a ideia e manter que sempre o conjunto é acíclico
    #então se um suspeito fizer um ciclo ele faz parte do ciclo e logo tem pelo menos 2 vizinhos
    #esse critério pega muitos falsos positivos
    #mas não é problema pois se foi um falso positivo então o falso positivo é uma floresta
    #por ser uma floresta há uma ordem que passe pelo critério
    #com o backtracking eu pego essa ordem em algum momento
    for v in graph.nodes:
        if len(currentToAdd) < 1:
            successes=successes+1
            currentToAdd.append(v) #edge case safety, likely useless
            simpTree.insert(currentToAdd)
            acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree)
            currentToAdd.pop()
            continue #to not make a tab mess
        print("here I am debugging again")
        print(v)
        print(currentToAdd)
        print(graph)
        if validMove(graph,currentToAdd,v):
            successes=successes+1
            currentToAdd.append(v)
            acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree)
            currentToAdd.pop()
    if successes==0:
        #terminal maybe maximal case (or false positives), optimal insert
        simpTree.insert(currentToAdd)

def validMove(graph,currentSet,suspect):
    if (suspect in currentSet): return False
    count = 0
    for v in currentSet:
        if suspect in graph.adj[v]: count=count+1
    if count > 1: return False
    return True

def check(x,y,graph,suspect):
    if suspect in graph.adj[y] or x==y:
        return x+1


def main():
    G = nx.path_graph(10)
    mset = [2,4,6]
    G.add_edge(3,6)
    print(validMove(G,mset,3))

    G = nx.cycle_graph(6)
    simpTree = acyclicComplexSimp(G)
    print("AM DONE")
    for sk_value in simpTree.get_skeleton(6):
        print(sk_value)
    print("I work")

if __name__=="__main__":
    main()

#NOTES TO SELF: check GraphInducedComplex, maybe useful
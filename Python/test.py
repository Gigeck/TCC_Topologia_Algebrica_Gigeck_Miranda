import networkx as nx
import gudhi as gd

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
    #no idea how to do this one
    pass


def main():
    G = nx.path_graph(10)
    simpTree = independentComplexSimp(G)
    for sk_value in simpTree.get_skeleton(4):
        print(sk_value)
    print("I work")

if __name__=="__main__":
    main()

#NOTES TO SELF: check GraphInducedComplex, maybe useful
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
    cliques = nx.find_cliques(graph)
    for i in cliques:
        simplex_tree_ret.insert(i)
    #toAdd = []
    #for g in graph.nodes:
    #    toAdd = []
    #    toAdd.insert(g)
        #initial piece of clique containing g
    #    for x in graph.adj[g]:
    #        toAdd.append(x)
    #        for y in graph.adj[g]:
    #            if (y in toAdd or y < x): continue
    #            flag = 1
    #            for k in toAdd:
    #                if y not in graph.adj[k]: flag=0
    #            if flag==1:
    #                toAdd.insert(y)
    #        #clique added
    #        simplex_tree_ret.append(toAdd)
    #        toAdd=[]
    #        toAdd.insert(g)
    return simplex_tree_ret

def main():
    G = nx.path_graph(10)
    simpTree = cliqueComplexSimp(G)
    for sk_value in simpTree.get_skeleton(2):
        print(sk_value)
    print("I work")

if __name__=="__main__":
    main()


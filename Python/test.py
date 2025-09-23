import networkx as nx
import gudhi as gd
import matplotlib.pyplot as plt
import random

#global cons
Infinity = 10000

def neighborComplexSimp(graph, simp_tree=None, max_dim=3, filtr=0.0):
    if simp_tree is None:
        simplex_tree_ret = gd.SimplexTree()
        for g in graph.nodes:
            neigCopy = (list(graph.adj[g])).copy()
            neigCopy.append(g)
            neigCopy.sort()
            simplex_tree_ret.insert(neigCopy)
        simplex_tree_ret.prune_above_dimension(max_dim)
        return simplex_tree_ret
    else:
        for g in graph.nodes:
            neigCopy = (list(graph.adj[g])).copy()
            neigCopy.append(g)
            neigCopy.sort()
            if not simp_tree.find(neigCopy):
                simp_tree.insert(neigCopy,filtration=filtr)
        simp_tree.prune_above_dimension(max_dim)
        return simp_tree


def cliqueComplexSimp(graph, simp_tree=None, max_dim=3, filtr=0.0):
    if simp_tree is None:
        simplex_tree_ret = gd.SimplexTree()
        cliques = nx.enumerate_all_cliques(graph)
        #adds a lot of repetitive cliques, but it is fine
        for i in cliques:
            if len(i) > max_dim+1:
                break
            simplex_tree_ret.insert(i)
        return simplex_tree_ret
    
    else:
        cliques = nx.enumerate_all_cliques(graph)
        #adds a lot of repetitive cliques, but it is fine
        for i in cliques:
            if len(i) > max_dim+1:
                break
            if not simp_tree.find(i):
                simp_tree.insert(i,filtration=filtr)
        return simp_tree


def independentComplexSimp(graph, max_dim=3):
    #THIS CANNOT BE USED FOR THE FILTRATION AS IT DOES NOT WORK THAT WAY
    cG = nx.complement(graph)
    simplex_tree_ret = cliqueComplexSimp(cG,max_dim=max_dim)
    return simplex_tree_ret

#def acyclicComplexSimp(graph):
#    simplex_tree_ret = gd.SimplexTree()
#    acyclicComplexSimpBacktrack(graph,[],simplex_tree_ret)
#    return simplex_tree_ret
#
#def acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree,depth=0):
#    successes=0
#    #print(depth)
#    #a ideia e manter que sempre o conjunto é acíclico
#    #então se um suspeito fizer um ciclo ele faz parte do ciclo e logo tem pelo menos 2 vizinhos
#    #esse critério pega muitos falsos positivos
#    #mas não é problema pois se foi um falso positivo então o falso positivo é uma floresta
#    #por ser uma floresta há uma ordem que passe pelo critério
#    #com o backtracking eu pego essa ordem em algum momento
#    for v in graph.nodes:
#        if len(currentToAdd) < 1:
#            successes=successes+1
#            currentToAdd.append(v) #edge case safety, likely useless
#            simpTree.insert(currentToAdd)
#            acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree,depth=depth+1)
#            currentToAdd.pop()
#            continue #to not make a tab mess
#        #print("here I am debugging again")
#        #print(v)
#        #print(currentToAdd)
#        #print(graph)
#        if validMove(graph,currentToAdd,v):
#            successes=successes+1
#            currentToAdd.append(v)
#            acyclicComplexSimpBacktrack(graph,currentToAdd,simpTree,depth=depth+1)
#            currentToAdd.pop()
#    if successes==0:
#        #terminal maybe maximal case (or false positives), optimal insert
#        currentToAdd.sort()
#        simpTree.insert(currentToAdd)

#def validMove(graph,currentSet,suspect):
#    if (suspect in currentSet): return False
#    count = 0
#    for v in currentSet:
#        if suspect in graph.adj[v]: count=count+1
#    if count > 1: return False
#    return True

def sampleAndPlot(complexSimpMethod,quantos,vertices,proba):
    histList = [[],[],[]]
    for n in range(quantos):
        G = nx.fast_gnp_random_graph(vertices,proba)
        simpTree = complexSimpMethod(G)
        #print("AM DONE")
        simpTree.compute_persistence()
        bettis = simpTree.betti_numbers()
        count = 0
        for num in bettis:
            print("numero {0}: {1}".format(count,num))
            histList[count].append(num)
            count=count+1
            if count == 3:
                break
        if count != 3:
            for i in range(3-count):
                histList[count].append(0)
                count=count+1
    plt.hist(histList[0], edgecolor='black')
    plt.xlabel('number')
    plt.ylabel('sample count')
    plt.show()
    plt.hist(histList[1], edgecolor='black')
    plt.xlabel('number')
    plt.ylabel('sample count')
    plt.show()
    plt.hist(histList[2], edgecolor='black')
    plt.xlabel('number')
    plt.ylabel('sample count')
    plt.show()

def randomWeightedGraph(proba=0.3,vert=30,min=1,max=10):
    G = nx.fast_gnp_random_graph(vert,proba)
    for (u,v) in G.edges:
        G.edges[u,v]["weight"] = random.randint(min,max)
    return G

def ripsSimplicialComplex(WG,cutoff):
    distances = dict(nx.all_pairs_bellman_ford_path_length(WG))
    # now transform this in distance matrix
    n = len(WG.nodes)
    matrix = [[Infinity for _ in range(n)] for _ in range (n)]
    for (i,v) in enumerate(WG.nodes):
        for (j,w) in enumerate(WG.nodes):
            if w not in distances[v]:
                continue
            matrix[i][j] = distances[v][w]
            matrix[j][i] = distances[w][v] #makes no difference

    rips_complex = gd.RipsComplex(distance_matrix=matrix, max_edge_length=cutoff)
    ####
    #### HARDCODED CONSTANT BELOW
    ####
    simplex_tree_ret = rips_complex.create_simplex_tree(max_dimension=3)
    return simplex_tree_ret

def displayBettis(simpTree):
    simpTree.compute_persistence()
    bettis = simpTree.betti_numbers()
    for (dim,value) in enumerate(bettis):
        print("numero {0}: {1}".format(dim,value))

def displayGraph(G,mid):
    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > mid]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= mid]

    pos = nx.spring_layout(G, seed=7)
    
    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=6)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=6, alpha=0.5, edge_color="b", style="dashed"
    )

    # node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    ax = plt.gca()
    ax.margins(0.08)
    plt.axis("off")
    plt.tight_layout()
    plt.show()

def displaySimplices(simpTree, maxdim=10, file=None):
    if file is None:
        for sk_value in simpTree.get_skeleton(maxdim):
            print(sk_value)
    else:
        with open(file,"w") as f :
            f.write("Simplices com dimensão máxima {0}:\n".format(maxdim))
            for sk_value in simpTree.get_skeleton(maxdim):
                f.write(repr(sk_value)+"\n")

def edgeFiltration(graph,simplicialFunction):
    newG = nx.Graph()
    newG.add_nodes_from(graph)
    filtration = 1.0
    simplex_tree_ret = gd.SimplexTree()
    edges = sorted(graph.edges(data=True), key=lambda edge: edge[2].get("weight",1))
    #for edge in edges:
    #    print("({0}, {1}) com peso abaixo".format(edge[0],edge[1]))
    #    print(edge[2].get("weight",1))
    for edge in edges:
        newG.add_edges_from([edge])
        #do something with simplex tree
        simplicialFunction(newG,simp_tree=simplex_tree_ret,filtr=filtration)
        filtration=filtration+1.0
    return simplex_tree_ret

def erdosGraphGenerator(prob=0.3,ver=30,mn=1,mx=10):
    G = randomWeightedGraph(proba=prob,vert=ver,min=mn,max=mx)
    while True:
        yield G
        G = randomWeightedGraph(proba=prob,vert=ver,min=mn,max=mx)

def main():

    #G = nx.fast_gnp_random_graph(30,0.3)
    #simpTree = cliqueComplexSimp(G)
    #print("AM DONE")
    #simpTree.compute_persistence()
    #bettis = simpTree.betti_numbers()
    #count = 0
    #for num in bettis:
    #    print("numero {0}: {1}".format(count,num))
    #    count=count+1
    #for sk_value in simpTree.get_skeleton(6):
    #    #print(sk_value)
    #    count = count+1

    output = "output.txt"
    #G = randomWeightedGraph(vert=30)
    eGG = erdosGraphGenerator(ver=10)

    G = next(eGG)
    displayGraph(G,5)
    
    simpTree = edgeFiltration(G,neighborComplexSimp)
    displaySimplices(simpTree,10,output)

    #simpTree = ripsSimplicialComplex(G,14)
    #simpTree = independentComplexSimp(G)
    print("this is fast, right")
    #for sk_value in simpTree.get_skeleton(10):
    #    print(sk_value)

    #displayBettis(simpTree)
    #displaySimplices(simpTree,10,output)
    print("I work")

if __name__=="__main__":
    main()

#NOTES TO SELF: check GraphInducedComplex, maybe useful

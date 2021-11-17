import igraph as ig
from igraph import plot
import json
from os.path import expanduser
from collections import defaultdict
from math import floor, sqrt

FB_USERNAME = ""
PHI = (1 + sqrt(5))/2

def default():
    return "light blue"

def hsv_to_rgb(h, s, v):
    h_i = floor(h*6)
    f = h*6 - h_i
    p = v * (1 - s)
    q = v * (1 - f*s)
    t = v * (1 - (1 - f) * s)
    if h_i == 0:
      r, g, b = v, t, p
    elif h_i == 1:
      r, g, b = q, v, p
    elif h_i == 2:
      r, g, b = p, v, t
    elif h_i == 3:
      r, g, b = p, q, v
    elif h_i == 4:
      r, g, b = t, p, v
    elif h_i == 5:
      r, g, b = v, p, q

    return (int(r*256), int(g*256), int(b*256))

def random(seed):
    global PHI
    hue = seed*PHI - floor(seed*PHI)
    return hsv_to_rgb(hue, 0.5, 0.95)

def neighbors(v, G):
    neighbors = set()
    for e in G.incident(v):
        neighbor = G.es[e].source if G.es[e].source != v else G.es[e].target
        neighbors.add(neighbor)
    return neighbors

def bron_kerbosch(R, P, X, G, found, fout):
    if not P and not X and len(R) > 3:
        found.append(list(R))
        json.dump(list(R), fout)
        fout.write('\n')

    for v in list(P):
        v_neighbors = neighbors(v,G)
        bron_kerbosch(R.union([v]), P.intersection(v_neighbors), X.intersection(v_neighbors), G, found, fout)
        P.remove(v)
        X.add(v)

def tomita(R, P, X, G, found, fout):
    if not P and not X and len(R) > 3:
        found.append(list(R))
        json.dump(list(R), fout)
        fout.write('\n')

    u = 0
    for v in list(P.union(X)):
        if G.degree(v) > G.degree(u) or u not in P:
            u = v
    u_neighbors = neighbors(u,G)
    for v in list(P.difference(u_neighbors)):
        v_neighbors = neighbors(v,G)
        tomita(R.union([v]), P.intersection(v_neighbors), X.intersection(v_neighbors), G, found, fout)
        P.remove(v)
        X.add(v)

def create_fb_network():
    f = open('./friends_edges.txt', 'r')
    names_dict = json.load(open('./friend_names.txt'))

    edges = [eval(line) for line in f]
    G = ig.Graph(edges, directed=False)
    G.vs[0]['name'] = FB_USERNAME
    for v in G.vs:
        for name,n_id in names_dict.iteritems():
            if n_id == v.index:
                v['name'] = name
                break
    return G

def draw_cliques_from_file(filename, num_cliques=None):
    G = create_fb_network()
    f = open(filename, 'r')
    cliques = [eval(line) for line in f]
    cliques = list(reversed(sorted(cliques, key=len)))
    num_cliques = num_cliques if num_cliques != None else len(cliques)

    layt = G.layout('kk', dim=2)
    visual_style = {}
    visual_style["vertex_size"] = 20
    visual_style['edge_width'] = 0.5
    visual_style["margin"] = 10
    visual_style["layout"] = layt
    visual_style["bbox"] = (2500,2500)
    visual_style["vertex_label"] = G.vs["name"]

    palette = ig.RainbowPalette(n=num_cliques)

    color_dict = defaultdict(default)
    for i in xrange(num_cliques):
        clique_color = palette.get(i)
        for v in cliques[i]:
            color_dict[v] = clique_color
    visual_style["vertex_color"] = [color_dict[v.index] for v in G.vs]
    plot(G, filename+'.png', **visual_style)

def draw_fb_network():
    G = create_fb_network()
    layt = G.layout('kk', dim=2)
    visual_style = {}
    visual_style["vertex_size"] = 5
    visual_style['edge_width'] = 0.5
    visual_style["margin"] = 10
    visual_style["layout"] = layt
    visual_style["bbox"] = (2500,2500)
    visual_style["vertex_label"] = G.vs["name"]

    color_dict = defaultdict(default)
    visual_style["vertex_color"] = [color_dict[v.index] for v in G.vs]
    plot(G, 'facebook.png', **visual_style)

def find_maximal_cliques(algo, outname):
    G = create_fb_network()
    R = set()
    P = set([v.index for v in G.vs])
    X = set()
    found = []
    fout = open(f'./{outname}.txt', 'w')
    if algo == 'tomita':
        tomita(R,P,X,G,found,fout)
    elif algo == 'bron-kerbosch':
        bron_kerbosch(R,P,X,G,found,fout)
    fout.close()

def intelligent_backtracking(R, P, X, G, cutoff, found, fout):
    if len(R) + len(P) < cutoff[0]:
        return

    if not P and not X and len(R) >= cutoff[0]:
        if len(R) > cutoff[0]:
            cutoff[0] = len(R)
            found = []
        print len(R)
        found.append(list(R))
        json.dump(list(R), fout)
        fout.write('\n')

    u = 0
    for v in list(P.union(X)):
        if G.degree(v) > G.degree(u) or u not in P:
            u = v
    u_neighbors = neighbors(u,G)
    for v in list(P.difference(u_neighbors)):
        v_neighbors = neighbors(v,G)
        intelligent_backtracking(R.union([v]), P.intersection(v_neighbors), X.intersection(v_neighbors), G, cutoff, found, fout)
        P.remove(v)
        X.add(v)

def find_maximum_cliques(G):
    P = set([v.index for v in G.vs])

    # find vertex with highest degree
    u = 0
    for v in P:
        if G.degree(v) > G.degree(u):
            u = v

    P = neighbors(u,G)
    # find neighbor with highest degree
    max_neighbor = 0
    for v in P:
        if G.degree(v) > G.degree(max_neighbor) or max_neighbor not in P:
            max_neighbor = v

    C = {u, max_neighbor}
    P = P.intersection(neighbors(max_neighbor,G))
    while P:
        max_adjacent = 0
        for v in P:
            if G.degree(v) > G.degree(max_adjacent) or max_adjacent not in P:
                max_adjacent = v
        C.add(max_adjacent)
        P = P.intersection(neighbors(max_adjacent,G))

    # prune the original list of vertex candidates whose degrees are less than
    # the degrees of vertices in this lower bound for a maximum clique
    P = set([v.index for v in G.vs])
    removed = 0
    for v in list(P):
        if G.degree(v) < len(C) - 1:
            P.remove(v)
            removed = removed + 1
    print removed

    R = set()
    X = set()
    found = []
    fout = open('./maximum_cliques.txt', 'w')
    intelligent_backtracking(R, P, X, G, [len(C)], found, fout)


if __name__ == '__main__':
    draw_fb_network()
    find_maximal_cliques('tomita', 'tomita_cliques')
    find_maximal_cliques('bron-kerbosch', 'bron_kerbosch_cliques')
    find_maximum_cliques(create_fb_network())
    draw_cliques_from_file('maximum_cliques.txt', 1)

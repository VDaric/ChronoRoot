#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:48:02 2020

@author: ncaggion
"""

import numpy as np
import graph_tool.all as gt


def find_dists(i, node, lnodes): #RETURNS THE LIST OF NODES WITHOUT THE NEAREST ONE
    d = np.linalg.norm(node[i]-lnodes, axis = 1)
    
    return d


def trimGraph(grafo, ske, ske2):
    g, pos, weight, clase, nodetype, age = grafo
    
    edges_to_delete = []
    to_delete = []
    
    gt.remove_parallel_edges(g)    
    
    ## DELETE WEIGHT 0 ED
    for edge in g.get_edges():
        e = g.edge(edge[0],edge[1])
        w = weight[e]
        if w == 0:
            edges_to_delete.append(edge)
            v1 = g.get_all_neighbors(edge[0])
            v2 = g.get_all_neighbors(edge[1])
    
            if (len(v1)) == 1:
                to_delete.append(edge[0])
            if (len(v2)) == 1:
                to_delete.append(edge[1])
            
    
    for i in reversed(sorted(to_delete)):
        g.clear_vertex(i)
        g.remove_vertex(i)
        
    to_delete = []
    vertices = g.get_vertices()
    
    for v in vertices:
        vecinos = g.get_out_neighbors(v)
        if len(vecinos) == 2:        
            edge = g.edge(vecinos[0], vecinos[1])
            
            if edge is None:
                edge = g.add_edge(vecinos[0], vecinos[1])
                ed1 = g.edge(v, vecinos[0])
                w1 = weight[ed1]
                ed2 = g.edge(v, vecinos[1])
                w2 = weight[ed2]
    
                weight[edge] = w1+w2
                
                if w1 == 0:
                    clase[edge] = clase[ed2]
                    ske2[np.where(ske2==clase[ed1][0])] == clase[ed2][0]
                elif w2 == 0:
                    clase[edge] = clase[ed1]
                    ske2[np.where(ske2==clase[ed2][0])] == clase[ed1][0]
                else:
                    clase[edge] = clase[ed2]
                    ske2[np.where(ske2==clase[ed1][0])] == clase[ed2][0]
    
                g.remove_edge(ed1)
                g.remove_edge(ed2)
                to_delete.append(v)
    
    for i in reversed(sorted(to_delete)):
        g.clear_vertex(i)
        g.remove_vertex(i)
        
    vertices = g.get_vertices()
    
    pos_vertex = []
    for i in vertices:
        pos_vertex.append(pos[i])
    pos_vertex = np.array(pos_vertex)
    
    pares = []
    
    for i in vertices:
        d = find_dists(i, pos, pos_vertex)
        mask = np.ones(pos_vertex.shape[0], bool)
        mask[i] = False
        
        pair = np.zeros(pos_vertex.shape[0], bool)
        pair[mask] = d[mask]<3
        c = np.count_nonzero(pair)
        
        if c==1:
            k = np.where(pair == True)[0][0]
            if [k, i] not in pares:
                pares.append([i,k])        
    
    to_delete = []
    
    for par in pares:
        v1 = par[0]
        v2 = par[1]
        if g.edge(v1,v2):
            if weight[g.edge(v1,v2)] == 0:
                vecinos2 = g.get_all_neighbors(v2)
                
                for k in vecinos2:
                    if k != v1:
                        edge = g.edge(v2, k)
                        w_e = weight[edge]
                        c_e = clase[edge]
                        
                        n_edge = g.add_edge(v1, k)
                        weight[n_edge] = w_e
                        clase[n_edge] = c_e
                
                g.clear_vertex(v2)
                to_delete.append(v2)
    
    for i in reversed(sorted(to_delete)):
        g.clear_vertex(i)
        g.remove_vertex(i)    
    
    
      
    
    return [g, pos, weight, clase, nodetype, age], ske, ske2



# import graph_tool.all as gt
# import cv2

# from rsmlFunc import createTree
# from imageFunc import getCleanSke
# from graphFunc import createGraph
# from trackFunc import matchGraphs


# conf = {}

# exec(open('/home/ncaggion/Escritorio/pRAnalyzer/confs/config.conf').read(),conf)

# for image in range(1214,1250):
#     g = gt.load_graph('/home/ncaggion/Escritorio/aux/graph_%s.xml.gz' %image)
#     pos = g.vertex_properties["pos"]
#     nodetype = g.vertex_properties["nodetype"] 
#     age = g.vertex_properties["age"]
#     weight = g.edge_properties["weight"]
#     clase = g.edge_properties["clase"] 
    
#     grafo1 = [g, pos, weight, clase, nodetype, age ]
    
#     seg = cv2.imread("/home/ncaggion/Escritorio/Test/Results 4/Imagenes/out_%s_2.png" %image, 0)
#     ske, bnodes, enodes, _ = getCleanSke(seg)
#     grafo2, seed, ske2 = createGraph(ske.copy(), pos[0], enodes, bnodes)
      
#     grafo2, ske, ske2 = trimGraph(grafo2, ske, ske2)
#     grafo2 = matchGraphs(grafo1, grafo2)
    
#     rsmlTree, numberLR = createTree(conf, 0, ["/home/ncaggion/Escritorio/Paper/Figura1/2020-03-31_12-15-18_2.png"], grafo2, ske, ske2)
#     rsmlTree.write(open('/home/ncaggion/Escritorio/aux/rsml_%s.rsml' %image, 'w'), encoding='unicode')
               
# gt.graph_draw(g, pos = pos)
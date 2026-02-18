from persim import PersistenceImager
from persim import plot_diagrams
from ripser import ripser
import tensorflow as tf
import numpy as np
#import gudhi as gd
import networkx as nx
import os
import glob as glob
import matplotlib.pyplot as plt
import random
from dataclasses import dataclass
import threading

def preprocess_img(img):
    img = tf.image.decode_png(img,channels=3)
    img = tf.image.resize(img, [240, 240])
    #img = tf.image.rgb_to_grayscale(img)
    return img.numpy()

def load_and_preprocess(path):
    img = tf.io.read_file(path)
    return preprocess_img(img)

def distanceMatrixFromGraph(WG):
    Infinity = 1000
    distances = dict(nx.all_pairs_bellman_ford_path_length(WG))
    # now transform this in distance matrix
    n = len(WG.nodes)
    matrix = [[Infinity for _ in range(n)] for _ in range (n)]
    for (i,v) in enumerate(WG.nodes):
        for (j,w) in enumerate(WG.nodes):
            if w not in distances[v]:
                continue
            matrix[i][j] = distances[v][w]
            try:
                matrix[j][i] = distances[v][w] #makes no difference
            except KeyError:
                print("Key error at graph")
                continue
    return np.array(matrix)

def EuclideanDistanceRGB(rgb1,rgb2):
    return np.sqrt(sum((a-b)**2 for (a,b) in zip(rgb1,rgb2)))

def EuclideanDistanceYUV(rgb1,rgb2):
    yuv1 = tf.image.rgb_to_yuv(rgb1).numpy()
    yuv2 = tf.image.rgb_to_yuv(rgb2).numpy()
    return np.sqrt(sum((a-b)**2 for (a,b) in zip(yuv1,yuv2)))

def EuclideanDistanceYIQ(rgb1,rgb2):
    yuv1 = tf.image.rgb_to_yiq(rgb1).numpy()
    yuv2 = tf.image.rgb_to_yiq(rgb2).numpy()
    return np.sqrt(sum((a-b)**2 for (a,b) in zip(yuv1,yuv2)))

def CMetric(rgb1,rgb2):
    r = (rgb1[0]+rgb2[0])/2
    dr = rgb1[0]-rgb2[0]
    dg = rgb1[1]-rgb2[1]
    db = rgb1[2]-rgb2[2]
    return np.sqrt((512+r)*dr*dr/256 + 4*dg*dg + (767-r)*db*db/256)

def createGraphFromImageCrop(img,imgsize=240,cropsize=30,mode=0):
    dict_pos = {}
    for i in range(cropsize):
        for j in range(cropsize):
            dict_pos[(i,j)] = cropsize*i+j

    midimg=np.floor(imgsize/2)
    offset=np.floor(cropsize/2)
    startingpixel = (midimg-offset).astype(np.int64)

    distances = [EuclideanDistanceRGB,EuclideanDistanceYUV,EuclideanDistanceYIQ,CMetric]
    distance = distances[mode] #can cause errors but this is my code for me
    G = nx.Graph()
    for i in range(cropsize):
        for j in range(cropsize):
            G.add_node(dict_pos[(i,j)])

    #link one below
    for i in range(cropsize):
        for j in range(cropsize-1):
            d = distance(img[startingpixel+i][startingpixel+j],img[startingpixel+i][startingpixel+j+1])
            G.add_edge(dict_pos[(i,j)],dict_pos[(i,j+1)],weight=d)
    #link one side
    for j in range(cropsize):
        for i in range(cropsize-1):
            d = distance(img[startingpixel+i][startingpixel+j],img[startingpixel+i+1][startingpixel+j])
            G.add_edge(dict_pos[(i,j)],dict_pos[(i+1,j)],weight=d)
    #main diag
    for j in range(cropsize-1):
        for i in range(cropsize-1):
            d=distance(img[startingpixel+i][startingpixel+j],img[startingpixel+i+1][startingpixel+j+1])
            G.add_edge(dict_pos[(i,j)],dict_pos[(i+1,j+1)],weight=d)
    #sec diag
    for j in range(1,cropsize):
        for i in range(cropsize-1):
            d = distance(img[startingpixel+i][startingpixel+j],img[startingpixel+i+1][startingpixel+j-1])
            G.add_edge(dict_pos[(i,j)],dict_pos[(i+1,j-1)],weight=d)
    return G

def theWholePlate(pathin, pathout):
    #path in == .png
    #path out == .jpg
    img = load_and_preprocess(pathin)
    graph = createGraphFromImageCrop(img,cropsize=50)
    dmatrix = distanceMatrixFromGraph(graph)
    dgms = ripser(np.array(dmatrix),distance_matrix=True)['dgms']
    h1 = dgms[1]
    pimgr = PersistenceImager(pixel_size=1)
    pimgr.fit(h1)
    pimgr.plot_image(pimgr.transform(h1),out_file=pathout)
    return 0

def threadFunc(folder):
    if MyConfigs.MODE == 0:
        modestr = "EclidRGB"
    elif MyConfigs.MODE == 1:
        modestr = "EclidYUV"
    elif MyConfigs.MODE == 2:
        modestr = "EclidYIQ"
    else:
        modestr = "CMetric"
    count = 0
    print('dealing with '+folder)
    for infile in glob.glob(folder+'*.png'):
        file, exten = os.path.splitext(infile)
        fileout = file+modestr+'Persim.jpg'
        if not os.path.exists(fileout):
            theWholePlate(infile,fileout)
        count=count+1
        print("clear ",count)

class MyConfigs:
    MODE = 3
    THRESHOLD = 0.1
    IMGSIZE = 240

def main():
    pathAI = os.getcwd()+os.sep+'dataset'+os.sep+'AiArtData'+os.sep
    pathReal = os.getcwd()+os.sep+'dataset'+os.sep+'RealArt'+os.sep
    paths = [pathAI,pathReal]

    threadFunc(paths[0])
    threadFunc(paths[1])

    print("all done")

if __name__=="__main__":
    main()

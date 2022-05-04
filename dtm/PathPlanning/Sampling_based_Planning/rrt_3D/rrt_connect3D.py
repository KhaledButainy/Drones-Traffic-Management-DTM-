# rrt connect algorithm
"""
This is rrt connect implementation for 3D
@author: yue qi
"""
import numpy as np
from numpy.matlib import repmat
from collections import defaultdict
import time
# import matplotlib.pyplot as plt

import os
import sys
from sqlalchemy import false

from sympy import Id, Point3D, Segment3D
from copy import deepcopy

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../../Sampling_based_Planning/")

from rrt_3D.env3D import env
from rrt_3D.utils3D import getDist, sampleFree, nearest, steer, isCollide, near, visualization, cost, path, edgeset
from rrt_3D.plot_util3D import set_axes_equal, draw_block_list, draw_Spheres, draw_obb, draw_line, make_transparent


class Tree():
    def __init__(self, node):
        self.V = []
        self.Parent = {}
        self.V.append(node)
        # self.Parent[node] = None

    def add_vertex(self, node):
        if node not in self.V:
            self.V.append(node)
        
    def add_edge(self, parent, child):
        # here edge is defined a tuple of (parent, child) (qnear, qnew)
        self.Parent[child] = parent


class rrt_connect():
    def __init__(self, start, goal, config):
        self.env = env(**config)
        self.Parent = {}
        self.V = []
        self.E = set()
        self.i = 0
        self.maxiter = 10000
        self.stepsize = 0.000125 #FIXME: use this instead
        # self.stepsize = 0.5 
        self.Path = []
        self.done = False

        self.env.start = start
        self.env.goal = goal

        self.qinit = tuple(start)
        self.qgoal = tuple(goal)
        self.x0, self.xt = tuple(start), tuple(goal)
        self.qnew = None
        self.done = False
        
        self.ind = 0
        # self.fig = plt.figure(figsize=(10, 8))


#----------Normal RRT algorithm
    def BUILD_RRT(self, qinit):
        tree = Tree(qinit)
        for k in range(self.maxiter):
            qrand = self.RANDOM_CONFIG()
            self.EXTEND(tree, qrand)
        return tree

    def EXTEND(self, tree, q):
        qnear = tuple(self.NEAREST_NEIGHBOR(q, tree))
        qnew, dist = steer(self, qnear, q)
        self.qnew = qnew # store qnew outside
        if self.NEW_CONFIG(q, qnear, qnew, dist=None):
            tree.add_vertex(qnew)
            tree.add_edge(qnear, qnew)
            if qnew == q:
                return 'Reached'
            else:
                return 'Advanced'
        return 'Trapped'

    def NEAREST_NEIGHBOR(self, q, tree):
        # find the nearest neighbor in the tree
        V = np.array(tree.V)
        if len(V) == 1:
            return V[0]
        xr = repmat(q, len(V), 1)
        dists = np.linalg.norm(xr - V, axis=1)
        return tuple(tree.V[np.argmin(dists)])

    def RANDOM_CONFIG(self):
        return tuple(sampleFree(self))

    def NEW_CONFIG(self, q, qnear, qnew, dist = None):
        # to check if the new configuration is valid or not by 
        # making a move is used for steer
        # check in bound
        collide, _ = isCollide(self, qnear, qnew, dist = dist)
        return not collide

#----------RRT connect algorithm
    def CONNECT(self, Tree, q):
        # print('in connect')
        while True:
            S = self.EXTEND(Tree, q)
            if S != 'Advanced':
                break
        return S

    def RRT_CONNECT_PLANNER(self, qinit, qgoal, visualize=False):
        Tree_A = Tree(qinit)
        Tree_B = Tree(qgoal)
        for k in range(self.maxiter):
            # print(k)
            qrand = self.RANDOM_CONFIG()
            if self.EXTEND(Tree_A, qrand) != 'Trapped':
                qnew = self.qnew # get qnew from outside
                if self.CONNECT(Tree_B, qnew) == 'Reached':
                    print('reached')
                    self.done = True
                    self.Path = self.PATH(Tree_A, Tree_B)
                    # if visualize:
                    #     self.visualization(Tree_A, Tree_B, k)
                    #     # plt.show()
                    return
                    # return
            Tree_A, Tree_B = self.SWAP(Tree_A, Tree_B)
            # if visualize:
            #     self.visualization(Tree_A, Tree_B, k)
        return 'Failure'

    # def PATH(self, tree_a, tree_b):
    def SWAP(self, tree_a, tree_b):
        tree_a, tree_b = tree_b, tree_a
        return tree_a, tree_b

    def PATH(self, tree_a, tree_b):
        qnew = self.qnew
        patha = []
        pathb = []
        while True:
            patha.append((tree_a.Parent[qnew], qnew))
            qnew = tree_a.Parent[qnew]
            if qnew == self.qinit or qnew == self.qgoal:
                break
        qnew = self.qnew
        while True:
            pathb.append((tree_b.Parent[qnew], qnew))
            qnew = tree_b.Parent[qnew]
            if qnew == self.qinit or qnew == self.qgoal:
                break
        return list(reversed(patha)) + pathb

#----------RRT connect algorithm        

LAYER_BORDER = 0.002
def flatten(coords):
    output = {'coordinates': []} 
    coordinates = []
    for i in coords:
        felement, _ = i
        longitude, latitude, altitude = felement
        if(altitude >= LAYER_BORDER): altitude = 15.0
        else: altitude = 10.0 
        coordinates.append([longitude,latitude,altitude])
    output['coordinates'] = coordinates
    #return patha + pathb
    return coordinates

def pairwise_overlap(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    a = iter(iterable)
    b = iter(iterable)
    next(b)
    return zip(a, b)

def triwise_overlap(iterable):
    "s -> (s0, s1), (s1, s2), (s2, s3), ..."
    assert len(iterable) > 2
    a = iter(iterable)
    b = iter(iterable)
    c = iter(iterable)
    next(b)
    next(c)
    next(c)
    return zip(a, b, c)

def remove_redundant_points(path):
    """
    mutates (modifies) the `path` variable, removes redundant points
    """
    if len(path) <= 3:
        return
    def angle(p1,p2):
        x1,y1,z1 = p1
        x2,y2,z2 = p2
        dx = x2 - x1
        dy = y2 - y1
        return np.arctan(dy/(dx + 0.00001*np.sign(dx)))
    indexes_to_remove = []
    for i,(p1,p2,p3) in enumerate(triwise_overlap(path)):
        if np.abs(angle(p1,p2) - angle(p1,p3)) <= 0.05:
            indexes_to_remove.append(i+1)

    for i in reversed(indexes_to_remove):
        # print(i)
        del path[i]

def find_new_path(droneID,start,goal,env_config,active_paths,visualize=False):
    """
    droneID, Integer ID number of the drone whose path we are generating
    start, (double)[x,y,z] The start point of the mission
    goal, (double)[x,y,z] The goal of our mission
    env, Dictionary containing the boundaries of the environment and all the objects inside it
    active_paths, Dictionary containing the active drone IDs and the paths they are following
    """
    #modify active paths 
    
    DRONE_EXTENTS = 0.00001
    ORIGINAL_ZLAYER_HEIGHT = 0.0005
    PADDING = 0.0000025
    env_config = deepcopy(env_config)

    for droneId, path in active_paths.items():
        for p1, p2 in pairwise_overlap(path):
            ZLAYER_HEIGHT = ORIGINAL_ZLAYER_HEIGHT
            x1, y1, z1 = p1
            x2, y2, z2 = p2
            dx = x2 - x1
            dy = y2 - y1
            px = (x1 + x2)/2
            py = (y1 + y2)/2
            if (z1 != z2):
                ZLAYER_HEIGHT = 2*ZLAYER_HEIGHT
                pz = LAYER_BORDER
            elif (z1 == 10 and z2 == 10):
                pz = LAYER_BORDER - LAYER_BORDER/2
            else:
                pz = LAYER_BORDER + LAYER_BORDER/2
            # pz = (z1 + z2)/2-PADDING/2
            #TODO: pathfinder output should have discrete z
            ex = np.sqrt(dx**2 + dy**2)/2
            ox = np.arctan(dy / (dx+0.00001*np.sign(dx)))
            # ox = np.arctan(dx / (dy+0.00001*np.sign(dy)))
            #TODO: implement ox and oy
            env_config['obbs'] += [[[px,py,pz], [ex+PADDING,DRONE_EXTENTS+PADDING,ZLAYER_HEIGHT+PADDING], [ox,0,0]]]

    # create rrt connect class
    p = rrt_connect(start, goal, env_config)
    p.RRT_CONNECT_PLANNER(p.qinit, p.qgoal, visualize=visualize)
    coords_flattened = flatten(p.Path)
    print('path     :', coords_flattened)
    # coords_flattened = coords_flattened[2:-2]
    remove_redundant_points(coords_flattened)
    # print('pathundup:', coords_flattened)
    active_paths[droneID] = coords_flattened
    return coords_flattened

def check_intersects(curren_path, other_paths):
    curren_path = deepcopy(curren_path)
    current_path_segments = []
    for i in range(len(curren_path)-1):
        p1 = Point3D(curren_path[i][0], curren_path[i][1], curren_path[i][2])
        p2 = Point3D(curren_path[i+1][0], curren_path[i+1][1], curren_path[i+1][2])
        current_path_segments.append(Segment3D(p1, p2))

    other_paths_segments = []
    if other_paths:
        for path in other_paths:
            path_seqments = []
            for i in range(len(path['flight_path']['coordinates'])-1):
                p1 = Point3D(path['flight_path']['coordinates'][i][0], path['flight_path']['coordinates'][i][1], path['flight_path']['coordinates'][i][2])
                p2 = Point3D(path['flight_path']['coordinates'][i+1][0], path['flight_path']['coordinates'][i+1][1], path['flight_path']['coordinates'][i+1][2])
                path_seqments.append(Segment3D(p1, p2))
            other_paths_segments.append(path_seqments)

    for i in range(len(current_path_segments)):
        for j in range(len(other_paths_segments)):
            for k in range(len(other_paths_segments[j])):
                try:
                    if current_path_segments[i].intersection(other_paths_segments[j][k]):
                        curren_path[i][2] = 15
                        curren_path[i+1][2] = 15
                finally:
                    break
    
    return curren_path


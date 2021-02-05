# -*- coding: utf-8 -*-
"""
Created on Wed Nov 25 13:11:06 2020

@author: 14830
"""


import heapq

class Node(object):

    def __init__(self, name):
        self.name = name
        self.connected_nodes = {}
        self.distance = float('inf')
        self.visited = False
        self.previous = None

    def add_connection(self, neighbor, weight=0):
        self.connected_nodes[neighbor] = weight

    def get_connections(self):
        return self.connected_nodes.keys()

    def get_name(self):
        return self.name

    def get_weight(self, neighbor):
        return self.connected_nodes[neighbor]

    def set_distance(self, distance):
        self.distance = distance

    def get_distance(self):
        return self.distance

    def set_previous(self, previous):
        self.previous = previous

    def set_visited(self):
        self.visited = True

    def __str__(self):
        return f'{self.name}: {[x for x in self.connected_nodes.keys()]}'

    def __lt__(self, other):
        return self.distance < other.distance

#build network
class Network(object):

    def __init__(self):
        self.node_dict = {}
        self.num_nodes = len(self.node_dict)
        self.previous = None

    def __iter__(self):
        return iter(self.node_dict.values())

    def add_nodes(self, nodes):
        for node in nodes:
            self.add_node(node)

    def add_node(self, node):
        self.node_dict[node] = Node(node)
        self.num_nodes = len(self.node_dict)
        return self.node_dict[node]

    def get_node(self, n):
        return self.node_dict[n] if n in self.node_dict else None

    def add_edge(self, frm, to, edge_weight=0.0):
        if frm not in self.node_dict:
            self.add_node(frm)
        if to not in self.node_dict:
            self.add_node(to)

        self.node_dict[frm].add_connection(self.node_dict[to], edge_weight)
        self.node_dict[to].add_connection(self.node_dict[frm], edge_weight)

    def get_nodes(self):
        return list(self.node_dict.keys())

    def set_previous(self, current):
        self.previous = current

    def get_previous(self):
        return self.previous

    def __str__(self):
        text = 'Network\n'
        for node in self:
            for connected_node in node.get_connections():
                node_name = node.get_name()
                connected_node_name = connected_node.get_name()
                text += f'{node_name} -> {connected_node_name} :' \
                        f' {node.get_weight(connected_node)}\n'
        return text

    def reset(self):
        for node in self:
            node.distance = float('inf')
            node.visited = False
            node.previous = None

#define network
class Dijkstra(object):

    @staticmethod
    def compute(network, start):
        start.set_distance(0)

        # create the priority queue with nodes
        unvisited_queue = [(node.get_distance(), node) for node in network]
        heapq.heapify(unvisited_queue)

        while len(unvisited_queue):
            # pop a node with the smallest distance
            unvisited_node = heapq.heappop(unvisited_queue)
            current_node = unvisited_node[1]
            current_node.set_visited()

            for next_node in current_node.connected_nodes:
                if not next_node.visited:
                    new_dist = current_node.get_distance() + current_node.get_weight(next_node)
                    if new_dist < next_node.get_distance():
                        next_node.set_distance(new_dist)
                        next_node.set_previous(current_node)
            
            # Rebuild heap: Pop every item, Put all nodes not visited into the queue
            while len(unvisited_queue):
                heapq.heappop(unvisited_queue)
            
            unvisited_queue = [(n.get_distance(), n) for n in network if not n.visited]
            heapq.heapify(unvisited_queue)

    @staticmethod
    def compute_shortest_path(node, path):
        if node.previous:
            path.append(node.previous.get_name())
            Dijkstra.compute_shortest_path(node.previous, path)


def read_network_from_file(file_name, delimeter=','):
    cities = list()
    distances = dict()

    f = open(file_name, 'r')
    lines = f.readlines()
    for line in lines:
        fields = line.rstrip().split(delimeter)
        city_1 = fields[0].strip(' ')
        city_2 = fields[1].strip(' ')
        distance = float(fields[2])

        # build the list of nodes
        if city_1 not in cities:
            cities.append(city_1)
        if city_2 not in cities:
            cities.append(city_2)

        # build the dictionary based on node weights
        if cities.index(city_1) not in distances.keys():
            distances[cities.index(city_1)] = {cities.index(city_2): distance}
        if cities.index(city_2) not in distances[cities.index(city_1)].keys():
            distances[cities.index(city_1)][cities.index(city_2)] = distance

    return cities, distances


def seek_and_compare(start_city_name, target_city_name, network):
    dist_one = 0
    path_one = []
    dist_two = 0
    path_two = []

    # First calculating the distance between: start_city--->New Orleans--->St. Louis--->target_city
    Dijkstra.compute(network, network.get_node(start_city_name))
    Orleans_city_node = network.get_node('New Orleans')
    path_start_to_Orleans = [Orleans_city_node.get_name()]
    Dijkstra.compute_shortest_path(Orleans_city_node, path_start_to_Orleans)
    print(f'{start_city_name} -> "New Orleans" = {path_start_to_Orleans[::-1]} : {Orleans_city_node.get_distance()}')
    dist_one += Orleans_city_node.get_distance()
    path_one += path_start_to_Orleans[::-1]

    network.reset()

    Dijkstra.compute(network, network.get_node('New Orleans'))
    Louis_city_node = network.get_node('St. Louis')
    path_Orleans_to_Louis = [Louis_city_node.get_name()]
    Dijkstra.compute_shortest_path(Louis_city_node, path_Orleans_to_Louis)
    print(f'"New Orleans" -> "St. Louis" = {path_Orleans_to_Louis[::-1]} : {Louis_city_node.get_distance()}')
    dist_one += Louis_city_node.get_distance()
    path_one += path_Orleans_to_Louis[::-1][1:]

    network.reset()

    Dijkstra.compute(network, network.get_node('St. Louis'))
    target_city_node = network.get_node(target_city_name)
    path_Louis_to_target = [target_city_node.get_name()]
    Dijkstra.compute_shortest_path(target_city_node, path_Louis_to_target)
    print(f'"St. Louis" -> {target_city_name} = {path_Louis_to_target[::-1]} : {target_city_node.get_distance()}')
    dist_one += target_city_node.get_distance()
    path_one += path_Louis_to_target[::-1][1:]

    # Second caculating the distance between: start_city--->St. LouisNew--->Orleans--->target_city
    network.reset()

    Dijkstra.compute(network, network.get_node(start_city_name))
    Louis_city_node = network.get_node('St. Louis')
    path_start_to_Louis = [Louis_city_node.get_name()]
    Dijkstra.compute_shortest_path(Louis_city_node, path_start_to_Louis)
    print(f'{start_city_name} -> "St. Louis" = {path_start_to_Louis[::-1]} : {Louis_city_node.get_distance()}')
    dist_two += Louis_city_node.get_distance()
    path_two += path_start_to_Louis[::-1]

    network.reset()

    Dijkstra.compute(network, network.get_node('St. Louis'))
    Orleans_city_node = network.get_node('New Orleans')
    path_Louis_to_Orleans = [Orleans_city_node.get_name()]
    Dijkstra.compute_shortest_path(Orleans_city_node, path_Louis_to_Orleans)
    print(f'"St. Louis" -> "New Orleans" = {path_Louis_to_Orleans[::-1]} : {Orleans_city_node.get_distance()}')
    dist_two += Orleans_city_node.get_distance()
    path_two += path_Louis_to_Orleans[::-1][1:]

    network.reset()

    Dijkstra.compute(network, network.get_node('New Orleans'))
    target_city_node = network.get_node(target_city_name)
    path_Orleans_to_target = [target_city_node.get_name()]
    Dijkstra.compute_shortest_path(target_city_node, path_Orleans_to_target)
    print(f'"New Orleans" -> {target_city_name} = {path_Orleans_to_target[::-1]} : {target_city_node.get_distance()}')
    dist_two += target_city_node.get_distance()
    path_two += path_Orleans_to_target[::-1][1:]

    if dist_one < dist_two:
        return dist_one, path_one
    else:
        return dist_two, path_two

def main():
    # application salutation
    application_name = 'Trucking Analysis Network'
    print('-' * len(application_name))
    print(application_name)
    print('-' * len(application_name))

    # read graph from file
    file_name = 'HW3_Network.csv'
    cities, distances = read_network_from_file(file_name)

    # build the graph
    network = Network()
    network.add_nodes(cities)
    for connection in distances.items():
        frm = cities[connection[0]]
        for connection_to in connection[1].items():
            network.add_edge(frm, cities[connection_to[0]], connection_to[1])

    # uncomment to print the graph
    for (index, city) in enumerate(network.get_nodes()):
        print(f'{index}: {city:s}')

    start_city_index = '--'
    while True:
        try:
            start_city_index = int(input(f'Please enter the start city by index (0 to {len(network.get_nodes()) - 1}): '))
            if not start_city_index >= 0:
                print(f'Please input a valid positive number! A valid range from 0 to {len(network.get_nodes()) - 1}.')
                continue
            elif start_city_index > (len(network.get_nodes()) - 1):
                print(f'Please input a valid positive number! A valid range from 0 to {len(network.get_nodes()) - 1}.')
                continue
        except ValueError:
            print("This is not a correct integer format!")
        else:
            break
    
    start_city_name = network.get_nodes()[start_city_index]

    target_city_index = '--'
    while True:
        try:
            target_city_index = int(input(f'Please enter the target city by index (0 to {len(network.get_nodes()) - 1}): '))
            if not target_city_index >= 0:
                print(f'Please input a valid positive number! A valid range is from 0 to {len(network.get_nodes()) - 1}.')
                continue
            elif target_city_index > (len(network.get_nodes()) - 1):
                print(f'Please input a valid positive number! A valid range is from 0 to {len(network.get_nodes()) - 1}.')
                continue        
        except ValueError:
            print("This is not a correct integer format!")
        else:
            break

    target_city_name = network.get_nodes()[target_city_index]

    # using Dijkstra's algorithm, compute least cost (distance)
    dist, path_shortest = seek_and_compare(start_city_name, target_city_name, network)

    print(f'\n the shortest distance from {start_city_name}-->{target_city_name} is : {dist}')
    print(f'the shortest path is {path_shortest}')
   
if __name__ == '__main__':
    main()

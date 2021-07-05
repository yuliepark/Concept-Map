import re
import json

""" Represents each node object (week, concept, subconcept, etc.) in concept map tree. """
class Node:
    def __init__(self, id, label):
        self.id = id
        self.label = label # e.g. "node0"
        self.children = [] 
        self.parent = "None" 
        self.sibling = "None" # right sibling
    def __repr__(self):
        rep = "["
        for child in self.children:
            rep += child.label + ", "
        rep = rep[:-2] + "]"
        return "Node(" + label + ", " + rep + ", " + parent.label + ", " + sibling.label


""" Parse given FILENAME dot file. Convert graphviz nodes into Nodes and record hierarchical relationships. """
def parse_dot(filename):
    file = open(filename, 'r')
    lines = file.readlines()

    id2node = {} # e.g. "node0": Node obj
    rank_ids = [] # list of node IDs with same rank (e.g. weeks)

    for line in lines:
        if rank_match := re.compile(r'rank(.*){(.*)}').search(line):
            rank_ids = rank_match.group(2).split(", ")
        if wks_match := re.compile(r'(node(\d+))(.*)"(.*)"(.*)](.*)').search(line):
            node_id = wks_match.group(1)
            id2node[node_id] = Node(id=node_id, label=wks_match.group(4))
        elif edge_match := re.compile(r'(node(\d+)) -> ((.*)node(\d+)(.*))').search(line):
            left = edge_match.group(1)
            right = edge_match.group(3)
            if "[dir" in right and "back]" in right: # ideally, encode backward arrows
                stop_idx = right.index("[")
                right = right[:stop_idx-1]
            if "{" in right:
                stop_idx = right.index("}")
                right = right[1:stop_idx].split(", ")
            else:
                right = [right]
            for child in right:
                if left in rank_ids and child in rank_ids:
                    id2node[left].sibling = id2node[child]
                else:
                    id2node[left].children.append(id2node[child])
                    id2node[child].parent = id2node[left]

    return id2node, rank_ids


"""
    Produces JSON string representation from ROOT_NODES
    Inputs:
    - ROOT_NODES: list of source Nodes from which the entire concept map can be generated 
    - SUBNODES: list of children Nodes
"""
def to_json_string(root_nodes):
    def recurse(subnodes):
        string = ""
        if subnodes:
            i = 0
            for node in subnodes:
                string += "{" + "id:'%s', name:'%s', children:[%s]"%(node.id, node.label, recurse(node.children)) + "}"
                if i < len(subnodes) - 1: string += ","
                i += 1
        return string
    json = """{id:'node00', name:'CS10', data:{}, children:[%s]}"""%(recurse(root_nodes))
    return json


""" For now, file is of .txt extension. """
def to_json_file(data, filename="output.txt"):
    with open(filename, 'w') as f:
        json.dump(data, f)

""" Main method """
def run(filename):
    id2node, rank_ids = parse_dot(filename)
    json = to_json_string([id2node[id] for id in rank_ids])
    print(json)
    to_json_file(json)


##################################################################################################################################

if __name__ == "__main__":
    filename = "test.dot"
    run(filename)
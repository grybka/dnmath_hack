import random

#bidirectional network
class Network:
    def __init__(self,n_nodes,edges=[]):
        self.n_nodes=n_nodes
        self.edges=edges

    def prune_until_spanning_tree(self):
        #remove edges until we have a spanning tree
        edges_copy=self.edges.copy()
        random.shuffle(edges_copy)
        for edge in edges_copy:
            #if I can remove the edge and the network is still connect, keep it removed
            self.edges.remove(edge)
            if not self.is_connected():
                self.edges.append(edge)

    def is_connected(self):
        #check if the network is connected
        nodes=list(range(self.n_nodes))
        visited=[False]*self.n_nodes
        queue=[]
        queue.append(0)
        visited[0]=True
        while len(queue)>0:
            current=queue.pop(0)
            for edge in self.edges:
                if edge[0]==current:
                    if not visited[edge[1]]:
                        visited[edge[1]]=True
                        queue.append(edge[1])
                if edge[1]==current:
                    if not visited[edge[0]]:
                        visited[edge[0]]=True
                        queue.append(edge[0])
        return all(visited)

    @staticmethod
    def fully_connected_network(n_nodes):
        network=Network(n_nodes)
        for i in range(n_nodes):
            for j in range(i+1,n_nodes):
                network.edges.append((i,j))
        return network
from pymote.algorithm import NodeAlgorithm
from pymote.message import Message

class DFT(NodeAlgorithm):
    required_params = {'informationKey', }
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'IDLE'
            if self.informationKey in node.memory:
                ini_node = node
        ini_node.status = 'INITIATOR'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def initiator(self, node, message):
        node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
        next_node = node.memory['unvisitedNodes'][0]
        node.send(Message(destination=next_node, header='T', data=message.data))
        
        nodeNeighbors = list(node.memory[self.neighborsKey])
        nodeNeighbors.remove(next_node)

        for i in range(len(nodeNeighbors)):
            node.send(Message(destination=nodeNeighbors[i], header='Visited', data=message.data))

        node.status = 'VISITED'

    def idle(self, node, message):
        if message.header == 'T':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            self.firstVisit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'] = list(node.memory[self.neighborsKey])
            node.memory['unvisitedNodes'].remove(message.source)
            node.status = 'AVAILABLE'

    def available(self, node, message):
        if message.header == 'T':
            self.firstVisit(node, message)
        elif message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)

    def visited(self, node, message):
        if message.header == 'Visited':
            node.memory['unvisitedNodes'].remove(message.source)
            if node.memory['unvisitedNodes'][0] is message.source:
                self.visit(node, message)
        elif message.header == 'T':
            node.memory['unvisitedNodes'].remove(message.source)
            if node.memory['unvisitedNodes'][0] is message.source:
                self.visit(node, message)
        elif message.header == 'Return':
            self.visit(node,message)

    def firstVisit(self, node, message):
        node.memory['entry'] = message.source
        node.memory['unvisitedNodes'].remove(message.source)

        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
            
            nodeNeighbors = list(node.memory[self.neighborsKey])
            nodeNeighbors.remove(next_node)
            nodeNeighbors.remove(node.memory['entry'])

            for i in range(len(nodeNeighbors)):
                node.send(Message(destination=nodeNeighbors[i], header='Visited', data=message.data))
            
            node.status = 'VISITED'
        else:
            node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            
            nodeNeighbors = list(node.memory[self.neighborsKey])
            nodeNeighbors.remove(node.memory['entry'])

            for i in range(len(nodeNeighbors)):
                node.send(Message(destination=nodeNeighbors[i], header='Visited', data=message.data))
            
            node.status = 'DONE'

    def visit(self, node, message):
        if node.memory['unvisitedNodes']:
            next_node = node.memory['unvisitedNodes'][0]
            node.send(Message(destination=next_node, header='T', data=message.data))
        else:
            if 'entry' in node.memory:
                node.send(Message(destination=node.memory['entry'], header='Return', data=message.data))
            node.status = 'DONE'

    def done(self, node, message):
        pass

    STATUS = {
                'INITIATOR': initiator,
                'IDLE': idle,
                'AVAILABLE': available,
                'VISITED': visited,
                'DONE': done
             } 
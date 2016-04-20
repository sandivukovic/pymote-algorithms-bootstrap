from pymote.algorithm import NodeAlgorithm
from pymote.message import Message

class Saturation(NodeAlgorithm):
    required_params = {}
    default_params = {'neighborsKey': 'Neighbors'}

    def initializer(self):
        for node in self.network.nodes():
            node.memory[self.neighborsKey] = node.compositeSensor.read()['Neighbors']
            node.status = 'AVAILABLE'
        ini_node = self.network.nodes()[0]
        ini_node.status = 'AVAILABLE'
        self.network.outbox.insert(0, Message(header=NodeAlgorithm.INI, destination=ini_node))

    def available(self, node, message):
        nodeNeighbors = list(node.memory[self.neighborsKey])
        if message.header == 'Activate':
            nodeNeighbors.remove(message.source)
            for i in range(len(nodeNeighbors)):
                node.send(Message(destination=nodeNeighbors[i], header='Activate', data=message.data))

        else:
            for i in range(len(nodeNeighbors)):
                node.send(Message(destination=nodeNeighbors[i], header='Activate', data=message.data))

        self.initialize(self, node, message)

        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def active(self, node, message):

        if message.header == 'Message':
            self.process_message(self, node, message)
            nodeNeighbors = list(node.memory[self.neighborsKey])
            nodeNeighbors.remove(message.source)

        if len(node.memory['neighbors']) == 1:
            self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header == 'Message':
            self.process_message(self, node, message)
            self.resolve(self, node, message)

    def initialize(self, node, message):
        raise NotImplementedError
    def prepare_message(self, node, message):
        m = ['Saturation']
    def process_message(self, node, message):
        raise NotImplementedError
    def resolve(self, node, message):
        node.status = 'SATURATED'

    STATUS = {
                'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing,
                'SATURATED': saturated
             }
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

        self.initialize(node, message)

        node.memory['neighbors'] = list(node.memory[self.neighborsKey])
        if len(node.memory['neighbors']) == 1:
            message = self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'
        else:
            node.status = 'ACTIVE'

    def active(self, node, message):

        if message.header == 'Message':
            self.process_message(node, message)
            node.memory['neighbors'].remove(message.source)

        if len(node.memory['neighbors']) == 1:
            message = self.prepare_message(node, message)
            node.memory['parent'] = node.memory['neighbors'].pop()
            node.send(Message(destination=node.memory['parent'], header='Message', data=message.data))
            node.status = 'PROCESSING'

    def processing(self, node, message):
        if message.header == 'Message':
            self.process_message(node, message)
            self.resolve(node, message)

    def initialize(self, node, message):
        pass

    def prepare_message(self, node, message):
        pass

    def process_message(self, node, message):
        pass

    def resolve(self, node, message):
        node.status = 'SATURATED'

    def saturated(self, node, message):
        pass

    STATUS = {
                'AVAILABLE': available,
                'ACTIVE': active,
                'PROCESSING': processing,
                'SATURATED': saturated
             }


class Median(Saturation):

    def processing(self, node, message):
        super(Median, self).processing(node, message)
        if message.header == 'Median':
            self.process_message(node, message)
            self.resolve(node, message)

    def initialize(self, node, message):
        node.memory['distance_sum'] = {}
        node.memory['distance_sum'][node] = 1

    def prepare_message(self, node, message):
        message = Message()
        message.data = node.memory['distance_sum'][node]
        message.header = 'Message'
        return message

    def process_message(self, node, message):
        node.memory['distance_sum'][message.source] = message.data
        node.memory['distance_sum'][node] += message.data

    def resolve(self, node, message):
        for neighbor in node.memory[self.neighborsKey]:
            # for all neighbors calculate G[y,x]
            G = node.memory['distance_sum'][node] - \
                2*node.memory['distance_sum'][neighbor]
            if G <= 0:
                # neighbor is median or on the way to the median
                if neighbor != node.memory['parent']:
                    # send message to neighbor only if it is not a parent
                    node.send(
                        Message(header='Median', destination=neighbor,
                                data=node.memory['distance_sum'][node] -
                                node.memory['distance_sum'][neighbor])
                    )
                if G == 0:
                    # this node is median also
                    node.status = 'MEDIAN'
                break
        else:
            # if all neighbors' G > 0 then this node is the only median
            node.status = 'MEDIAN'

    def median(self, node, message):
        pass

    STATUS = {
        'AVAILABLE': Saturation.STATUS.get('AVAILABLE'),
        'ACTIVE': Saturation.STATUS.get('ACTIVE'),
        'PROCESSING': processing,
        'SATURATED': Saturation.STATUS.get('SATURATED'),
        'MEDIAN': median
    }
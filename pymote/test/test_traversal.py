from pymote.networkgenerator import NetworkGenerator
from pymote.simulation import Simulation
from pymote.algorithms.traversal import DF_STAR
from pymote.algorithms.traversal import DFT
from pymote.npickle import write_pickle
from pymote.network import Network

def one_node_network():
	net = Network()
	net.add_node(pos=(351, 351), commRange=80)
	return net

def small_random_network():
	net_gen = NetworkGenerator(10, commRange=400)
	net = net_gen.generate_random_network()
	return net

def medium_random_network():
	net_gen = NetworkGenerator(20, commRange=250)
	net = net_gen.generate_random_network()
	return net

def big_random_network():
	net_gen = NetworkGenerator(50, commRange=300)
	net = net_gen.generate_random_network()
	return net

def line_network():
	net = Network()
	net.add_node(pos=(111, 111), commRange=80)
	net.add_node(pos=(151, 151), commRange=80)
	net.add_node(pos=(201, 201), commRange=80)
	net.add_node(pos=(251, 251), commRange=80)
	net.add_node(pos=(301, 301), commRange=80)
	net.add_node(pos=(351, 351), commRange=80)
	net.add_node(pos=(401, 401), commRange=80)
	net.add_node(pos=(451, 451), commRange=80)
	net.add_node(pos=(501, 501), commRange=80)
	net.add_node(pos=(551, 551), commRange=80)
	return net

def triangle_network():
	net = Network()
	net.add_node(pos=(111, 111), commRange=200)
	net.add_node(pos=(111, 251), commRange=200)
	net.add_node(pos=(251, 111), commRange=200)
	return net

def square_x_network():
	net = Network()
	net.add_node(pos=(111, 111), commRange=200)
	net.add_node(pos=(111, 251), commRange=200)
	net.add_node(pos=(251, 111), commRange=200)
	net.add_node(pos=(251, 251), commRange=200)
	return net

def square_network():
	net = Network()
	net.add_node(pos=(111, 111), commRange=151)
	net.add_node(pos=(111, 251), commRange=151)
	net.add_node(pos=(251, 111), commRange=151)
	net.add_node(pos=(251, 251), commRange=151)
	return net

def my_random_network():
	net = Network()
	net.add_node(pos=(100, 100), commRange=300)
	net.add_node(pos=(123, 302), commRange=300)
	net.add_node(pos=(204, 250), commRange=250)
	net.add_node(pos=(100, 574), commRange=300)
	net.add_node(pos=(395, 350), commRange=300)
	net.add_node(pos=(250, 500), commRange=300)
	net.add_node(pos=(404, 145), commRange=450)
	net.add_node(pos=(374, 195), commRange=300)
	net.add_node(pos=(147, 220), commRange=250)
	net.add_node(pos=(298, 402), commRange=300)
	return net

def tree_network():
	net = Network()
	net.add_node(pos=(300, 559), commRange=370)
	net.add_node(pos=(410, 520), commRange=370)
	net.add_node(pos=(150, 500), commRange=200)
	net.add_node(pos=(490, 480), commRange=100)
	net.add_node(pos=(50, 400), commRange=170)
	net.add_node(pos=(200, 430), commRange=130)
	net.add_node(pos=(400, 400), commRange=150)
	net.add_node(pos=(480, 380), commRange=130)
	net.add_node(pos=(320, 300), commRange=140)
	net.add_node(pos=(15, 330), commRange=100)
	net.add_node(pos=(140, 350), commRange=150)
	net.add_node(pos=(370, 215), commRange=140)
	net.add_node(pos=(511, 405), commRange=50)
	net.add_node(pos=(490, 354), commRange=50)
	net.add_node(pos=(200, 300), commRange=105)
	return net

def test_network():
	net = one_node_network()
	net.algorithms = (DF_STAR, )
	sim = Simulation(net)

	try:
		sim.run()
	except Exception, e:
		write_pickle(net, 'net_exception.npc.gz')
		raise e
	for node in net.nodes():
		
		assert node.status == 'DONE'
		assert len(node.memory['unvisitedNodes']) == 0

if __name__=='__main__':
	test_network()
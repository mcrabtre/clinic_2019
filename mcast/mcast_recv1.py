import socket
import struct
import pickle
import numpy
#import queue

kill = False
prev = 0


def m_recv(node, stage, q, priority):
    global prev
    while not kill:
        if stage == 1:
            ip_switcher = {
                1: '224.3.29.71',
                2: '224.3.29.72',
                3: '224.3.29.73',
                4: '224.3.29.74',
                5: '224.3.29.75',
            }
            port_switcher = {
                1: 5001,
                2: 5002,
                3: 5003,
                4: 5004,
                5: 5005,
            }
        else:
            ip_switcher = {
                1: '224.3.29.76',
                2: '224.3.29.77',
                3: '224.3.29.78',
                4: '224.3.29.79',
                5: '224.3.29.80',
            }
            port_switcher = {
                1: 5006,
                2: 5007,
                3: 5008,
                4: 5009,
                5: 5010,
            }
        MCAST_GRP = ip_switcher.get(node, '0.0.0.0')
        MCAST_PORT = port_switcher.get(node, 0000)
        server_addr = ('',MCAST_PORT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #print('bound to ', server_addr)
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack("=4sl", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920)  # max buff size for pi /proc/sys/net/core/rmem_max
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_TTL, 20)
        sock.setsockopt(socket.SOL_IP, socket.IP_MULTICAST_LOOP, 1)
        buff = 1470  # not (necessarily) the same as set value
        sock.bind(server_addr)
        recvd = b''
        while True:
            #print('Attempting to receive from ', MCAST_GRP, MCAST_PORT)
            part = sock.recv(buff)
            recvd = recvd + part
            if len(part) < buff:
                break
        rec = pickle.loads(recvd)
        #print('Received Data')
        #print()
        #print(rec)
        if not(numpy.array_equal(rec, prev)):
            print('received ', len(recvd), ' bytes of data from node ', node, ' stage ', stage, ' priority ', priority)
            q.put((priority, rec))
            prev = rec
        sock.close()


#qu = queue.Queue()
#m_recv(1, 1, qu, 1)
#print('at the bottom of the ocean')
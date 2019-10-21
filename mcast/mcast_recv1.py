import socket
import struct
import pickle
import queue

kill = False


def m_recv(node, stage, q, priority):
    while not kill:
        ip_switcher = {
            1: '224.3.29.71',
            2: '224.3.29.72',
            3: '224.3.29.73',
            4: '224.3.29.74',
            5: '224.3.29.75',
        }
        MCAST_GRP = ip_switcher.get(node, '0.0.0.0')
        port_switcher = {
            1: 5007,
            2: 5008,
        }
        MCAST_PORT = port_switcher.get(stage, 0000)
        server_addr = ('',MCAST_PORT)
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        #print('bound to ', server_addr)
        group = socket.inet_aton(MCAST_GRP)
        mreq = struct.pack("=4sl", group, socket.INADDR_ANY)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 81920) #max buff size for pi. see /proc/sys/net/core/rmem_max
        buff = sock.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF) #not (necessarily) the same as set value
        sock.bind(server_addr)
        recvd = b''
        on = True
        while on:
            print('Attempting to receive from ', MCAST_GRP)
            recvd, addr = sock.recvfrom(buff)
            if recvd:
                on = False
        print('received ', len(recvd), ' bytes of data from ', addr)
        rec = pickle.loads(recvd)
        #print('Received Data')
        #print()
        print(rec)
        q.put((priority, rec))
        sock.close()


q = queue.Queue()
m_recv()
#print('at the bottom of the ocean')
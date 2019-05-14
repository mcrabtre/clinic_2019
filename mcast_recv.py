import socket
import struct
import pickle

def m_recv():

    MCAST_GRP = '224.1.1.1'
    MCAST_PORT = 5007

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((MCAST_GRP, MCAST_PORT))
    mreq = struct.pack("=4sl", socket.inet_aton(MCAST_GRP), socket.INADDR_ANY)

    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)

    recvd = b''
    on = True
    while on:

        recvdPart, addr = sock.recvfrom(8192)
        recvd += recvdPart #taking portions of what was recieved and adding to what we have
        print(len(recvd))
        if len(recvd) >= 6000: #== b'': until we recieve an empty bit
              on = False
              
    print(len(recvd))
    rec = pickle.loads(recvd)
    print('Recieved w')
    print(len(rec.w))        
      
      
    return rec.w,rec.tau#,recvd
    sock.close()
    

#use:
w,tau = m_recv()













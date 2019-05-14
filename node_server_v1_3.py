import pickle
import socket


def server(host):
    
    host = host
    port = 65432
    keep_running = True

    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((host, port))

    s.listen()
    while keep_running:
        conn, addr = s.accept()
        print ('Got connection', addr)
        recvd = b''
        while True:
            recvdPart = conn.recv(1024)
            recvd += recvdPart #taking portions of what was recieved and adding to what we have
            if not recvdPart: #== b'': until we recieve an empty bit
                break                
        print(len(recvd))
        rec = pickle.loads(recvd)
        print('Recieved w')
        conn.close
        
        if len(rec.w) != 0:
            keep_running = False
            
    return rec.w,rec.tau,rec.nodenum,rec.k #,recvd
    s.close()    


##host = '192.168.0.11'
##w,tau,nodenum,recvd = server(host)
##print('tau = ',tau,'; nodenum ',nodenum)
##print('length w: ',len(w))
##print('length xmitted bits: ',len(recvd))




import os


def run():
    os.system('hostname -I > output.txt')  # these 6 commands reads ip address from linux OS
    ip_file = open('output.txt', 'r')
    n_ip = ip_file.readline()
    nodeIP = n_ip.rstrip(' \n')
    ip_file.close()
    os.remove('output.txt')
    print(nodeIP)
    print(nodeIP.)
    print(nodeIP[1])


run()

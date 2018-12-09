# -*- coding: utf-8 -*-
import serial
import re
import binascii
import socket
from bluetooth import *

#PARAMETROS ANTENA

TCP_IP = '192.168.25.112'
TCP_PORT = 2112
BUFFER_SIZE = 1024

stx = "\x02"
etx = "\x03"
read = "sMN TAreadTagData 0 3 0 "
write = "sMN TAwriteTagData 0 3 0 "
trys = " 32 "
size_word = "6"
NoC = "+24 "

#PARAMETROS BALANÇA

bal = serial.Serial("/dev/ttyUSB0", 9600, timeout = 1)
mensagem = str(chr(5))

#PARAMETROS BLUETOOTH

server_sock=BluetoothSocket( RFCOMM )
server_sock.bind(("",PORT_ANY))
server_sock.listen(1)

port = server_sock.getsockname()[1]

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( server_sock, "SampleServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
#                   protocols = [ OBEX_UUID ] 
                    )
                   
print("Waiting for connection on RFCOMM channel %d" % port)

client_sock, client_info = server_sock.accept()
print("Accepted connection from ", client_info)

# INICIALIZA COMM

try:
    while True:
        x = client_sock.recv(1024).decode()
        
        if len(x) == 0: break
        print("received [%s]" % x)
        #client_sock.send("oi teste")


        print ("starting...")



        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((TCP_IP,TCP_PORT))

    #---------------------------------------------------------------------------------
        if len(x) ==  12:
            ##----------------escrita--------------------
            
            data = x.encode()
            msgW = stx + write + size_word + trys + NoC + data.hex() + etx
            s.send(msgW.encode())
            data = s.recv(BUFFER_SIZE)

            dataR = data.decode("utf-8")

            if dataR == stx + "sAN TAwriteTagData 1 " + size_word + etx:
                data_inf = "Escrita efetuada"
            else:
                data_inf = "Escrita não efetudada"

            print (data_inf)
            client_sock.send(data_inf + " ")
            print ()
    #-----------------------------------------------------------------------------------
        elif x == 'LERTAG':
            ##----------------leitura--------------------

            msgR = stx + read + size_word + trys + etx
            s.send(msgR.encode())
            data = s.recv(BUFFER_SIZE)

            list = data.decode("utf-8").split()

            info_aux = []
            info_aux = list[len(info_aux)-1].split("\x03")
            info = info_aux[0]

            if info == "0":
                data_inf = "Sem TAG"
            else:
                data_inf = bytes.fromhex(info).decode("utf-8")

            print ("received data: " + data_inf)
            client_sock.send("received data: " + data_inf + " ")
            
            print ()
    #----------------------------------------------------------------------------------
        elif x == 'LERBALANCA':
            if bal.isOpen():
                
                print(mensagem)
                print(bal.portstr)
                bal.write(mensagem.encode("ascii"))
                
                bal.flushInput()
                
                h_peso = bal.readline()
                list = h_peso.decode("utf-8")
                
                peso = re.findall('\x02(.*?)\x03', list)
                peso1 = int (peso[0])
                r_peso = peso1 / 1000
                s_peso = str(peso[0])
                hpeso = binascii.hexlify(s_peso.encode())
                
                print(s_peso)
                print(hpeso)
                print(r_peso)
                            
                client_sock.send(s_peso + " ")

            
    #----------------------------------------------------------------------------------
        else:
            print("comando indefinido")

except IOError:
    pass

print("disconnected")

client_sock.close()
server_sock.close()
print("all done")
        







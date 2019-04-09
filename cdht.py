#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 22 23:21:18 2018

@author: z5151899
"""
import sys
import socket
import threading
import time

HOST = '127.0.0.1'
BASE = 40000

def PortNum(peer):
    return BASE+int(peer)

def pingResponse():
    global ack1,ack2
    while 1:#accepting requests and send response from its two predecessors->server
        ReceivedMessage,clientaddr = sock.recvfrom(1024)
        sen = ReceivedMessage.split()
        #print(sen)
        if sen[-1]=="request": 
            printrev = "A ping request message was received from peer "+sen[2]
            print(printrev)
            #ResponseMessage = "A ping response message was received from peer" +str(PeerID)
            #sock.send(ResponseMessage,(HOST,clientaddr[1]))
            if pred1[-1]==-1 or pred2[-1]==-1:
                if sen[0] == '1':
                    pred1.append(clientaddr[1])
                    #print("pred1: ",pred1[-1])
                else:
                    pred2.append(clientaddr[1])
                    #print("pred2: ",pred2[-1])
            if clientaddr[1]!=pred1[-1] and clientaddr[1]!=pred2[-1]:
                if sen[0] == '1':
                    pred1.append(clientaddr[1])
                    #print("pred1: ",pred1[-1])
                else:
                    pred2.append(clientaddr[1])
                    #print("pred2: ",pred2[-1])
            if sen[0]=="1":
                #sock1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                ack1sentence = "ACK1 "+sen[1] + ' ' + str(PeerID) + ' ' +"response"
                sock.sendto(ack1sentence,(HOST,clientaddr[1]))
            elif sen[0]=="2":
                #sock2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                ack2sentence = "ACK2 "+sen[1] + ' ' + str(PeerID)+ ' ' +"response"
                sock.sendto(ack2sentence,(HOST,clientaddr[1]))    
        
        else:
            printres = "A ping response message was received from peer "+sen[2]
            print(printres)
            if sen[0]=="ACK1":
                ack1 = int(sen[1])
            elif sen[0]=="ACK2":
                ack2 = int(sen[1]) 

        
def pingRequest():
    global count1,count2,ack1,ack2,gap1,gap2
    lastpingtime = 0
    sock.settimeout(10)
    while 1:
        if(time.time()-lastpingtime)>5:#timestep same as time.sleep(5)
            #sockTCP1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sentence1 = "1 "+str(count1) +' ' + str(PeerID) + ' ' +"request"#means send from pred1(near)
            sock.sendto(sentence1,(HOST,PortNum(succ1[-1])))
            count1+=1
            
            #sockTCP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sentence2 = "2 "+str(count2) +' ' + str(PeerID)+ ' ' +"request"#means send from pred2(not near)
            sock.sendto(sentence2,(HOST,PortNum(succ2[-1])))
            count2+=1
            lastpingtime = time.time()
                
            gap1=count1-ack1#acknum - seqnum
            #print("gap1 is {}".format(gap1))
            if gap1 > 4:
                print("{} is no longer alive\n".format(succ1[-1]))
                succ1.append(succ2[-1])
                gap1 = 0
                ack1 = count1
                print("My first successor is now {}\n".format(succ1[-1]))
                #print(succ1[-1])
                sockTCP1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockTCP1.connect((HOST,PortNum(succ1[-1])))
                sentence1 = "ask " + str(PeerID)
                sockTCP1.sendall(sentence1.encode())
                sockTCP1.close()
            #time.sleep(5)        
            gap2 = count2-ack2
            #print("gap2 is {}".format(gap2))
            if gap2>4:
                print("{} is no longer alive\n".format(succ2[-1]))
                print("My first successor is now {}\n".format(succ1[-1]))
                sockTCP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sockTCP2.connect((HOST,PortNum(succ1[-1])))
                sentence2 = "ask " + str(PeerID)
                sockTCP2.sendall(sentence2.encode())
                sockTCP2.close()

#borrowed code from: https://github.com/mohammadg/Circular-DHT-Network/blob/master/src/cdht_ex.py
#Returns values to say if file should be forwarded, if file is available here 
#or if file will be available at the next peer
def check(filenum):
    hashfile = int(filenum) % 256
    if hashfile == PeerID:#current PeerID has the file
        return 1
    elif succ1[-1] < PeerID and (hashfile > PeerID or hashfile <=succ1[-1]):#succ1 has the file,special case
        return 2
    elif PeerID < hashfile<=succ1[-1]:#succ1 has the file
        return 2  
    else:
        return 3

def TCPRequest(senderpeer,filenum,func):#client
    if func == 1:#current peer has the file
        print("File {} is here.\nA response message, destined for {}, has been sent\n".format(filenum,senderpeer))
    elif func == 2: #send churn message to succ1, which has the file
        sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP.connect((HOST,PortNum(succ1[-1])))
        sentence = '1 Request ' + str(filenum) +' '+ str(senderpeer)
        sockTCP.sendall(sentence.encode())  #send file to succ1
        print("File {} is not here.\nFile request message has been forwarded to my successor\n".format(filenum))
        sockTCP.close()
        #sockTCP.close()
    elif func ==3 :#send message to its successors
        sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP.connect((HOST,PortNum(succ1[-1])))
        sentence = '2 Request ' + str(filenum) +' ' + str(senderpeer)
        sockTCP.sendall(sentence.encode())  #send file to succ1
        sockTCP.close()
        print("File {} is not here.\nFile request message has been forwarded to my successor\n".format(filenum))
    elif func == 4:
        sockTCP1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP1.connect((HOST,pred2[-1]))
        sentence1 = '3 Departure ' + str(succ1[-1])#tell pred2(not near) about new succ2(which is current's succ1)
        sockTCP1.sendall(sentence1.encode())
        sockTCP1.close()
        
        sockTCP2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP2.connect((HOST,pred1[-1]))
        sentence2 = '4 Departure ' + str(succ1[-1]) +' '+ str(succ2[-1])#tell pred1(near) about new succ1 andnew  succ2
        sockTCP2.sendall(sentence2.encode())
        sockTCP2.close()
        
        sockTCP3 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP3.connect((HOST,PortNum(succ2[-1])))
        sentence3 = '5 Departure ' + str(pred1[-1])#tell succ2(not near) about new pred2(which is current's pred1) 
        sockTCP3.sendall(sentence3.encode())
        sockTCP3.close()
        
        sockTCP4 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP4.connect((HOST,PortNum(succ1[-1])))
        sentence4 = '6 Departure ' + str(pred1[-1]) + ' ' + str(pred2[-1])#tell succ1(near) about new pred1 and new pred2
        sockTCP4.sendall(sentence4.encode())
        sockTCP4.close()


def TCPResponce():#server
    global ack1,ack2,count1,count2,gap1,gap2
    
    try:
        sockTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sockTCP.bind((HOST,PortNum(PeerID)))#bind with pred to receive messages
        print('TCPserver bind complete')
    except socket.error as emsg:
        print('TCPserver Bind failed.')
        sys.exit()
    #sockTCP.settimeout(20)
    while 1:
        sockTCP.listen(2)  
        #print("sockTCP is listening")
        connectionsocket,addr = sockTCP.accept()
        sentence = connectionsocket.recv(2048).decode().split()     
        if sentence[0] == '1':#current peer has the file
            sockTCPRes = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sockTCPRes.connect((HOST,PortNum(sentence[3])))
            sen = "File "+ str(PeerID) + ' ' +str(sentence[2])
            sockTCPRes.sendall(sen.encode())
            sockTCPRes.close()
            print("File {} is here.\nA response message, destined for {}, has been sent\n".format(sentence[2],sentence[3]))
        elif sentence[0] == '2' :
            flag = check(sentence[2])
            if flag == 1:
                TCPRequest(sentence[3],sentence[2],1)
            elif flag == 2:
                TCPRequest(sentence[3],sentence[2],2)#2 for special case that request succ1, knowing which has the file
            else:
                TCPRequest(sentence[3],sentence[2],3)
        elif sentence[0] == '3':#pred2(not near)
            succ2.append(sentence[2].encode())
            gap2 = 0
            ack2 = count2
            print("My first successor is now {}\n My second successor is now {}.\n".format(succ1[-1],succ2[-1]))
        elif sentence[0] == '4':#pred1(near)
            succ1.append(sentence[2].encode())
            succ2.append(sentence[3].encode())
            print("My first successor is now {}\n My second successor is now {}.\n".format(succ1[-1],succ2[-1]))
            gap1 = 0
            ack1 = count1
            gap2 = 0
            ack2 = count2
        elif sentence[0] == '5':#succ2(not near)
            pred2.append(int(sentence[2].encode()))
            #print("My first predecessor address is now {}\n My second predecessor address is now {}.".format(pred1[-1],pred2[-1]))
        elif sentence[0] == '6':#succ1(near)
            pred1.append(int(sentence[2].encode()))
            pred2.append(int(sentence[3].encode()))
            #print("My first predecessor address is now {}\n My second predecessor address is now {}.".format(pred1[-1],pred2[-1]))        
        elif sentence[0] == "File":
            print("Received a response message from peer {}, which has the file {}.\n".format(sentence[1],sentence[2]))
        elif sentence[0] == "ask": 
            sockTCP5 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #print(addr[1])
            sockTCP5.connect((HOST,PortNum(sentence[1])))
            sentence = "reply " + str(succ1[-1])
            sockTCP5.sendall(sentence.encode())
            sockTCP5.close()
        elif sentence[0] == "reply":
            succ2.append(sentence[1])
            gap2 = 0
            ack2 = count2
            print("My second successor is now {}\n".format(succ2[-1]))
            
        
        
            
if len(sys.argv)!=4:
    print(sys.stderr,'usage:',sys.argv[0],'[peer identifier] [successor #1] [successor #2 identifier]')
    sys.exit()
PeerID = int(sys.argv[1])
succ1 = [int(sys.argv[2])]
succ2 = [int(sys.argv[3])]
pred1 = [-1]
pred2 = [-1]
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((HOST,PortNum(PeerID)))
    print('Socket bind complete')
except socket.error as emsg:
    print('Bind failed.')
    sys.exit()

count1 = 0
count2 = 0
ack1 = 0
ack2 = 0
gap1 = 0
gap2 = 0
#Borrowed code:
https://stackoverflow.com/questions/2846653/how-to-use-threading-in-python
t1 = threading.Thread(target=pingRequest,args=())
t3 = threading.Thread(target=pingResponse,args=())
t4 = threading.Thread(target = TCPResponce,args = ())
t1.daemon = True
t3.daemon = True
t4.daemon = True
t1.start()
t3.start()
t4.start()


while 1:
    userinput = raw_input()
    #print '{}'.format(userinput)     
    if userinput.startswith('request'):
        try:
            filenumstr = userinput.split()[1]
            filenumint = int(filenumstr)
            if not (0 <=filenumint<=9999) or len(filenumstr)!=4:
                raise ValueError('Invalid request file provided.')
        except:
            print("Invalid file was requestd. File name must be a 4 length numeral.")
            continue;
        flag = check(filenumint)
        if flag == 1:#current port has the file
            TCPRequest(PeerID,filenumint,1)
           
        elif flag == 2:
            TCPRequest(PeerID,filenumint,2)#2 for special case that request succ1, kowning which has the file
        else:    
            TCPRequest(PeerID,filenumint,3)
    elif userinput.startswith('quit'):
        TCPRequest(PeerID,-1,4)
        
        print("Peer {} will depart from this network.".format(PeerID))
        t1.join(2)
        t3.join(2)
        t4.join(2)
        break            



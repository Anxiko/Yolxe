# -*- coding: utf-8 -*-

import socket
import string

#Strip a string left and right
def string_strip(string):
        return string.strip()

#Finds a string on a list of strings
def find_any(str,keys):
	for key in keys:
		if str.find(key)!=-1:
			return True
	return False

#Logs the bot into the IRC
def get_in(sck,nick,ident,host,machine,realname):
	sck.send("NICK %s\r\n" % nick)
	sck.send("USER %s %s %s :%s\r\n" % (ident, host, machine, realname))
	print "Logging in as ",nick
	return True

#Establish connection
def connect(host,port):
        s=socket.socket()
        s.connect((host, port))
        return s

#Get lines
def get_lines(sck):
        read=sck.recv(10000)
        output=[]
        for line in read.split('\n'):
                line=string_strip(line)
                if len(line)>0:
                        output.append(line)

        return output

#Main function
def main():
        #Connection config
        HOST="irc.quakenet.org"
        PORT=6667
        NICK="Yolxe"
        IDENT="Nereon"
        REALNAME="Yolxe Yaim Keol"
        MACHINE="NERSYS_AXK"
        CHAN="#hawkensiege"
        MASTERS=["37.222.127.112"]
        
        #Connect to the server
        s=connect(HOST,PORT)
        
        #Control flags
        stay=True
        loged=False

        #Main loop
        while stay:
                #Check for input
                if not loged:
                        loged=get_in(s,NICK,IDENT,HOST,MACHINE,REALNAME)
                #Split it in lines
                for temp in get_lines(s):
                        print "Line read ->",temp
                        temp=temp.split(CHAN + ':')
                        if (len(temp)<1):#If no other message
                                continue#Skip

                        input_string=temp[0]
                        if input_string.find("PING") != -1:
                                pingid = input_string.split()[1]
                                s.send("PONG %s\r\n" % pingid)
                                print "PONG sent"
                        elif input_string.find("MODE "+NICK+" +i")!=-1:
                                s.send("JOIN %s\r\n" % CHAN)
                        elif input_string.find("Nickname is alredy in use")!=-1:
                                print "WARNING: Nickname in use"
                                loged=False
                                NICK+="_"
                        else:
                                sp=input_string.split("PRIVMSG")
                                if len(sp)>1:
                                        sender=sp[0]
                                        receiver,msg=sp[1].split(':')
                                        receiver=string_strip(receiver)
                                        sender=string_strip(sender)
                                        print '[',sender,']',"->",'[',receiver,']','=>','[',msg,']'
                                        print "Command received"

                                        if msg=="!out":
                                                print "Quitting"
                                                s.send("QUIT %s" % ("Yolxe out!"))
                                                s.close()
                                                stay=False


#Start
if __name__=="__main__":
        main()

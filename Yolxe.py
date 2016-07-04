# -*- coding: utf-8 -*-

import socket
import string
import random
import ConfigParser

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

#Send a message to someone
def say(sck,recv,msg):
        output="PRIVMSG "+recv+" :"+msg+"\r\n"
        print "Saying","=>",output
        sck.send(output)

#Main function
def main():
        config = ConfigParser.ConfigParser()
        config.read("config.ini")
        #Connection config
        HOST=config.get('ConnectInfo', 'host')
        PORT=config.getint('ConnectInfo', 'port')
        NICK=config.get('ConnectInfo', 'nick')
        IDENT=config.get('ConnectInfo', 'ident')
        REALNAME=config.get('ConnectInfo', 'realname')
        MACHINE=config.get('ConnectInfo', 'machine')
        CHAN=config.get('ConnectInfo', 'chan')
        MASTERS=config.get('ConnectInfo', 'masters')

        revolver=None
        
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
                                        receiver=receiver[1:]
                                        sender=string_strip(sender)
                                        msg=string_strip(msg)
                                        
                                        print '[',sender,']',"->",'[',receiver,']','=>','[',msg,']'
                                        print "Command received"

                                        if msg=="!out":
                                                print "Quitting"
                                                s.send("QUIT :%s" % (NICK+" out!\r\n"))
                                                s.close()
                                                stay=False

                                        if msg=="!spin":
                                                revolver=random.randint(0,5)
                                                say(s,CHAN,"Weapon loaded")
                                                print "Bullet on ",revolver
                                        if msg=="!fire":
                                                if revolver==None:
                                                        say(s,CHAN,"Load the weapon first, with !spin")
                                                elif revolver==0:
                                                        revolver=None
                                                        say(s,CHAN,"BANG!")
                                                else:
                                                        revolver-=1
                                                        say(s,CHAN,"CLICK")
                                                        print "Bullet on ",revolver
#Start
if __name__=="__main__":
        main()

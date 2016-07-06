# -*- coding: utf-8 -*-

import socket
import string
import random
import ConfigParser

#Classes

#Config and tools of the bot
class ConfigBot:
        #Connection config
        PORT=6667
        NICK="Yolxe"
        IDENT="Nereon"
        REALNAME="Yolxe Yaim Keol"
        MACHINE="NERSYS_AXK"
        CHAN=None
        HOST=None

        #Socket
        s=None

        #Control flags
        loged=False
        stay=True

        def __init__(self):

                #Load the file
                config = ConfigParser.ConfigParser()
                config.read("config.ini")
                #Connection config

                #Read values that are not critical

                #Port
                try:
                        self.PORT=config.getint('ConnectInfo', 'port')
                except:
                        print "PORT not loaded, defaulting to "+str(self.PORT)
                #Nick
                try:
                        self.NICK=config.get('ConnectInfo', 'nick')
                except:
                        print "NICK not loaded, defaulting to "+str(self.NICK)

                #Ident
                try:
                        self.IDENT=config.get('ConnectInfo', 'ident')
                except:
                        print "IDENT not loaded, defaulting to "+str(self.IDENT)

                #Real name
                try:
                        self.REALNAME=config.get('ConnectInfo', 'realname')
                except:
                        print "REALNAME not loaded, defaulting to "+str(self.REALNAME)

                try:
                        self.MACHINE=config.get('ConnectInfo', 'machine')
                except:
                        print "MACHINE not loaded, defaulting to "+str(self.MACHINE)

                #Critical values, MUST be present
                self.HOST=config.get('ConnectInfo', 'host')
                self.CHAN=config.get('ConnectInfo', 'chan')

                #Connect to the server
                self.s=connect(self.HOST,self.PORT)

#Message class
class Message:
        #Members
        prefix=None #Prefix of the sender (optional)
        command=None #Command
        args=[] #Arguments of the commmand

        #Constructor
        def __init__(self,s):

                try:
                        prefix = ''
                        trailing = []
                        if s:
                                if s[0] == ':':
                                        prefix, s = s[1:].split(' ', 1)
                                if s.find(' :') != -1:
                                        s, trailing = s.split(' :', 1)
                                        args = s.split()
                                        args.append(trailing)
                                else:
                                        args = s.split()
                                command = args.pop(0)
                                self.prefix,self.command,self.args=prefix,command,args
                except:
                        self.prefix=None
                        self.command="PARSE_ERROR"
                        self.args=[s]

        #Methods

        #Print the message
        def __repr__(self):
                return str(self.prefix)+" => "+self.command+"("+str(self.args)+")"

        #Get a formatted private message
        def fmt_privmsg(self):

                #Data to be collected
                nick=None
                chan=None
                text=None

                #If the command is a private message, parse it
                if self.command=="PRIVMSG":
                        #Get the nick
                        if self.prefix is not None:
                                index=self.prefix.find("!")
                                if index>0:
                                        nick=self.prefix[:index]
                        #Get the channel and text
                        chan=self.args[0]
                        if chan.find("#")<0:
                                chan=None
                        text=self.args[1]
                #return the parsed data
                return (nick,chan,text)

class Plugin:
        #Members

        #Interface
        start=None #Function called at the start
        process=None #Function called to process a message
        stop=None #Function called at quit

        def __init__(self,f_start,f_process,f_stop):
                self.start=f_start
                self.process=f_process
                self.stop=f_stop
                
#Functions


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
        read=sck.recv(20000)
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

#Revolver methods

#Start
def rev_start(self,c):
        self.rev=None

def rev_process(self,c,msg):
        if msg.command=="PRIVMSG":
                (nick,chan,text)=msg.fmt_privmsg()
                if chan is None:
                        chan=nick
                if (text=="!spin"):
                        self.rev=random.randint(0,5)
                        say(c.s,chan,"Weapon loaded")
                elif (text=="!fire"):
                        if self.rev==None:
                                say(c.s,chan,"Load the weapon first, with !spin")
                        elif self.rev==0:
                                self.rev=None
                                say(c.s,chan,"BANG!")
                        else:
                                self.rev-=1
                                say(c.s,chan,"CLICK")
                                print "Bullet on ",self.rev
                else:
                        return False
                return True

#Ping methods

#Process
def ping_process(self,c,msg):
        if msg.command=="PING":
                c.s.send("PONG :"+msg.args[0]+"\r\n")
                return True
        return False

#Out methods

#Process
def out_process(self,c,msg):
        if msg.command=="PRIVMSG":
                (_,_,text)=msg.fmt_privmsg()
                if text=="!out":
                        c.stay=False
                        print "Quitting"
                        c.s.send("QUIT :%s" % (c.NICK+" out!\r\n"))
                        c.s.close()
                        return True

        return False

#Join methods

#Process
def join_process(self,c,msg):
        if msg.command=="MODE":
                if msg.args[0]==c.NICK and msg.args[1]=="+i":
                        c.s.send("JOIN "+c.CHAN+"\r\n")
                        return True
        return False

#Nick methods

#Process
def nick_process(self,c,msg):
        if msg.command=="433":
                c.loged=False
                c.NICK=c.NICK+"_"
                return True
        return False

#Printer methods

#Process
def printer_process(self,c,msg):
        print msg
        return False

#Smiley method

#Look for the smiley on the string
def smiley_look(dic,string):
        words=string.split()#Split the line in words
        for smiley in dic.keys():#Check the words against each smiley
                if smiley in words:#Check if the smiley is one of the words
                        return dic[smiley]#Return the answer
        return None#Nothing found
                
        
#Start
def smiley_start(self,c):
        self.dic={}
        self.dic[":("]=":)"
        self.dic["):"]="(:"
        self.dic["D:"]=":D"
        self.dic[":c"]="c:"
        self.dic[":C"]="C:"
        self.dic[":/"]=":>"
        self.finder=smiley_look

#Process
def smiley_process(self,c,msg):
        if msg.command=="PRIVMSG":
                (nick,chan,text)=msg.fmt_privmsg()
                response=self.finder(self.dic,text)
                if response is not None:
                        if chan is None:
                                chan=nick
                        say(c.s,chan,"Cheer up "+nick+" "+response)
                        return True
        return False
        

#Main function
def main():
        #Config class
        c=ConfigBot()

        #Plugins
        rev_plug=Plugin(rev_start,rev_process,None)#Russian roulette plugin
        ping_plug=Plugin(None,ping_process,None)#Ping plugin
        out_plug=Plugin(None,out_process,None)#Out plugin
        join_plug=Plugin(None,join_process,None)#Join plugin
        nick_plug=Plugin(None,nick_process,None)#Nick plugin
        print_plug=Plugin(None,printer_process,None)#Printer plugin
        smiley_plug=Plugin(smiley_start,smiley_process,None)#Smiley plugin

        plugins=[]

        plugins.append(print_plug)
        
        plugins.append(ping_plug)
        plugins.append(join_plug)
        plugins.append(out_plug)
        plugins.append(nick_plug)

        plugins.append(smiley_plug)
        plugins.append(rev_plug)
        

        for p in plugins:
                if p.start is not None:
                        p.start(p,c)

        #Main loop
        while c.stay:
                #Check for input
                if not c.loged:
                        c.loged=get_in(c.s,c.NICK,c.IDENT,c.HOST,c.MACHINE,c.REALNAME)
                #Split it in lines
                for line in get_lines(c.s):
                        msg=Message(line)

                        for p in plugins:
                                if p.process is not None:
                                        if p.process(p,c,msg):
                                                break
                        
                        #if input_string.find("Nickname is alredy in use")!=-1:

                        for p in plugins:
                                if p.stop is not None:
                                        p.stop(p,c)
#Start
if __name__=="__main__":
        main()

# -*- coding: utf-8 -*-

import socket
import string

HOST="irc.quakenet.org"
PORT=6667
NICK="Yolxe"
IDENT="Nereon"
REALNAME="Yolxe Yaim Keol"
MACHINE="NERSYS_AXK"
CHAN="#hawkensiege"
masters=["37.222.127.112"]

def find_any(str,keys):
	for key in keys:
		if str.find(key)!=-1:
			return True
	return False

def get_in():
	s.send("NICK %s\r\n" % NICK)
	s.send("USER %s %s %s :%s\r\n" % (IDENT, HOST, MACHINE, REALNAME))
	loged=True
	print "Logging in as ",NICK

s=socket.socket( )
s.connect((HOST, PORT))

stay=True
loged=False

while stay:
	if not loged:
		get_in()
	read=s.recv(1024)
	for temp in read.split("\n"):
		temp.rstrip()
		temp=temp.split(CHAN + ':')
		if (len(temp)<1):
			continue
		print temp
		if temp[0].find("PING") != -1:
			pingid = temp[0].split()[1]
			s.send("PONG %s\r\n" % pingid)
			print "PONG sent"
		elif temp[0].find("MODE "+NICK+" +i")!=-1:
			s.send("JOIN %s\r\n" % CHAN)
		elif temp[0].find("Nickname is alredy in use")!=-1:
			print "WARNING: Nickname in use"
			loged=False
			NICK+="_"
		else:
			sp=temp[0].split("PRIVMSG")
			if len(sp)>1:
				print sp[0]," -> ",sp[1]
				if find_any(sp[0],masters):
					print "Command received"
					if sp[1].find("!out"):
						print "Quitting"
						s.send("QUIT %s" % ("Yolxe out!"))
						s.close()
						stay=False

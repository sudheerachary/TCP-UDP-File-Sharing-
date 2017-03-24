import os
import socket
import time
from socket import *

def shortList ( clientSocket, timestamp1, timestamp2 ):
	os.chdir ( "syncShared" )
	# index shortlist 2015-03-20 13:20:10.888016945 +0530 2018-03-20 13:20:10.888016945 +0530
	output = ""
	command = "find ./ -type f -newermt '" + str ( timestamp1 ) + "' ! -newermt '" + str ( timestamp2 ) + str ( "'" )
	files = os.popen ( command ).read ( )
	files = files.split ( "\n" )
	for file in files:
		if file == '':
			output += str ( os.popen ( "ls -l "+str ( file ) ).read ( ) )
	clientSocket.send ( output )
	os.chdir ( ".." )	

def longList ( clientSocket ):
	os.chdir ( "syncShared" )
	command = "ls -lah"
	output = os.popen ( command ).read ( ) 
	clientSocket.send ( output ) 
	os.chdir ( ".." )

def regex ( clientSocket, matcher ):
	os.chdir ( "syncShared" )
	command = "ls -l " + str ( matcher )
	output = os.popen ( command ).read ( )
	clientSocket.send ( output )
	os.chdir ( ".." )

def verify ( clientSocket, filename ):
	os.chdir ( "syncShared" )
	command = "md5sum " + str ( filename )
	output = os.popen ( command ).read ( )
	clientSocket.send ( output ) 
	os.chdir ( ".." )

def checkall ( clientSocket ):
	os.chdir ( "syncShared" )
	output = ""
	command = "ls"
	files = os.popen ( command ).read ( )
	files = files.split ( "\n" )
	for file in files:
		if not file == '' and not os.path.isdir ( file ):
			command = "md5sum " + str ( file )
			result = os.popen ( command ).read ( )
			output += str ( result )
	clientSocket.send ( output )
	os.chdir ( ".." )

def tcpDownload ( clientUDPSocket, clientSocket, filename ):
	if os.path.exists ( filename ):
		if os.path.isdir ( filename ):
			clientUDPSocket.sendto ( "directory", addr )
			clientUDPSocket.sendto ( filename, addr )
			permissions = os.popen ( "stat -c ' %a ' " + filename ).read ( )
			clientUDPSocket.sendto ( permissions, addr )
			os.chdir ( filename )
			files = os.popen ( "ls" ).read ( )
			files = files.split ( "\n" )
			clientUDPSocket.sendto ( str ( len ( files ) - 1 ), addr )
			for file in files:
				if not file == '':
					tcpDownload ( clientUDPSocket, clientSocket, file )
			os.chdir ( ".." )
		else:
			clientUDPSocket.sendto ( "file", addr )
			clientUDPSocket.sendto ( filename, addr )
			permissions = os.popen ( "stat -c ' %a ' " + filename ).read ( )
			existence, address = clientSocket.recvfrom ( 1024 ) 
			if existence == "exists":
				command = "md5sum " + str ( filename )
				output = os.popen ( command ).read ( )
				output = output.split ( )
				clientUDPSocket.sendto ( output[0], addr )
				status, address = clientUDPSocket.recvfrom ( 1024 )
				if status == "continue": 
					clientUDPSocket.sendto ( str ( os.path.getmtime ( filename ) ), addr )
					process, address = clientUDPSocket.recvfrom ( 1024 )
					if process == "upload":
						# upload
						tcpFileUpload ( clientSocket, filename )
					else:
						# download
						tcpFileDownload ( clientSocket, filename )
			else:
				tcpFileDownload ( clientSocket, filename )
	else:
		clientUDPSocket.sendto ( "NotFound", addr )
		
def tcpFileDownload ( clientSocket, filename):
	try:
		file = open ( filename, "rb" )
		byte = file.read ( 1024 )
		while byte:
			clientSocket.send ( byte )
			byte = file.read ( 1024 )
		time.sleep ( 1 )
		clientSocket.send ( "Done" )
		file.close ( )
	except:
		print "Error"

def udpDownload ( clientUDPSocket, filename, addr ):
	if os.path.exists ( filename ):
		if os.path.isdir ( filename ):
			clientUDPSocket.sendto ( "directory", addr )
			clientUDPSocket.sendto ( filename, addr )
			permissions = os.popen ( "stat -c ' %a ' " + filename ).read ( )
			clientUDPSocket.sendto ( permissions, addr )
			os.chdir ( filename )
			files = os.popen ( "ls" ).read ( )
			files = files.split ( "\n" )
			clientUDPSocket.sendto ( str ( len ( files ) - 1 ), addr )
			for file in files:
				if not file == '':
					udpDownload ( clientUDPSocket, file, addr )
			os.chdir ( ".." )
		else:
			clientUDPSocket.sendto ( "file", addr )
			clientUDPSocket.sendto ( filename, addr )
			permissions = os.popen ( "stat -c ' %a ' " + filename ).read ( )
			clientUDPSocket.sendto ( permissions, addr )
			existence, address = clientUDPSocket.recvfrom ( 1024 )
			if existence == "exists":
				command = "md5sum " + str ( filename )
				output = os.popen ( command ).read ( )
				output = output.split ( )
				clientUDPSocket.sendto ( output[0], addr )
				status, address = clientUDPSocket.recvfrom ( 1024 )
				if status == "continue": 
					clientUDPSocket.sendto ( str ( os.path.getmtime ( filename ) ), addr )
					process, address = clientUDPSocket.recvfrom ( 1024 )
					if process == "upload":
						# upload
						udpFileUpload ( clientUDPSocket, filename )
					else:
						# download
						udpFileDownload ( clientUDPSocket, filename, addr )
			else:
				udpFileDownload ( clientUDPSocket, filename, addr )
	else:
		clientUDPSocket.sendto ( "NotFound", addr )

def udpFileDownload ( clientUDPSocket, filename, addr ):
	try:
		file = open ( filename, "rb" )
		byte = file.read ( 1024 )
		while byte:
			clientUDPSocket.sendto ( byte, addr )
			# data, addr = clientUDPSocket.recvfrom ( 1024 )
			byte = file.read ( 1024 )
		clientUDPSocket.sendto ( "done", addr )
		file.close ( )
	except:
        		print "Error"

# upload

def udpFileUpload ( clientUDPSocket, filename ):
	try:
	    file = open ( filename, "wb+")
	except:
	    # print "Error: File Not Found"
	    return
	
	while True:
		data, addr = clientUDPSocket.recvfrom ( 1024 )
		if data == "done":
			break
		file.write ( data )
	file.close ( )

def tcpFileUpload ( clientSocket, filename ):

	with open( filename, "wb" ) as file:
	    while True:
	        data = clientSocket.recv ( 1024 )
	        if data == "Done":
	            break
	        file.write ( data )
	file.close ( )

# upload

def synchronize ( clientUDPSocket, address ):
	os.chdir ( "syncShared" )
	files = os.popen ( "ls" ).read ( )
	files = files.split ( '\n' )
	clientUDPSocket.sendto ( str ( len ( files ) - 1 ), address )
	for file in files:
		if not file == '':
			udpDownload ( clientUDPSocket, file, address )
	os.chdir ( ".." )

if __name__ == "__main__":

	serverSocket = socket ( AF_INET, SOCK_STREAM )
	clientUDPSocket = socket ( AF_INET, SOCK_DGRAM )
	host = gethostname ( )
	port = 6001
	udpPort = 6002
	addr = ( host, udpPort )
	serverSocket.bind ( ( host, port ) )
	serverSocket.setsockopt ( SOL_SOCKET, SO_REUSEADDR, 1)
	serverSocket.listen ( 5 )
	# print ">>> Server Listening... "
	
	clientSocket, clientAddress = serverSocket.accept ( )

	while True:
		choice = str ( clientSocket.recv ( 1024 ) ) 

		if choice == "Y":
			argument = clientSocket.recv ( 1024 )

		elif choice == "N" or choice == "E":
			# print ">>> Synchronizing ..... "
			synchronize ( clientUDPSocket, addr )
			continue

		else:	
			# print ">>> Error: Not a Proper Input !"
			continue
			
		# print ">>> Serving ", argument
		argument = argument.split ( )

		if argument[0] == "index":
			
			if argument[1] == "longlist":
				longList ( clientSocket )

			elif argument[1] == "shortlist":
				shortList ( clientSocket, str ( str ( argument[2] ) + str ( ' ' ) + str ( argument[3] ) +str ( ' ' ) + str ( argument[4] ) ),
					 str ( str ( argument[5] ) + str ( ' ' ) + str ( argument[6] ) + str ( ' ' ) + str ( argument[7] ) ) )

			elif argument[1] == "regex":
				regex ( clientSocket, argument[2] )

			else:
				# print "Error: Command Not Found"
				continue

		elif argument[0] == "hash":
			
			if argument[1] == "verify":
				verify ( clientSocket, argument[2] )
		
			elif argument[1] == "checkall":
				checkall ( clientSocket )
		
			else:
				# print "Error: Command Not Found"
				continue

		elif argument[0] == "download":
			
			if argument[1] == "TCP":
				os.chdir ( "syncShared" )
				tcpDownload ( clientUDPSocket, clientSocket, argument[2] )
				os.chdir ( ".." )

			elif argument[1] == "UDP":
				os.chdir ( "syncShared" )
				udpDownload ( clientUDPSocket, argument[2], addr )
				os.chdir ( ".." )

			else:
				# print "Error: Command Not Found"
				continue

		elif argument[0] == "close":
			break

		else:
			# print "Error: Command Not Found"
			continue

	clientSocket.close ( )
	clientUDPSocket.close ( )
	serverSocket.close ( )
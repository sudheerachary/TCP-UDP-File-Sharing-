import os
import socket
import signal
import time
from socket import *

class AlarmException(Exception):
    pass

def alarmHandler(signum, frame):
    raise AlarmException

def nonBlockingRawInput ( prompt = "", timeout = 10 ):
    signal.signal ( signal.SIGALRM, alarmHandler )
    signal.alarm ( timeout )
    try:
        text = raw_input ( prompt )
        signal.alarm ( 0 )
        return text
    except AlarmException:
        print "\nSynchronize Continuing..."
    signal.signal ( signal.SIGALRM, signal.SIG_IGN )
    return "E"

def longList ( clientSocket ):
	data = clientSocket.recv ( 4096 )
	print data

def shortList ( clientSocket ):
	data = clientSocket.recv ( 4096 )
	data = data.split ( "\n" )
	for file in data:
		print file

def regex ( clientSocket ):
	data = clientSocket.recv ( 4096 )
	print data

def verify ( clientSocket ):
	data = clientSocket.recv ( 4096 )
	print data

def checkall ( clientSocket ):
	data = clientSocket.recv ( 4096 )
	print data

def tcpDownload ( clientUDPSocket, clientSocket ):
	recievingFile, address = clientUDPSocket.recvfrom ( 1024 )
	if recievingFile == "directory":
		directory, address = clientUDPSocket.recvfrom ( 1024 )
		if not os.path.exists ( directory ): 
			os.mkdir ( directory )
		permission, address = clientUDPSocket.recvfrom ( 1024 )
		os.chmod ( directory, int ( permission, 8 ) ) 
		os.chdir ( directory )
		files, address = clientUDPSocket.recvfrom ( 1024 )
		for i in range ( int ( files ) ):
			tcpDownload ( clientUDPSocket, clientSocket )
		os.chdir ( ".." )
	elif recievingFile == "file":
		filename, address = clientUDPSocket.recvfrom ( 1024 )
		permission, address = clientUDPSocket.recvfrom ( 1024 )
		if os.path.exists ( filename ):
			clientSocket.sendto ( "exists", address )
			cloudHash, address = clientUDPSocket.recvfrom ( 1024 )
			command = "md5sum " + str ( filename )
			output = os.popen ( command ).read ( )
			output = output.split ( )
			localHash = output[0]
			if not cloudHash == localHash:
				clientUDPSocket.sendto ( "continue", address )
				localFileTime = os.path.getmtime ( filename )
				cloudFileTime, address = clientUDPSocket.recvfrom ( 1024 )
				cloudFileTime = float ( cloudFileTime )
				if localFileTime > cloudFileTime:
					# upload
					clientUDPSocket.sendto ( "upload", address )
					tcpFileUpload ( clientSocket, filename )
				else:
					# download
					clientUDPSocket.sendto ( "download", address )
					tcpFileDownload ( clientSocket, filename )
			else:
				clientUDPSocket.sendto ( "stop", address )
		else:
			clientSocket.send ( "notexists" )
			tcpFileDownload ( clientSocket, filename )
		os.chmod ( filename, int ( permission, 8 ) )
	else:
		print "Requested File Not Found"

def tcpFileDownload ( clientSocket, filename ):

	with open( filename, "wb" ) as file:
	    while True:
	        data = clientSocket.recv ( 1024 )
	        if data == "Done":
	            break
	        file.write ( data )
	file.close ( )

def udpDownload ( clientUDPSocket ):
	recievingFile, address = clientUDPSocket.recvfrom ( 1024 )
	if recievingFile == "directory":
		directory, address = clientUDPSocket.recvfrom ( 1024 )
		if not os.path.exists ( directory ): 
			os.mkdir ( directory )
		permission, address = clientUDPSocket.recvfrom ( 1024 )
		os.chmod ( directory, int ( permission, 8 ) ) 
		os.chdir ( directory )
		files, address = clientUDPSocket.recvfrom ( 1024 )
		for i in range ( int ( files ) ):
			udpDownload ( clientUDPSocket )
		os.chdir ( ".." )
	elif recievingFile == "file":
		filename, address = clientUDPSocket.recvfrom ( 1024 )
		permission, address = clientUDPSocket.recvfrom ( 1024 )
		if os.path.exists ( filename ):
			clientUDPSocket.sendto ( "exists", address ) 
			cloudHash, address = clientUDPSocket.recvfrom ( 1024 )
			command = "md5sum " + str ( filename )
			output = os.popen ( command ).read ( )
			output = output.split ( )
			localHash = output[0]
			if not cloudHash == localHash:
				clientUDPSocket.sendto ( "continue", address )
				localFileTime = os.path.getmtime ( filename )
				cloudFileTime, address = clientUDPSocket.recvfrom ( 1024 )
				cloudFileTime = float ( cloudFileTime )
				if localFileTime > cloudFileTime:
					# upload
					clientUDPSocket.sendto ( "upload", address )
					udpFileUpload ( clientUDPSocket, filename, address )
				else:
					# download
					clientUDPSocket.sendto ( "download", address )
					udpFileDownload ( clientUDPSocket, filename )
			else:
				clientUDPSocket.sendto ( "stop", address )
		else:
			clientUDPSocket.sendto ( "notexists", address )
			udpFileDownload ( clientUDPSocket, filename )
		os.chmod ( filename, int ( permission, 8 ) )
	else:
		print "Requested File Not Found"

def udpFileDownload ( clientUDPSocket, filename ):
	try:
	    file = open ( filename, "wb+")
	except:
	    print "Error: File Not Found"
	    return
	
	while True:
		data, addr = clientUDPSocket.recvfrom ( 1024 )
		if data == "done":
			break
		file.write ( data )
	file.close ( )

#upload

def tcpFileUpload ( clientSocket, filename):
	try:
		file = open ( filename, "rb" )
		byte = file.read ( 1024 )
		while byte:
			clientSocket.send ( byte )
			byte = file.read ( 1024 )
		time.sleep ( 1 )
		clientSocket.send ( "Done" )
		time.sleep ( 1 )
		file.close ( )
	except:
		print "Error"

def udpFileUpload ( clientUDPSocket, filename, addr ):
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

#upload

def synchronize ( clientUDPSocket, address ):
	os.chdir ( "shared" )
	files, address = clientUDPSocket.recvfrom ( 1024 )
	for i in range ( int ( files ) ):
		udpDownload ( clientUDPSocket )
	os.chdir ( ".." )

if __name__ == "__main__":
	
	clientSocket = socket ( AF_INET, SOCK_STREAM )
	clientUDPSocket = socket ( AF_INET, SOCK_DGRAM )
	port = 6001
	udpPort = 6002
	host = gethostname ( )
	addr = ( host, udpPort )
	clientUDPSocket.bind ( ( host, udpPort ) )
	clientSocket.connect ( ( host, port ) )
	log = open ( "Client-Server.log", "a+" )
	log.write ( "-----------------------------------------------------------------------------------------\n" )
	iteration = 0
	print "***************** User Directory Client *****************"

	while True:
		iteration += 1
		choice = nonBlockingRawInput ( ">>> Enter Command Line ( Y or N ): ")
		clientSocket.send ( choice )
		if choice == "Y":
			argument = raw_input ( ">>> ")
			clientSocket.send ( argument )
			detail = str ( "User Client : |" ) + str ( iteration ) + " : |" + str ( argument ) + " . \n"
			log.write ( detail )

		elif choice == "N" or choice == "E":
			synchronize ( clientUDPSocket, addr )
			detail = str ( "User Client : |" ) + str ( iteration ) + " : |" + str ( "synchronize" ) + " . \n"
			log.write ( detail )
			continue

		else:
			message = "Error: Not a Proper input ! "
			detail = str ( "User Client : |" ) + str ( iteration ) + " : |" + str ( message ) + " . \n"
			log.write ( detail )
			print message
			continue

		if argument == "close":
			print "***************** User Directory Sync Client *****************"
			clientSocket.close ( )
			clientUDPSocket.close ( )
			log.write ( "-----------------------------------------------------------------------------------------\n" )
			log.close ( )
			break

		argument = argument.split ( )

		if argument[0] == "index":
	
			if argument[1] == "longlist":
				longList ( clientSocket )
	
			elif argument[1] == "shortlist":
				shortList ( clientSocket )

			elif argument[1] == "regex":
				regex ( clientSocket )

			else:
				print "Error: Command Not Found"
		
		elif argument[0] == "hash":

			if argument[1] == "verify":
				verify ( clientSocket )

			elif argument[1] == "checkall":
				checkall ( clientSocket )
			
			else:
				print "Error: Command Not Found"

		elif argument[0] == "download":
		
			if argument[1] == "TCP":
				os.chdir ( "shared" )
				tcpDownload ( clientUDPSocket, clientSocket )
				os.chdir ( "..")

			elif argument[1] == "UDP":
				os.chdir ( "shared" )
				udpDownload ( clientUDPSocket )
				os.chdir ( ".." )

			else:
				print "Error: Command Not Found"

		else:
			print "Error: Command Not Found"
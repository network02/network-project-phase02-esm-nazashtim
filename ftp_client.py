import socket
import os               

host ='localhost'
port= 8080
server_addr = (host , port)
format = 'utf-8'
default_pass='C:\\Users\\Taha\\Desktop\\client_dir'
file_path = ''
txt_formats = ['txt','docx']

def handle_retr(server_msg):
       global file_path

       if 'retr:FILE_NAME:' in server_msg :
            file_name = server_msg.replace('retr:FILE_NAME:','')
            file_path = os.path.join(default_pass,file_name)
            file = open(file_path,"a")
            file.close()

       elif server_msg == 'retr:B': # for non text files
            
            while not server_msg ==b'retr:EOF':
                server_msg = client.recv(1024)
                client.sendall(b'A')
                if server_msg ==b'retr:EOF':
                     break
                file = open(file_path,"ab")
                file.write(server_msg)
                file.close()
            print('\n200 successfully file transfered!')

       elif 'retr:NB':
            while not server_msg =='retr:EOF':
                server_msg = client.recv(1024).decode(format)
                client.sendall(b'A')
                if server_msg =='retr:EOF':
                     break
                file = open(file_path,"a")
                file.write(server_msg)
                file.close()
            print('\n200 successfully file transfered!')

    
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

client.connect(server_addr)

while True :
        server_msg = client.recv(1024).decode(format) 
        
        client.sendall(b'A')
       
        if 'list:' in server_msg :
            server_msg = server_msg.replace('list:','')
            print(server_msg)  

        elif 'retr:' in server_msg :
           
           handle_retr(server_msg)
        
        elif server_msg == 'fin':
            break
                    
        else:

            answer = input(server_msg)
            client.send(answer.encode(format))
     

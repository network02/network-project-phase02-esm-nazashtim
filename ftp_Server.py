import socket
import threading
import os ,shutil
import time 

admins = ["taha" , "mahdi" , "ali"]
password = ["1234" , "5678" , "9123"]
format = 'utf-8'
isAdmin = False
entercommand = "\nEnter your command :"
txt_formats = ['txt','docx']
user_file = 'C:\\Users\\Taha\\Desktop\\username.txt'
pass_file = 'C:\\Users\\Taha\\Desktop\\passwords.txt'
allowed_dir = "C:\\Users\\Taha\\Desktop\\client_dir"
current_dir = allowed_dir
username=''

def send_msg(client,msg):
    
    client.send(msg.encode(format))
    client.recv(1)

def recv_msg(client):
    
    server_msg =client.recv(1024).decode(format)
    client.send(b'A')
    return server_msg

def user_auth (msg):
    if msg in admins:
        return True
    else: 
        return False


def pass_auth (msg) :
   if msg in password :
      return True
   else :
      return False

def handle_signup(client):
    send_msg(client,'Enter Username: ')
    msg = client.recv (1024).decode('utf-8')
    file = open(user_file,'a+')
    file.seek(0)
    lines = file.read()
    if msg not in lines:
        file.write(f"{msg}\n")
        file.close()
        file = open(pass_file,'a')
        send_msg(client,'Enter Password: ')
        msg = client.recv (1024).decode('utf-8')
        file.write(f"{msg}\n")
        file.close()
        send_msg(client,'list:200 signing up successfully compeleted.')
        
    else :
        send_msg(client,'list:400 user is in use!')
        handle_signup(client)


def check_user_pass_exist(msg_user,msg_pass):

    user = open(user_file)
    password = open(pass_file)
    users = user.read()
    passwords = password.read()

    if msg_user in users:
        if msg_pass in passwords:
            send_msg(client,'list:200 Loging in successfully compeleted!')
            return True
        else:
            send_msg(client,'list:400 invalid password !')
            return False
    else :
        send_msg(client,'list:400 invalid username !')
        return False

def isAllowed_Path(path):
    global isAdmin
    
    abs_path =os.path.abspath(path)
    if not isAdmin:
        if allowed_dir in abs_path :
            return True
        else :
            False
    else :
        return True
    

def handle_l_or_s(l_or_s,client,addr):
    if l_or_s == 's':
        handle_signup(client)
        auth = authentication(client)
        return auth
    elif l_or_s == 'l':
        auth = authentication(client)
        return auth
    else:
        send_msg(client,'list:400 Invalid Command!')
        handle_client(client,addr)
        

def authentication(client ) :

    global isAdmin,username

    send_msg(client ,'Entry...\nEnter User:' ) 
    msg1 = client.recv (1024).decode('utf-8')
    msg1 = msg1.replace('user ','')
    send_msg(client ,'Enter Password:' ) 
    msg2 = client.recv (1024).decode('utf-8')
    msg2 = msg2.replace('pass ' , '')


    if user_auth(msg1): # check if is admin

        if pass_auth(msg2):
            username = msg1
            isAdmin = True   #.....
            print(f"[NEW CONNECTION] {addr} ")
            send_msg(client,"200 You are authenticated successfully!\nEnter your commands : ")
            return True
        
        else:

            send_msg(client,'list:400 invalid info')
            authentication(client)

    else: # if is not admin but has registered

        result = check_user_pass_exist(msg1,msg2)

        if result :
                username = msg1
                print(f"[NEW CONNECTION] {addr} ")
                send_msg(client,"200 You are authenticated successfully!\nEnter your commands : ")
                return True
        else:
            authentication(client)


def folder_info (client,path,*isFile) :
        
        if not isFile :
            if isAllowed_Path(path):

                file_list = os.listdir(path)

                for file_name in file_list :
                    file_path = os.path.join(path,file_name)
                    file_size = os.path.getsize(file_path)
                    ti_c = os.path.getctime(file_path)
                    file_creation_date = time.ctime(ti_c)
                    msg = f'list: {file_creation_date}  {file_size}  {file_name}\n'
                    send_msg(client,msg)
            else :
                send_msg(client,"list:400 You can`t access this directory")
        else :
            if isAllowed_Path(path):

                file = open(path)
                content = file.readlines()
                
                for line in content :
                    line='list: '+line
                    send_msg(client,line)
                    
                file.close()
            else:
                send_msg(client,"list:400 You can`t access this directory")



def handle_list(command) :
    global current_dir

    if not command =='list' :
        path = command.replace('list ','')

    if command =='list' :
        
        folder_info(client,current_dir)
        
    else :
        isFile = os.path.isfile(path)
        if not isFile :
            current_dir = path
            folder_info(client,current_dir)
        else :
           current_dir = os.path.dirname(path)
           folder_info(client,path,True)    



def handle_retr(client,command) :
    global username , current_dir
    
    path = command.replace('retr ','')
    
    if os.path.exists(path): 

        if isAllowed_Path(path):

            current_dir = os.path.dirname(path)

            username =f'retr:USERNAME:{username}'
            send_msg(client,username)
            file = open(path,'br')
            file_name = os.path.basename(path)  #retrieve file name with format
            extension =file_name.split('.')
            file_name = 'retr:FILE_NAME:' + file_name
            send_msg(client,file_name)
            file_ext = extension[1].lower()

            if not file_ext in txt_formats:
                send_msg(client,'retr:B')
            else :
                send_msg(client,'retr:NB')

            content = file.readlines()
            for line in content :
                client.sendall(line)
                client.recv(1)
            
            send_msg(client,'retr:EOF')

        else :
            send_msg(client,"400 You can`t access this file.")

    else :
        send_msg(client,'list:400 path not found!')


def handle_dele (client,command):
    global current_dir

    send_msg(client,'Do you really wish to delete? Y/N: ')
    answer = client.recv(1024).decode(format)

    if answer =='y':

        if os.path.isfile(path):
         
         if isAllowed_Path(path):

            current_dir = os.path.dirname(path)
            path = command.replace('dele ','')
         else :
            send_msg(client,'list:400 You can`t access this directory!')

            os.remove(path)
        else :
            send_msg(client,'list:400 The path is not pointing to a file!') 
    else :
        pass



def handle_mkd (client,command) :
    path = command.replace('mkd ','')

    if path:    
        if isAllowed_Path(path):
            abs_path =os.path.abspath(path)
                
            if not os.path.exists(abs_path):
                os.makedirs(abs_path)
            else :
                send_msg(client,'list:400 File already exists!')        
    else :
        send_msg(client,'list:400 Wrong Command!')


def handle_rmd(client,command):
    global current_dir

    path = command.replace('rmd ','')

    if path :
        if isAllowed_Path(path):
            abs_path =os.path.abspath(path)

            if  os.path.exists(abs_path):
                if os.path.isdir(abs_path):

                    current_dir = abs_path ####

                    listdir = os.listdir(abs_path)
                    
                    if len(listdir) == 0 :
                        os.rmdir(abs_path)
                        send_msg(client,'list:200 successfully deleted !')  

                    else :
                        shutil.rmtree(abs_path)
                        send_msg(client,'list:200 successfully deleted !')  
                else :
                    send_msg(client,'400 the path is not pointing to a directory!')
            else :
                    send_msg(client,'list:400 Cannot remove a file when that file doesn`t exists!')  
        else :
               send_msg(client,'list:400 You can`t access this directory!')  

    else :
        send_msg(client,'list:400 Wrong Command!')


def handle_stor(client,command):

    global isAdmin
    if 'stor:FILE_NAME:' in command:
        file_name = command.replace('stor:FILE_NAME:','')
        client.sendall(b'A')
        file_name = os.path.join(allowed_dir,file_name)

        server_msg = recv_msg(client)

        if 'NB' in server_msg:
             
            while not server_msg =='stor:EOF':
                server_msg = client.recv(1024).decode(format)
                client.sendall(b'A')
                if server_msg =='stor:EOF':
                     break
                file = open(file_name,"a")
                file.write(server_msg)
                file.close()
        
        elif 'B' in server_msg :
                    while  not server_msg ==b'stor:EOF':
                        server_msg = client.recv(1024)
                        client.sendall(b'A')
                        if server_msg == b'stor:EOF':
                            break
                        file = open(file_name,"ab")
                        file.write(server_msg)
                        file.close()


def handle_pwd(command):
    pass



def handle_client(client,addr):
   
   send_msg(client,"Enter login or Signup l/s: ")
   l_or_s = client.recv (1024).decode('utf-8')
   auth = handle_l_or_s(l_or_s,client,addr)

   while auth : 
      command = client.recv(1024).decode(format)

      if command == "quit" :
        send_msg(client,'fin')
        print(f"[CONNECTIO CLOSED] {addr}")
        
      elif 'list' in command :
         handle_list(command)
      elif  'retr' in command :
          handle_retr(client,command) 
      elif 'dele' in command :
          handle_dele(client,command)
      elif 'mkd' in command :
          handle_mkd(client,command)
      elif 'rmd' in command :
          handle_rmd(client,command)
      elif 'stor' in command :
          handle_stor(client,command)
      elif 'pwd' in command :
          handle_pwd(command)
      send_msg(client,entercommand)


host = 'localhost'
port = 8080
addr =(host,port)
server_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

server_socket.bind(addr)

server_socket.listen(5)

print(f"SERVER LISTENING ON {addr[1]} ...")           

while True:
    client , addr = server_socket.accept()
    thread = threading.Thread(target= handle_client , args=(client,addr ))
    thread.start()
    





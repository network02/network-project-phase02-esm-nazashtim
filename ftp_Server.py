import socket
import threading
import os ,shutil
import time 

admins = ["taha" , "mahdi" , "ali"]
password = ["1234" , "5678" , "9123"]
format = 'utf-8'
entercommand = "\nEnter your command :"
txt_formats = ['txt','docx']
user_file = 'C:\\Users\\Taha\\Desktop\\username.txt'
pass_file = 'C:\\Users\\Taha\\Desktop\\passwords.txt'
def send_msg(client,msg):
    
    client.send(msg.encode(format))
    client.recv(1)


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

def handle_signup(client,addr):
    send_msg(client,'Enter Username: ')
    msg = client.recv (1024).decode('utf-8')
    file = open(user_file,'a')
    file.write(f"{msg}\n")
    file.close()
    file = open(pass_file,'a')
    send_msg(client,'Enter Password: ')
    msg = client.recv (1024).decode('utf-8')
    file.write(f"{msg}\n")
    file.close()


def handle_login():
    pass

def handle_l_or_s(l_or_s,client,addr):
    if l_or_s == 's':
        handle_signup(client,addr)
    elif l_or_s == 'l':
        handle_login(client,addr)
    else:
        send_msg(client,'Invalid Command!')
        handle_client(client,addr)
        

def authentication(client ) :

    send_msg(client ,'Enter User:' ) 
    msg = client.recv (1024).decode('utf-8')
    msg = msg.replace('user ','')

    if msg :
       exist = user_auth(msg)

       if exist :
            send_msg(client ,'Enter Password:' ) 
            msg = client.recv (1024).decode('utf-8')
            msg = msg.replace('pass ' , '')
            pass_exist = pass_auth(msg)
            
            if pass_exist :
                print(f"[NEW CONNECTION] {addr} ")
                send_msg(client,"You are authenticated successfully! \n Enter your commands : ")
                return True
            else :
                send_msg(client,"You are not authenticated ! \n Enter Pass: ")
                authentication(client)
    
       else :
        send_msg(client,"User Not Found !\n Enter User: ")
        authentication(client)

    else:
        send_msg(client,"You are not authenticated !\n Enter User:")
        authentication(client)


def folder_info (path,*isFile) :
        
        if not isFile :
            file_list = os.listdir(path)

            for file_name in file_list :
                file_path = os.path.join(path,file_name)
                file_size = os.path.getsize(file_path)
                ti_c = os.path.getctime(file_path)
                file_creation_date = time.ctime(ti_c)
                msg=f'\nlist: {file_creation_date}  {file_size}  {file_name}'
                send_msg(client,msg)
        else :
            file = open(path)
            content = file.readlines()
            
            for line in content :
                line='list: '+line
                send_msg(client,line)
                
            file.close()


def handle_list(command) :

    if not command =='list' :
        path = command.replace('list ','')
   
    if command =='list' :
        path = "C:\\Users\\Taha\\Desktop"
        folder_info(path)
        
    else :
        isFile = os.path.isfile(path)
        if not isFile :
            folder_info(path)
        else :
            folder_info(path,True)    



def handle_retr(client,command) :
    
    path = command.replace('retr ','')

    if os.path.exists(path): #check file existance :انجام شود

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
        send_msg(client,'list:400 path not found!')


def handle_dele (client,command):
    path = command.replace('dele ','')
    send_msg(client,'Do you really wish to delete? Y/N: ')
    answer = client.recv(1024).decode(format)
    if answer =='y':
        if os.path.isfile(path):
         os.remove(path)
        else :
            send_msg(client,'list:The path is not pointing to a file!') 
    else :
        pass



def handle_mkd (client,command) :
    path = command.replace('mkd ','')

    if path :
        abs_path =os.path.abspath(path)
          
        if not os.path.exists(abs_path):
            os.makedirs(abs_path)
        else :
                send_msg(client,'list:Cannot create a file when that file already exists!')     
    else :
        send_msg(client,'list:Wrong Command!')


def handle_rmd(client,command):
    path = command.replace('rmd ','')

    if path :
        abs_path =os.path.abspath(path)
          
        if  os.path.exists(abs_path):
            if os.path.isdir(abs_path):
                listdir = os.listdir(abs_path)
                if len(listdir) == 0 :
                    os.rmdir(abs_path)
                else :
                    shutil.rmtree(abs_path)
        else :
                send_msg(client,'list:Cannot remove a file when that file doesn`t exists!')     
    else :
        send_msg(client,'list:Wrong Command!')

def handle_client(client,addr):
   
   send_msg(client,"Enter login or Signup l/s: ")
   l_or_s = client.recv (1024).decode('utf-8')
   handle_l_or_s(l_or_s,client,addr)
   auth = authentication(client)

   while auth : 
      command = client.recv(1024).decode(format)

      if command == "quit" :
        send_msg(client,'fin')
        print(f"[CONNECTIO CLOSED] {addr}")
        break
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
    





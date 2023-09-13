# https://youtu.be/GYFWuuq8dHw
# kuchma pratic 1:05:00 create web application
# kuchma pratic 1:33:00 create web application do_POST

# https://youtu.be/uiWl5DEOOnk
# kuchma 1:00 socket

#https://youtu.be/vc6eEKOUPSk
# kuchma render 4:00
# kuchma server 23:00
# kuchma request 47:00
# kuchma docker 54:00

import datetime
import pathlib
from threading import Thread
import urllib.parse # для маршрутизации
from http.server import HTTPServer, BaseHTTPRequestHandler
import mimetypes # finding type of fyles by extentions
import json
import socket #This is the Python socket module, which provides low-level network programming capabilities. It allows you to create and manage sockets for various network protocols.
import logging
from jinja2 import Environment, FileSystemLoader


BASE_DIR = pathlib.Path("front-init")
SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
BUFFER = 1024


def send_data_to_socket(body):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.sendto(body, (SERVER_IP, SERVER_PORT ))
    client_socket.close()


# hunddler processing the request:
class HTTPHandler(BaseHTTPRequestHandler):

    def do_POST(self):
        #read data:
        print (44, self.headers) # all infore with Content-Length: 42 - hedaers data length 42 bytes
        print (45, self.headers['Content-Length']) # 42 -string
        body = self.rfile.read(int(self.headers['Content-Length'])) # entered data in the contact page
        send_data_to_socket(body)

        # redirect
        self.send_response(302) #redirect
        self.send_header("Location", '/message' ) #redirect to the blog
        self.end_headers()

    def do_GET(self):# оброблюе гет запроси GET must be capital!!!
        #print(self.path) # siple path to the referencies "href" in the html document
        #print(urllib.parse.urlparse(self.path)) #parses a routs
        route = urllib.parse.urlparse(self.path)
        #print (83, route, self.path) # self.path  -route "href" from index.html during request to do_GET
        match route.path:
            case "/":
                self.send_html('front-init/index.html')
            case "/message": # вкладка contact
                self.send_html('front-init/message.html')
            case _:
                file = BASE_DIR / route.path[1:]
                if file.exists():
                    self.send_static(file)
                else:
                    self.send_html('front-init/error.html', 404)
    
    
    def send_html(self, filename, statusc_code=200):
        self.send_response(statusc_code) #return respons of get command
        self.send_header('Content-Type', 'text/html') #'Content-Type' -key of header, 'text/html' - value of the header
        self.end_headers() #end of the headr
        with open (filename, 'rb') as f:
            self.wfile.write(f.read())


    def send_static(self, filename, status_code=200):
        self.send_response(status_code)
        mime_type, *args = mimetypes.guess_type(filename) # повертає кореж на першому мшсті - mimetype
        if mime_type:
            self.send_header('Content-Type', mime_type) #'Content-Type' -key of header, 'text/html' - value of the header
        else:
            self.send_header('Content-Type', 'text/plain')
        self.end_headers() #end of the headr
        with open (filename, 'rb') as f:
            self.wfile.write(f.read())

#function to start HTTP server
def run(server=HTTPServer, handler=HTTPHandler):
    address =('0.0.0.0', 3000) #(host, port) host - IP ('' - local host / 0.0.0.0 for outside), port 0-65535
    http_server = server(address, handler)# creatrs HTTP server
    try:
        http_server.serve_forever() # starts HTTP server
    except KeyboardInterrupt: #ctrl + c
        print("KeyboardInterrupt: Ctrl + C pressed!")
        http_server.server_close #closing HTTP server


def save_data(body):
    body = urllib.parse.unquote_plus(body.decode()) # all spaces are not "+" anymore (_plus)
    try:
        print (104, body) 
        payload = {key: value for key, value in [el.split('=') for el in body.split('&')]}
        print (106, payload)
    except ValueError as err:
        logging.error(f"Filed pars data: {body} with error: {err}")
    except OSError as err: # truble with file
        logging.error(f"Filed write data: {body} with error: {err}")
    
    with open(BASE_DIR.joinpath("storage/data.json"), "r") as fd:
        file_contents = fd.read()
    if not file_contents:
        messages_dict ={}
    else:
        with open(BASE_DIR.joinpath("storage/data.json"), "r", encoding="utf-8") as fd:
                messages_dict = json.load(fd)
 
    print(121, messages_dict)

    messages_dict[str(datetime.datetime.now())]= payload
    print (124, messages_dict)
    with open(BASE_DIR.joinpath("storage/data.json"), "w", encoding = "utf-8") as fd:
        json.dump(messages_dict, fd, ensure_ascii=False)

# Sepaate server who will receive the data from page "contacts" and save it to data.json throgh 127.0.0.1:5000
def run_socket_server(ip, port):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # 
    server = ip, port
    server_socket.bind (server)
    try:
        while True:
            data, address  = server_socket.recvfrom(BUFFER)
            save_data(data)
            print (135, data)
    except KeyboardInterrupt:
        logging.info('Socket server stopped')
    finally:
        server_socket.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(threadName)s %(message)s")
    print (144, pathlib.Path())
    STORAGE_DIR = pathlib.Path().joinpath("front-init/storage")
    print(146, STORAGE_DIR)
    #D:\VSCode_projects\Python-web-hw04\front-init\storage
    STORAGE_FILE = STORAGE_DIR / 'data.json'
    print (149, STORAGE_FILE)
    if not STORAGE_FILE.exists():
        with open(STORAGE_FILE, "w", encoding = "utf-8") as fd:
            json.dump({}, fd, ensure_ascii=False) #{} - creats empty json file

    thread_server = Thread(target = run)
    thread_server.start()
    thread_socket =Thread(target=run_socket_server(SERVER_IP, SERVER_PORT))
    thread_socket.start()
    #/app/application//main.py"
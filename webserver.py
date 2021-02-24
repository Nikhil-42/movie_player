# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import pathlib

hostName = "0.0.0.0"
serverPort = 80

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        
        path = pathlib.Path('movies' + self.path)

        if path.exists() and path.is_file():    
            self.send_response(200)
            self.send_header("Content-type", "text/plaintext")
            self.end_headers()
            with open(path, 'rb') as f:
                self.wfile.write(f.read())
        else:
            print("Invalid request detected: " + self.path)

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
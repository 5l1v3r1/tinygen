# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
import http.server, os, signal, sys, atexit, socketserver

def webServer(config):
    os.chdir('generated/')
    Handler = http.server.SimpleHTTPRequestHandler
    try:
        PORT = int(config['ETC']['server-port'])
    except:
        print('Port not specified in config, defaulting to 8080')
        PORT = 8080
    try:
        ADDR = config['ETC']['server-ip']
    except:
        print('Address not specified in config, defaulting to 127.0.0.1')
        ADDR = '127.0.0.1'

    Handler = http.server.SimpleHTTPRequestHandler
    try:
        with socketserver.TCPServer((ADDR, PORT), Handler) as httpd:
            def closeServer():
                os.chdir('../')
                print('Closed server')
                httpd.server_close()
                sys.exit(0)
            def server_signal_handler(signal, frame):
                closeServer()
            signal.signal(signal.SIGINT, server_signal_handler)
            print('''

NOTICE: This server is meant primarily for site testing purposes.
For increased security, speed, and for advanced features such as https, consider using a full web server like Caddy, Nginx, or Apache

''')
            print('Serving at port', PORT, 'on', ADDR)
            atexit.register(closeServer)
            httpd.serve_forever()
    except OSError:
        return 'port already taken'

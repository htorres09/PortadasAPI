"""
This script runs the APIPortadas application using a development server.
"""

from os import environ
from APIPortadas import app, hostData

if __name__ == '__main__':
    #HOST = environ.get('SERVER_HOST', 'localhost')
    HOST = environ.get('SERVER_HOST', hostData['HOST'])
    try:
        #PORT = int(environ.get('SERVER_PORT', '5555'))
        PORT = int(environ.get('SERVER_PORT', hostData['PORT']))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)

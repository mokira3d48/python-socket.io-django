"""
WSGI config for django_socketio project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os
import socketio

from django.core.wsgi import get_wsgi_application
from socketio_app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_socketio.settings');

django_app  = get_wsgi_application();
application = socketio.WSGIApp(sio, django_app);

####################################################################################

from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler

server = pywsgi.WSGIServer(("", 8000), application, handler_class=WebSocketHandler);
server.serve_forever();


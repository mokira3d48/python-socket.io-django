# python-socket.io-django
Python socket.io example with Django framework

<br/>

## Installation des modules
Voici tous les modules dont on a besoin pour monter notre serveur socket.

Contenu du fichier `requirements.txt` :
```
asgiref==3.4.1
bidict==0.21.2
Django==3.2.6
dnspython==1.16.0
enum-compat==0.0.3
eventlet==0.30.0
gevent==21.1.2
gevent-websocket==0.10.1
greenlet==0.4.17
python-engineio==4.2.1
python-socketio==5.4.0
pytz==2021.1
six==1.10.0
sqlparse==0.4.1
zope.event==4.5.0
zope.interface==5.4.0

```
Utiliser la commande suivante pour installer tous les modules contenus dans le fichier.
Vous pouvez aussi les installer un a un afin d'avoir leur dernière version.

```
pip install -r requirements.txt
```

<br/>
<br/>

## Creation d'un projet Django
On va maintenant créer un projet Django nommé `django_socketio` par exemple.

```
django-admin startproject django_socketio
```

Il faut créer ensuite une application. C'est dans cette dernière qu'on va mettre en place
la configuration du serveur de `socket.io`.

```
django-admin startapp socketio_app
```

<br/>
<br/>

## Configuration du projet
On va placer les boûts de code qu'il faut dans certains fichiers de django.

<br/>

### Configuration de l'URL
1. Dans le fichier `django_socketio/settings.py`, insérer la ligne suivante :

```python
# ...

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1'];

# ...
```

C'est pour permettre l'accès de tous les ordinateurs connectés sur le même réseau
que vous (`0.0.0.0`) et l'accès en localhost (`127.0.0.1`) au serveur de l'application.

<br/>

2. Dans le fichier `django_socketio/urls.py`, insérer la ligne suivante :

```python
from django.conf.urls import url, include

# ...
```

ensuite,

```python
# ...

urlpatterns = [
    url(r'', include('socketio_app.urls')),
    path('admin/', admin.site.urls),
]
```

<br/>

3. Dans le dossier `django_socketio/socketio_app/`, créez le fichier `urls.py` et insérer s'y
le code suivant :

```python
from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'', views.index, name='index'),
];

```

<br/>

### Configuration du serveur en socket.io
On va maintenant mettre en place les fonctionnalités du serveur de socket.io.

1. Dans le fichier `django_socketio/socketio_app/views.py` insérer les lignes de code suivantes :

```python
import socketio

# mode d'asynchronisation
async_mode = 'gevent';

# definition du serveur de socket.io
sio = socketio.Server(async_mode=async_mode);


```

<br/>

![Stratégie de déploiement](https://www.botreetechnologies.com/blog/wp-content/uploads/2020/12/deployment-strategy.jpg, "Stratégie de déploiement")

- Le déploiement est délicat, car les sockets ne sont pas basés sur le protocole HTTP. Le serveur d'applications alloue généralement un processus ou un fil distinct pour chaque demande. Par conséquent, nous devons utiliser `Gevent`, qui agit comme une boucle d'événements et chaque fois qu'il y a une demande de connexion, il génère un nouveau thread et attribue la connexion à ce thread.

- Nous avons décidé de séparer l'application socket de l'application normale, car la prise en charge à la fois de la fonction Django normale et de l'application socket dans une seule `application Django` rendait la gestion des réponses aux requêtes lente.

- Le déplacement du code socketio vers une autre application a également facilité la maintenance du code.

Par [ici](https://www.botreetechnologies.com/blog/django-websocket-with-socketio/) pour en savoir plus.

<br/>

2. Dans le dossier `django_socketio/socketio_app/`, créez le dossier `management`, dans ce dernier, créez le dossier `commands`, ensuite, dans le dossier `commands`, créer le fichier `runserver.py`. Dans ce dernier, insérez les lignes de codes suivantes :

```python
from django.core.management.commands.runserver import Command as RunCommand

from socketio_app.views import sio


class Command(RunCommand):
    help = 'Run the Socket.IO server'

    def handle(self, *args, **options):
        if sio.async_mode == 'threading':
            super(Command, self).handle(*args, **options)
        
        elif sio.async_mode == 'eventlet':
            # deploy with eventlet
            import eventlet
            import eventlet.wsgi
            from django_socketio.wsgi import application

            eventlet.wsgi.server(eventlet.listen(('', 8000)), application);
        
        elif sio.async_mode == 'gevent':
            # deploy with gevent
            from gevent import pywsgi
            from django_socketio.wsgi import application
            
            try:
                from geventwebsocket.handler import WebSocketHandler

                websocket = True;
                print('Gevent config is done !\n');

            except ImportError:
                websocket = False;
            
            if websocket:
                pywsgi.WSGIServer(('', 8000), application, handler_class=WebSocketHandler).serve_forever()

            else:
                pywsgi.WSGIServer(('', 8000), application).serve_forever();

        elif sio.async_mode == 'gevent_uwsgi':
            print('Start the application through the uwsgi server. Example:');
            print('uwsgi --http :5000 --gevent 1000 --http-websockets '
                  '--master --wsgi-file django_example/wsgi.py --callable '
                  'application');

        else:
            print('Unknown async_mode: ' + sio.async_mode)


```

<br/>

3. Remplacez les lignes de code du fichier `django_socketio/wsgi.py` par les suivantes :

```python
import os
import socketio

from django.core.wsgi import get_wsgi_application
from socketio_app.views import sio

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_socketio.settings');

django_app = get_wsgi_application();
application = socketio.WSGIApp(sio, django_app);

```

<br/>
<br/>


# python-socket.io-django
Python socket.io example with Django framework

- French version is [here](https://github.com/mokira3d48/python-socket.io-django/tree/master/fr)

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


2. Remplacez les lignes de code du fichier `django_socketio/wsgi.py` par les suivantes :

```python
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

```

<br/>
<br/>

### Implémentation des exemples de fonctionnalités avec socket.io
On va juste essayer d'implémenter un programme de chat. Remplacez donc tous le code contenu dans le fichier `django_socketio/socketio_app/views.py` par les lignes de code suivantes :

```python
# définissez async_mode sur 'threading', 'eventlet', 'gevent' ou 'gevent_uwsgi' sur
# forcer un autre mode, le meilleur mode est sélectionné automatiquement parmi ce qui est
# installée
async_mode = 'gevent';

import os

from django.http import HttpResponse
import socketio

basedir = os.path.dirname(os.path.realpath(__file__));
sio     = socketio.Server(async_mode=async_mode);

# thread = None
users = {};

def index(request):
    """ 
        Programme qui permet de renvoiyer la page web `index`
    """

    # global thread;

#    if thread is None:
#        thread = sio.start_background_task(background_thread);

    # on renvois une page WEB
    return HttpResponse(open(os.path.join(basedir, 'static/index.html')));


# def background_thread():
#     """ Exemple de programme d'execution de programme d'arriere plan """

#     count = 0;

#     while True:
#         sio.sleep(10);
#         count += 1;
#         sio.emit('my_response', {'data': 'Server generated event'}, namespace='/test');

@sio.event
def set_username(sid, message):
    """ Programme de modification du nom d'utilisateur """
    users[sid] = message['data'];

    # on notifit que le username a ete correctement notifie
    sio.emit('my_response', {'data': f"Username is set to {users[sid]} !"}, to=sid);



@sio.event
def my_event(sid, message):
    # Programme qui permet d'envoyer le message a moi meme
    sio.emit('my_response', {'data': message['data']}, room=sid);



@sio.event
def my_broadcast_event(sid, message):
    # Programme qui permet d'envoyer le message a tous le monde
    sio.emit('my_response', {'data': f"[{users[sid]}] {message['data']}"});



@sio.event
def join(sid, message):
    """ Programme de creation et d'adesion de canale """

    # on cree le canale et on se join a ce canal
    sio.enter_room(sid, message['room']);

    # sio.emit('my_response', {'data': 'Entered room: ' + message['room']}, room=sid);

    # on emet a tous ceux qui sont dans le canal qu'on de 
    # rejoindre le canal
    sio.emit('my_response', {'data': 'Entered room: ' + message['room']}, to=message['room']);


@sio.event
def leave(sid, message):
    """ Programme de deconnection d'un canal """

    # on se deconnecte du canal
    sio.leave_room(sid, message['room']);
    sio.emit('my_response', {'data': users[sid] + ' left room: ' + message['room']}, room=sid);


@sio.event
def close_room(sid, message):
    """ Programme de fermeture d'un canal """

    # on ferme le canal
    sio.close_room(message['room']);
    sio.emit('my_response', {'data': 'Room ' + message['room'] + ' is closing.'}, room=message['room']);


@sio.event
def my_room_event(sid, message):
    """ Programme qui permet d'envoyer un message a tous les membres du canal """
    sio.emit('my_response', {'data': f"[{users[sid]}] {message['data']}"}, room=message['room']);


@sio.event
def disconnect_request(sid):
    """ Programme qui declanche la deconnection de l'utilisateur """
    sio.disconnect(sid);


@sio.event
def connect(sid, environ):
    """ Programme de connexion 
        Au cour de la connexion, on enregistre tous les utilisateurs 
        connectes
    """

    print(f"{sid}\t connected");

    # on ajoute le nouveau a la liste
    users[sid] = None;

    # on lui notifie qu'il s'est bien connecte
    sio.emit('my_response', {'data': 'Connected', 'count': len(users)}, room=sid);


@sio.event
def disconnect(sid):
    """ Programme de deconnexion
        Lors de la deconnexion, on supprime l'utilisateur de la liste des
        connectes
    """

    print(f"{sid}\t {users[sid]} disconnected");

    # on le supprime de la liste 
    del users[sid];


```

<br/>
<br/>

### Mise en place d'une interface WEB
Dans le dossier `django_socketio/socketio_app/`, créez un dossier nommé `static`, ensuite, dans ce dernier, créer un fichier nommé `index.html`. Dans ce fichier, insérez les lignes de code suivantes :

```html
<!DOCTYPE HTML>
<html>
    <head>
        <title>Django + SocketIO Test</title>
        <script type="text/javascript" src="//code.jquery.com/jquery-3.2.1.slim.min.js"></script>
        <script type="text/javascript" src="//cdnjs.cloudflare.com/ajax/libs/socket.io/3.0.3/socket.io.min.js"></script>
        <script type="text/javascript" charset="utf-8">
            $(document).ready(function(){
                var socket = io.connect();

                socket.on('connect', function() {
                    socket.emit('my_event', {data: 'I\'m connected!'});
                });
                socket.on('disconnect', function() {
                    $('#log').append('<br>Disconnected');
                });
                socket.on('my_response', function(msg) {
                    $('#log').append('<br>Received: ' + msg.data);
                });

                // event handler for server sent data
                // the data is displayed in the "Received" section of the page
                // handlers for the different forms in the page
                // these send data to the server in a variety of ways
                $('form#username').submit(function(event) {
                    socket.emit('set_username', {data: $('#name_data').val()});
                    return false;
                });
                $('form#emit').submit(function(event) {
                    socket.emit('my_event', {data: $('#emit_data').val()});
                    return false;
                });
                $('form#broadcast').submit(function(event) {
                    socket.emit('my_broadcast_event', {data: $('#broadcast_data').val()});
                    return false;
                });
                $('form#join').submit(function(event) {
                    socket.emit('join', {room: $('#join_room').val()});
                    return false;
                });
                $('form#leave').submit(function(event) {
                    socket.emit('leave', {room: $('#leave_room').val()});
                    return false;
                });
                $('form#send_room').submit(function(event) {
                    socket.emit('my_room_event', {room: $('#room_name').val(), data: $('#room_data').val()});
                    return false;
                });
                $('form#close').submit(function(event) {
                    socket.emit('close_room', {room: $('#close_room').val()});
                    return false;
                });
                $('form#disconnect').submit(function(event) {
                    socket.emit('disconnect_request');
                    return false;
                });
            });
        </script>
    </head>
    <body>
        <h1>Django + SocketIO Test</h1>
        <h2>Send:</h2>
        <form id="username" method="POST" action='#'>
            <input type="text" name="username" id="name_data" placeholder="Username">
            <input type="submit" value="Set name">
        </form>
        <form id="emit" method="POST" action='#'>
            <input type="text" name="emit_data" id="emit_data" placeholder="Message">
            <input type="submit" value="Echo">
        </form>
        <form id="broadcast" method="POST" action='#'>
            <input type="text" name="broadcast_data" id="broadcast_data" placeholder="Message">
            <input type="submit" value="Broadcast">
        </form>
        <form id="join" method="POST" action='#'>
            <input type="text" name="join_room" id="join_room" placeholder="Room Name">
            <input type="submit" value="Join Room">
        </form>
        <form id="leave" method="POST" action='#'>
            <input type="text" name="leave_room" id="leave_room" placeholder="Room Name">
            <input type="submit" value="Leave Room">
        </form>
        <form id="send_room" method="POST" action='#'>
            <input type="text" name="room_name" id="room_name" placeholder="Room Name">
            <input type="text" name="room_data" id="room_data" placeholder="Message">
            <input type="submit" value="Send to Room">
        </form>
        <form id="close" method="POST" action="#">
            <input type="text" name="close_room" id="close_room" placeholder="Room Name">
            <input type="submit" value="Close Room">
        </form>
        <form id="disconnect" method="POST" action="#">
            <input type="submit" value="Disconnect">
        </form>
        <h2>Receive:</h2>
        <div><p id="log"></p></div>
    </body>
</html>

```

<br/>
<br/>

## Démarrage du serveur
N'oublier pas de sauvegarder tous les fichiers sources. Il est temps de tester notre programme.
On doit d'abord faire un migration dans une base de données avant de démarrer le serveur.
Pour faire la migration, tappez la commande suivante :

```
./manage.py migrate
```

On peut maintenant démarrer le serveur avec la commande suivante :

```
./manage.py runserver
```

Si tout va bien, vous verrez le message suivant affichez dans votre terminal.

```
async_mode is set to `Gevent` !
```

<br/>
<br/>

## Test
Voici le lien pour accéder à l'interface web : [http://127.0.0.1:8000/](http://127.0.0.1:8000/).
Pour que d'autre ordinateur puisse accéder à votre application, il faut qu'ils soient dans le même réseau que votre ordinateur. Ensuite, ils doivent utiliser votre adresse IP (souvent sous la forme `192.168.xxx.xxx`). Pour qu'on connaitre votre adresse IP :

- sous linux :

```
sudo ifconfig
```

- sous windows :

```
ipconfig
```



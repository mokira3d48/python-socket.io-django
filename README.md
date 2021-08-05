# python-socket.io-django
Python socket.io example with Django framework

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

## Configuration du projet
On va placer les boûts de code qu'il faut dans certains fichiers de django.

### Configuration de l'URL
- Dans le fichier `django_socketio/settings.py`, insérer la ligne suivante :

```python
# ...

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1'];

# ...
```

C'est pour permettre l'accès de tous les ordinateurs connectés sur le même réseau
que vous (`0.0.0.0`) et l'accès en localhost (`127.0.0.1`) au serveur de l'application.

- Dans le fichier `django_socketio/urls.py`, insérer la ligne suivante :

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





# set async_mode to 'threading', 'eventlet', 'gevent' or 'gevent_uwsgi' to
# force a mode else, the best mode is selected automatically from what's
# installed
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



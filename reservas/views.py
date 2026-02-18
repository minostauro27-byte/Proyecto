from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseForbidden
from firebase_admin import firestore, auth
from proyecto_grupo.firebase_connection import initialize_firebase
from functools import wraps
import requests
import os


db = initialize_firebase()

def registro_usuario(request):
    mensaje = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:

            user = auth.create_user(
                email = email,
                password = password
            )

            db.collection('perfiles').document(user.uid).set({
                'email' : email,
                'uid' : user.uid,
                'fecha_registro' : firestore.SERVER_TIMESTAMP,
            })

            mensaje = f"Usuario registrado correctamente con UID: {user.uid}"

        except Exception as e:
            mensaje = f"Error: {e}"

    return render(request, 'reservas/registro.html', {'mensaje': mensaje})


def iniciar_sesion(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        api_key = os.getenv('FIREBASE_WEB_API_KEY')

        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"

        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }

        response = requests.post(url, json=payload)
        data = response.json()

        if response.status_code == 200:
            request.session['uid'] = data['localId']
            request.session['email'] = data['email']
            return redirect('dashboard')
        else:
            messages.error(request, "Credenciales incorrectas")

    return render(request, 'reservas/login.html')



def login_required_firebase(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if 'uid' not in request.session:
            return redirect('login')
        return view_func(request, *args, **kwargs)
    return _wrapped


@login_required_firebase
def dashboard(request):
    return render(request, 'reservas/dashboard.html')


@login_required_firebase
def crear_reserva(request):
    if request.method == 'POST':
        habitacion = request.POST.get('habitacion')
        fecha_entrada = request.POST.get('fecha_entrada')
        fecha_salida = request.POST.get('fecha_salida')
        uid = request.session.get('uid')

        try:
            db.collection('reservas').add({
                'cliente_id': uid,
                'habitacion': habitacion,
                'fecha_entrada': fecha_entrada,
                'fecha_salida': fecha_salida,
                'estado': 'Activa',
                'fecha_creacion': firestore.SERVER_TIMESTAMP
            })

            messages.success(request, " Reserva creada correctamente")
            return redirect('mis_reservas')

        except Exception as e:
            messages.error(request, f"Error: {e}")

    return render(request, 'reservas/crear.html')


@login_required_firebase
def mis_reservas(request):
    uid = request.session.get('uid')
    reservas = []

    docs = db.collection('reservas').where('cliente_id', '==', uid).stream()

    for doc in docs:
        reserva = doc.to_dict()
        reserva['id'] = doc.id
        reservas.append(reserva)

    return render(request, 'reservas/listar.html', {'reservas': reservas})



@login_required_firebase
def cancelar_reserva(request, reserva_id):
    db.collection('reservas').document(reserva_id).update({
        'estado': 'Cancelada'
    })

    messages.info(request, " Reserva cancelada")
    return redirect('mis_reservas')


@login_required_firebase
def cerrar_sesion(request):
    request.session.flush() 
    return redirect('login')

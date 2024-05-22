from django.shortcuts import render, redirect
from django.contrib.auth import authenticate 
from django.contrib import auth

# Create your views here.

def inicio (request):
    mensaje ="debe iniciar sesión"
    return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})




def inicioAdministrador (request):
    if request.user.is_authenticate:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "administrador/inicio.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})
    


def inicioEmpleado (request):
    if request.user.is_authenticate:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "empleado/inicio.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})
    



def inicioTecnico (request):
    if request.user.is_authenticate:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "tecnico/inicio.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})






def login(request):
    username=request.POST['txtUser']
    password=request.POST['txtPassword']
    user= authenticate(username=username, password=password)
    if user is not None:
        # registrar la variable de sesión
        auth.login(request, user)
        if user.groups.filter(name="Administrador").exists():
            return redirect('/inicioAdministrador')
        elif user.groups.filter(name='Tecnico').exists():
            return redirect('/inicioTecnico')
        else:
            return redirect('/inicioEmpleado')
        
    else:
        mensaje = "usuario o contraseña incorrecto"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})
    


def salir(request):
    mensaje ="ha cerrado sesión"
    return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})

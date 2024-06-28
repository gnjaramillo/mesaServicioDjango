from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth import authenticate 
from django.contrib import auth
from appMesaServicio.models import  *
from random import *
from django.db import Error, transaction
from datetime import datetime
# para correo
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import threading
from smtplib import SMTPException
from django.http import JsonResponse

def inicio (request):
    mensaje ="debe iniciar sesión"
    return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})


def inicioAdministrador (request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "administrador/inicioAdm.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})
    


def inicioEmpleado (request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "empleado/inicioEmp.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})
    



def inicioTecnico (request):
    if request.user.is_authenticated:
        datosSesion = {"user": request.user, "rol":request.user.groups.get().name}
        return render (request, "tecnico/inicioTec.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})



@csrf_exempt
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





def vistaSolicitud(request):
    if request.user.is_authenticated:
        oficinaAmbientes = OficinaAmbiente.objectos.all()
        datosSesion = {"user": request.user, 
                       "rol":request.user.groups.get().name,
                       "oficinaAmbientes": oficinaAmbientes}
        return render(request, "empleado/solicitud.html", datosSesion)
    else:
        mensaje ="debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})


    


def registrarSolicitud(request):
 if request.user.is_authenticated:   
    try:
        with transaction.atomic():
            user = request.User
            descripcion = request.POST['txtDescripcion']
            idOficinaAmbiente = int(request.POST['cbOficinaAmbiente'])
            oficinaAmbiente = OficinaAmbiente.objects.get(pk=idOficinaAmbiente)
            solicitud = Solicitud(solUsuario = User, 
                                solDescripcion = descripcion, 
                                solOficinaAmbiente = oficinaAmbiente )
            solicitud.save()
            # Obtener año para en el consecutivo agregar por el año
            fecha = datetime.now()
            year = fecha.year
            #obtener el numero de solicitudes hechas pro año actual
            consecutivoCaso = Solicitud.objects.filter(fechaHoraCreacion__year = year).count()
            # ajustar en consecutivo caso con ceros a la izq
            consecutivoCaso = str(consecutivoCaso).rjust(5,'0')
            # crear el codigo del caso
            codigoCaso =f"REQ-{year}-{consecutivoCaso}"
            # consultar el usuario tipo admin para asignarlo al caso y que posteriormente el asigne el caso a un tecnico
            userCaso = User.objects.filter(groups__name__in=['Administrador']).first()
            # crear el caso
            estado = "Solicitada"
            caso = Caso(casSolicitud = solicitud,
                        casCodigo = codigoCaso,
                        casUsuario = userCaso,
                        casEstado = estado
            )
            caso.save()
            mensaje = "se ha registrado su solicitud de manera exitosa"
            # enviar correo de registro de solicitud
            asunto ='Registro Solicitud -Mesa de servicio'
            mensajeCorreo = f'Cordial saludo, <b>{user.first_name} {user.last_name}</b>, nos permitimos \
                informarle que su solicitud fue registrada en nuestro sistema con el número de caso \
                <b>{codigoCaso}</b>. <br><br> Su caso será gestionado en el menor tiempo posible, \
                según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                <br><br>Lo invitamos a ingresar a nuestro sistema en la siguiente url:\
                http://mesadeservicioctpicauca.sena.edu.co.'
             # crear el hilo para el envío del correo
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeCorreo, [user.email]))
            # ejecutar el hilo
            thread.start()
            mensaje = "Se ha registrado su solicitud de manera exitosa"
    # Enviar el correo al empleado
    except Error as error:
        transaction.rollback()
        mensaje = f"{error}"


    oficinaAmbiente=OficinaAmbiente.objects.all()
    retorno = {"mensaje": mensaje, "oficinasAmbientes": oficinaAmbiente}
    return render(request, "empleado/solicitud.html", retorno)
 else:
    mensaje ="debe iniciar sesión"
    return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})
  



def enviarCorreo(asunto=None, mensaje=None, destinatario=None,archivo=None):
    remitente = settings.EMAIL_HOST_USER
    template = get_template('enviarCorreo.html')
    contenido = template.render({
        'mensaje':mensaje,
    })
    try:
        correo = EmailMultiAlternatives(
            asunto, mensaje, remitente, destinatario
        )
        correo.attach_alternative(contenido,'text/html')
        if archivo != None :
            correo.attach_file(archivo)
        correo.send(fail_silently=True)
    except SMTPException as error:
        print (error)

    
def listarCasosParaAsignar(request):
    if request.user.is_authenticated:  
        try:
            mensaje=""
            fecha = datetime.now()
            year = fecha.year
            listaCasos = Caso.objects.filter(
                casSolicitud__fechaHoraCreacion__year=year, casEstado='Solicitada')
            tecnicos = User.objects.filter(groups__name__in=['Tecnico'])
        except Error as error :
            mensaje=str(error)
    
        retorno = {"listaCasos":listaCasos, "tecnicos":tecnicos, "mensaje":mensaje}
        return render (request, "administrador/listarCasosParaAsignar.html", retorno)
    else:
        mensaje ="debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})

        

def asignarTecnicoCaso (request):
    if request.user.is_authenticated:
        try:
            idTecnico = int(request.POST['cbTecnico'])
            userTecnico = User.objects.get(pk=idTecnico)
            idCaso = int(request.POST['idCaso'])
            caso = Caso.objects.get(pk=idCaso)

            ######### PREGUNTARRRRRRRRRRRRRRRRRRRRRRRRRRRRR
            caso.casUsuario=userTecnico
            caso.casEstado="En Proceso"
            caso.save()
            # Enviar Correo al tecnico
            asunto = 'Asignacion Caso - Mesa de Servicio'
            mensajeCorreo = f'Cordial saludo, <b>{userTecnico.first_name} {userTecnico.last_name}</b>, nos permitimos \
                informarle que se le ha asignado un caso para dar solucion. Codigo de Caso: \
                <b>{caso.casCodigo}</b>.Se solicita se atienda de manera oportuna \
                según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                <br><br>Lo invitamos a ingresar al sistema para gestionar sus casos asignados:\
                http://mesadeservicioctpicauca.sena.edu.co.'
            # crear el hilo para el envío del correo
            thread = threading.Thread(
                target=enviarCorreo, args=(asunto, mensajeCorreo, [userTecnico.email]))
            # ejecutar el hilo
            thread.start()
            mensaje = "Caso asignado"

            #### VERIFICARRRRRR
            return redirect('listarCasosParaAsignar/', {"mensaje":mensaje})
            
        except Error as error:
            mensaje=str(error)
    else:
        mensaje="Debes iniciar sesion"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})


def listarEmpleadosTecnicos(request):
    if request.user.is_authenticated:  
        try:
            mensaje =""
            tecnicos = User.objects.filter(groups_name_in=['Tecnico'])
        except Error as error:
         mensaje=str(error)
        retorno = {"tecnicos":tecnicos, "mensaje":mensaje}
        return JsonResponse(retorno)
    else:
        mensaje ="debe iniciar sesión"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})






    
def listarCasosAsignadosTecnico(request):
    if request.user.is_authenticated:
        try:
            listaCasos = Caso.objects.filter(casEstado='En proceso', casUsuario=request.user)
            listaTipoProcedimiento = TipoProcedimiento.objects.all().values()
            mensaje='listado de casos asignados'
        except Error as error :
            mensaje=str(error)
    
        retorno = {"listaCasos":listaCasos,  "mensaje":mensaje, 
                   "listaTipoProcedimiento":listaTipoProcedimiento,
                   "listaTipoSolucion":tipoSolucion}
        
        return render (request, "tecnico/listarCasosAsignados.html", retorno)
    else:
        mensaje="Debes iniciar sesion"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})
    


def solucionarCaso(request):

    if request.user.is_authenticated:
            try:
                if transaction.atomic():
                    procedimiento = request.POST["txtProcedimiento"]
                    tipoProc = int(request.POST['cbTipoProcedimiento'])
                    tipoProcedimiento =  TipoProcedimiento.objects.get(pk=tipoProc)
                    tipoSolucion = request.POST['cbTipoSolucion']
                    idCaso = int(request.POST['idCaso'])
                    caso = Caso.objects.get(pk=idCaso)
                    solucionCaso = SolucionCaso(solCaso = caso,
                                                solProcedimiento=procedimiento,
                                                solTipoSolucion=tipoSolucion)
                    solucionCaso.save()

                    #actualizar estado caso dependiendo del tipo de solucion

                    if (tipoSolucion == "Definitiva"):
                        caso.casEstado = "Finalizada"
                        caso.save()

                    #crear el objeto solucion tipo procedimiento

                    solucionCasotipoProcedimiento = SolucionCasotipoProcedimiento(
                        solSolucionCaso = solucionCaso,
                        solTipoProcedimiento = tipoProcedimiento
                    )

                    solucionCasotipoProcedimiento.save()
                    #enviar correo a empleado que realizo la solicitud
                    solicitud = caso.casSolicitud
                    userEmpleado= solicitud.solUsuario
                    asunto = 'Solución Caso - Mesa de Servicio CTPI-CAUCA'
                    userEmpleado = Caso.objects.filter('casSolicitud_solUsuario').first()

                    mensajeCorreo = f'Cordial saludo, <b>{userEmpleado.first_name} {userEmpleado.last_name}</b>, nos permitimos \
                        informarle que se le ha brindado una solucion de tipo {tipoSolucion}. al Caso identificado con el código: \
                        <b>{caso.casCodigo}</b>.Lo invitamos a revisar su equipo para verificar la respectiva solución, \
                        cualquier inquietud al respecto, nos puede informar de manera opurtuna por este medio,\
                        según los acuerdos de solución establecidos para la Mesa de Servicios del CTPI-CAUCA.\
                        <br><br>Lo invitamos a ingresar al sistema para consultar el detalle de la solución de su respectiva \
                        solicitud registrada en la siguiente url:\
                        http://mesadeservicioctpicauca.sena.edu.co.'
                    #crear el hilo para el envío del correo
                    thread = threading.Thread(
                        target=enviarCorreo, args=(asunto, mensajeCorreo, [userEmpleado.email]))
                    #ejecutar el hilo
                    thread.start()
                    mensaje = "solución caso"
            except Error as error:
                transaction.rollback()
                mensaje = str(error)
            retorno = {"mensaje" : mensaje}
            return redirect("/listarCasosAsignadosTecnico/")
    else:
        mensaje="Debes iniciar sesion"
        return render(request, "frmIniciarSesion.html", {"mensaje":mensaje})




def salir(request):
    auth.logout(request)
    mensaje ="ha cerrado sesión"
    return render (request, "frmIniciarSesion.html", {"mensaje": mensaje})

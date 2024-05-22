from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

tipoOficinaAmbiente=[
    ('Administrativo','Administrativo'),
    ('Formación','Formación'),
]

class OficinaAmbiente(models.Model):
    ofiTipo = models.CharField(max_length=15, choices=tipoOficinaAmbiente,
                               db_comment="tipo de oficina")
    ofiNombre = models.CharField(max_length=50, unique=True,
                               db_comment="nombre de oficina o ambiente")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                               db_comment="fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización")
    
    def _str_(self) -> str:
        return self.ofiNombre
    

tipoUsuario=[
    ('Administrativo','Administrativo'),
    ('Instructor','Instructor'),
]


class User(AbstractUser):
    userTipo = models.CharField(max_length=15, choices=tipoUsuario,
                               db_comment="tipo de oficina")
    userFoto = models.ImageField(upload_to=f"fotos/", null=True, blank=True,
                               db_comment="foto usuario")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                               db_comment="fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización")


    def __str__(self) -> str:
        return self.username
    


class Solicitud(models.Model):
    solUsuario = models.ForeignKey(User,on_delete=models.PROTECT,
                               db_comment="hace ref al empleado que hace la solicitud")
    solDescripcion = models.TextField(max_length=1000,
                               db_comment="descripción solicitud del empleado")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                               db_comment="fecha y hora del registro de solicitud")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")
    solOficinaAmbiente = models.ForeignKey(OficinaAmbiente, on_delete=models.PROTECT,
                               db_comment="hace ref a la oficina o ambiente donde se requiere la solicitud")


    def _str_(self) -> str:
        return self.solDescripcion
    

estadoCaso = [('Solicitada', 'Solicitada'),
              ('En proceso', 'En proceso'),
              ('Finalizada', 'Finalizada'),           
]

class Caso(models.Model):
    casSolicitud = models.ForeignKey(Solicitud,on_delete=models.PROTECT,
                               db_comment="hace ref a la solicitud que genero el caso")
    casCodigo = models.CharField(max_length=10, unique=True,
                               db_comment="codigo unico del caso")
    casUsuario = models.ForeignKey(User,on_delete=models.PROTECT,
                               db_comment="Empleado de soporte técnico asignado al caso")
    casEstado = models.CharField(max_length=20, choices=estadoCaso )

    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")




class TipoProcedimiento(models.Model):
    tipNombre = models.CharField(max_length=30, unique=True,
                               db_comment="tipo de procedimiento")
    tipDescripcion = models.TextField(max_length=1000,
                               db_comment="texto con la descripcion del procedimiento")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")
    



[('hardware', 'hardware'),
        ('software', 'software'),
        ('conexion red', 'conexion red'),
]



class solucionCaso(models.Model):
    solCaso = models.ForeignKey(Caso, on_delete=models.PROTECT,
                               db_comment="hace ref a la solicitud que genero el caso")   





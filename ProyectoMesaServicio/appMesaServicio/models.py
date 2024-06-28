from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

tipoOficinaAmbiente=[
    ('Administrativo','Administrativo'),
    ('Formación','Formación'),
]

tipoUsuario=[
    ('Administrativo','Administrativo'),
    ('Instructor','Instructor'),
]

estadoCaso = [('Solicitada', 'Solicitada'),
              ('En proceso', 'En proceso'),
              ('Finalizada', 'Finalizada'),           
]

tipoSolucion = [('Parcial', 'Parcial'),
                ('Definitiva', 'Definitiva')
]

tipoProcedimiento = [('hardware', 'hardware'),
                ('software', 'software'),
                ('red', 'red'),
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
    solOficinaAmbiente = models.ForeignKey(OficinaAmbiente, on_delete=models.PROTECT,
                               db_comment="hace ref a la oficina o ambiente donde se requiere la solicitud")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                               db_comment="fecha y hora del registro de solicitud")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")


    def _str_(self) -> str:
        return self.solDescripcion
    


class Caso(models.Model):
    casSolicitud = models.ForeignKey(Solicitud,on_delete=models.PROTECT,
                               db_comment="hace ref a la solicitud que genero el caso")
    casCodigo = models.CharField(max_length=10, unique=True,
                               db_comment="codigo unico del caso")
    casUsuario = models.ForeignKey(User,on_delete=models.PROTECT,
                               db_comment="Empleado de soporte técnico asignado al caso")
    casEstado = models.CharField(max_length=20, choices=estadoCaso, default='Solicitada' )

    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")

    def _str_(self) -> str:
        return self.casCodigo
    


class TipoProcedimiento(models.Model):
    tipNombre = models.CharField(max_length=30, unique=True,
                               db_comment="tipo de procedimiento")
    tipDescripcion = models.TextField(max_length=1000,
                               db_comment="texto con la descripcion del procedimiento")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                                             db_comment="Fecha y hora del registro")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                               db_comment="fecha y hora de ultima actualización de la solicitud")
    
    def __str__(self) -> str:
            return self.tipNombre





class SolucionCaso(models.Model):
    solCaso = models.ForeignKey(Caso, on_delete=models.PROTECT,
                               db_comment="hace ref a la solicitud que genero el caso")   

    solProcedimiento = models.TextField(max_length=2000,
                                        db_comment="Texto del procedimiento realizado en la solución del caso")
    solTipoSolucion = models.CharField(max_length=20, choices=tipoSolucion,
                                       db_comment="Tipo de la solucuín, si es parcial o definitiva")
    fechaHoraCreacion = models.DateTimeField(auto_now_add=True,
                                             db_comment="Fecha y hora de creacion")
    fechaHoraActualizacion = models.DateTimeField(auto_now=True,
                                                    db_comment="Fecha y hora de actualizacion")
    def __str__(self):
        return self.solTipoSolucion   




class SolucionCasotipoProcedimiento (models.Model):
    solSolucionCaso =models.ForeignKey(SolucionCaso, on_delete=models.PROTECT, db_comment="Llave foranea de Solucion del caso")
    solTipoProcedimiento =models.ForeignKey(TipoProcedimiento, on_delete=models.PROTECT, db_comment="Llave foranea de Solucion de Tipo de procedimiento")
    def __str__(self):
        return f"{self.sp_solucion_caso},{self.sp_tipo_procedimiento}"



from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.core.validators import RegexValidator, MinValueValidator
from django.db.models import Q, F


# ===============================
# ✅ VALIDADORES REUSABLES
# ===============================

cedula_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="La cédula debe tener exactamente 10 dígitos numéricos."
)

telefono_10_validator = RegexValidator(
    regex=r"^\d{10}$",
    message="El teléfono debe tener exactamente 10 dígitos numéricos."
)

telefono_8_10_validator = RegexValidator(
    regex=r"^(?:\d{8}|\d{10})$",
    message="El teléfono debe tener 8 o 10 dígitos numéricos."
)

telefono_convencional_validator = RegexValidator(
    regex=r"^(?:\d{8}|[Nn][Oo])$",
    message="El teléfono convencional debe tener 8 dígitos o escribir 'no'."
)


def fecha_no_futura(value):
    """✅ No permitir fechas futuras."""
    if value and value > timezone.now().date():
        raise ValidationError("La fecha no puede ser futura.")


# ===============================
# ✅ MODELO BASE (OBLIGA VALIDACIÓN)
# ===============================
class ValidatedModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.full_clean()  # ✅ obliga validaciones
        super().save(*args, **kwargs)


# ===============================
# ✅ DATOS PERSONALES
# ===============================
class DatosPersonales(ValidatedModel):
    SEXO_CHOICES = [
        ("H", "Hombre"),
        ("M", "Mujer"),
    ]

    idperfil = models.AutoField(primary_key=True)

    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.IntegerField(
        choices=[(1, "Activo"), (0, "Inactivo")],
        default=1
    )

    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)

    fechanacimiento = models.DateField(
        null=True,
        blank=True,
        validators=[fecha_no_futura]
    )

    numerocedula = models.CharField(
        max_length=10,
        unique=True,
        validators=[cedula_validator]
    )

    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)

    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)

    telefonoconvencional = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[telefono_convencional_validator]
    )

    telefonofijo = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        validators=[telefono_10_validator]
    )

    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50)

    sitioweb = models.URLField(max_length=200, blank=True, null=True)

    # ✅ FOTO PERFIL (Cloudinary)
    fotoperfil = models.ImageField(upload_to="fotos/", blank=True, null=True)

    class Meta:
        db_table = "datospersonales"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


# ===============================
# ✅ EXPERIENCIA LABORAL
# ===============================
class ExperienciaLaboral(ValidatedModel):
    idexperiencialaboral = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50)

    emailempresa = models.EmailField(max_length=100, blank=True, null=True)
    sitiowebempresa = models.URLField(max_length=200, blank=True, null=True)

    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)

    telefonocontactoempresarial = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        validators=[telefono_8_10_validator]
    )

    fechainiciogestion = models.DateField(validators=[fecha_no_futura])
    fechafingestion = models.DateField(blank=True, null=True)

    descripcionfunciones = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    rutacertificado = models.FileField(
        upload_to="certificados/experiencia/",
        blank=True,
        null=True
    )

    def clean(self):
        hoy = timezone.now().date()

        if self.fechafingestion and self.fechafingestion > hoy:
            raise ValidationError({"fechafingestion": "La fecha fin no puede ser futura."})

        if self.fechafingestion and self.fechainiciogestion and self.fechafingestion < self.fechainiciogestion:
            raise ValidationError({"fechafingestion": "La fecha fin no puede ser menor que la fecha de inicio."})

    class Meta:
        db_table = "experiencialaboral"
        constraints = [
            models.CheckConstraint(
                condition=Q(fechafingestion__isnull=True) | Q(fechafingestion__gte=F("fechainiciogestion")),
                name="experiencia_fechas_validas"
            )
        ]

    def __str__(self):
        return f"{self.cargodesempenado} - {self.nombrempresa}"


# ===============================
# ✅ CURSOS REALIZADOS
# ===============================
class CursosRealizados(ValidatedModel):
    idcursorealizado = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombrecurso = models.CharField(max_length=100)

    fechainicio = models.DateField(validators=[fecha_no_futura])
    fechafin = models.DateField(validators=[fecha_no_futura])

    totalhoras = models.IntegerField(validators=[MinValueValidator(0)])
    descripcioncurso = models.CharField(max_length=100)

    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)

    telefonocontactoauspicia = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        validators=[telefono_8_10_validator]
    )

    emailempresapatrocinadora = models.EmailField(max_length=100, blank=True, null=True)

    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="certificados/cursos/", blank=True, null=True)

    def clean(self):
        if self.fechafin and self.fechainicio and self.fechafin < self.fechainicio:
            raise ValidationError({"fechafin": "La fecha fin no puede ser menor que la fecha de inicio."})

    class Meta:
        db_table = "cursosrealizados"

    def __str__(self):
        return self.nombrecurso


# ===============================
# ✅ RECONOCIMIENTOS
# ===============================
class Reconocimientos(ValidatedModel):
    TIPO_CHOICES = [
        ("Académico", "Académico"),
        ("Público", "Público"),
        ("Privado", "Privado"),
    ]

    idreconocimiento = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES)
    fechareconocimiento = models.DateField(validators=[fecha_no_futura])
    descripcionreconocimiento = models.CharField(max_length=100)

    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)

    telefonocontactoauspicia = models.CharField(
        max_length=60,
        blank=True,
        null=True,
        validators=[telefono_8_10_validator]
    )

    activarparaqueseveaenfront = models.BooleanField(default=True)

    rutacertificado = models.FileField(
        upload_to="certificados/reconocimientos/",
        blank=True, null=True
    )

    class Meta:
        db_table = "reconocimientos"

    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.descripcionreconocimiento}"


# ===============================
# ✅ PRODUCTOS ACADÉMICOS
# ===============================
class ProductosAcademicos(ValidatedModel):
    idproductoacademico = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombrerecurso = models.CharField(max_length=120)
    clasificador = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200)

    activarparaqueseveaenfront = models.BooleanField(default=True)

    rutacertificado = models.FileField(
        upload_to="productos/academicos/",
        blank=True, null=True
    )

    class Meta:
        db_table = "productosacademicos"

    def __str__(self):
        return self.nombrerecurso


# ===============================
# ✅ PRODUCTOS LABORALES
# ===============================
class ProductosLaborales(ValidatedModel):
    idproductolaboral = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombreproducto = models.CharField(max_length=120)
    fechaproducto = models.DateField(blank=True, null=True, validators=[fecha_no_futura])
    descripcion = models.CharField(max_length=200)

    activarparaqueseveaenfront = models.BooleanField(default=True)

    rutacertificado = models.FileField(
        upload_to="productos/laborales/",
        blank=True, null=True
    )

    class Meta:
        db_table = "productoslaborales"

    def __str__(self):
        return self.nombreproducto


# ===============================
# ✅ VENTA DE GARAGE
# ===============================
class VentaGarage(ValidatedModel):
    ESTADO_CHOICES = [
        ("Disponible", "Disponible"),
        ("Vendido", "Vendido"),
    ]

    idventagarage = models.AutoField(primary_key=True)

    perfil = models.ForeignKey(
        DatosPersonales,
        on_delete=models.CASCADE,
        db_column="idperfilconqueestaactivo"
    )

    nombreproducto = models.CharField(max_length=120)

    valordelbien = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )

    estadoproducto = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default="Disponible"
    )

    descripcion = models.CharField(max_length=250)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    class Meta:
        db_table = "ventagarage"
        constraints = [
            models.CheckConstraint(condition=Q(valordelbien__gte=0), name="garage_valor_gte_0")
        ]

    def __str__(self):
        return f"{self.nombreproducto} - {self.estadoproducto}"

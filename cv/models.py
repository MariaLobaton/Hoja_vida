from django.db import models


# ===============================
# ✅ DATOS PERSONALES
# ===============================
class DatosPersonales(models.Model):
    SEXO_CHOICES = [
        ("H", "Hombre"),
        ("M", "Mujer"),
    ]

    idperfil = models.AutoField(primary_key=True)
    descripcionperfil = models.CharField(max_length=50)
    perfilactivo = models.IntegerField()
    apellidos = models.CharField(max_length=60)
    nombres = models.CharField(max_length=60)
    nacionalidad = models.CharField(max_length=20)
    lugarnacimiento = models.CharField(max_length=60)
    fechanacimiento = models.DateField()
    numerocedula = models.CharField(max_length=10, unique=True)
    sexo = models.CharField(max_length=1, choices=SEXO_CHOICES)
    estadocivil = models.CharField(max_length=50)
    licenciaconducir = models.CharField(max_length=6, blank=True, null=True)
    telefonoconvencional = models.CharField(max_length=15, blank=True, null=True)
    telefonofijo = models.CharField(max_length=15, blank=True, null=True)
    direcciontrabajo = models.CharField(max_length=50, blank=True, null=True)
    direcciondomiciliaria = models.CharField(max_length=50)
    sitioweb = models.CharField(max_length=60, blank=True, null=True)
    fotoperfil = models.ImageField(upload_to="fotos/", blank=True, null=True)

    class Meta:
        db_table = "datospersonales"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"


# ===============================
# ✅ EXPERIENCIA LABORAL
# ===============================
class ExperienciaLaboral(models.Model):
    idexperiencialaboral = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")
    cargodesempenado = models.CharField(max_length=100)
    nombrempresa = models.CharField(max_length=50)
    lugarempresa = models.CharField(max_length=50)
    emailempresa = models.CharField(max_length=100)
    sitiowebempresa = models.CharField(max_length=100, blank=True, null=True)
    nombrecontactoempresarial = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoempresarial = models.CharField(max_length=60, blank=True, null=True)
    fechainiciogestion = models.DateField()
    fechafingestion = models.DateField(blank=True, null=True)
    descripcionfunciones = models.CharField(max_length=100)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="certificados/experiencia/", blank=True, null=True)

    class Meta:
        db_table = "experiencialaboral"

    def __str__(self):
        return f"{self.cargodesempenado} - {self.nombrempresa}"


# ===============================
# ✅ CURSOS REALIZADOS
# ===============================
class CursosRealizados(models.Model):
    idcursorealizado = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")
    nombrecurso = models.CharField(max_length=100)
    fechainicio = models.DateField()
    fechafin = models.DateField()
    totalhoras = models.IntegerField()
    descripcioncurso = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    emailempresapatrocinadora = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="certificados/cursos/", blank=True, null=True)

    class Meta:
        db_table = "cursosrealizados"

    def __str__(self):
        return self.nombrecurso


# ===============================
# ✅ RECONOCIMIENTOS
# ===============================
class Reconocimientos(models.Model):
    TIPO_CHOICES = [
        ("Académico", "Académico"),
        ("Público", "Público"),
        ("Privado", "Privado"),
    ]

    idreconocimiento = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")
    tiporeconocimiento = models.CharField(max_length=100, choices=TIPO_CHOICES)
    fechareconocimiento = models.DateField()
    descripcionreconocimiento = models.CharField(max_length=100)
    entidadpatrocinadora = models.CharField(max_length=100)
    nombrecontactoauspicia = models.CharField(max_length=100, blank=True, null=True)
    telefonocontactoauspicia = models.CharField(max_length=60, blank=True, null=True)
    activarparaqueseveaenfront = models.BooleanField(default=True)

    # ✅ AHORA SÍ permite subir archivo desde el admin
    rutacertificado = models.FileField(upload_to="certificados/reconocimientos/", blank=True, null=True)

    class Meta:
        db_table = "reconocimientos"

    def __str__(self):
        return f"{self.tiporeconocimiento} - {self.descripcionreconocimiento}"


# ===============================
# ✅ PRODUCTOS ACADÉMICOS
# ===============================
class ProductosAcademicos(models.Model):
    idproductoacademico = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")

    nombrerecurso = models.CharField(max_length=120)
    clasificador = models.CharField(max_length=80)
    descripcion = models.CharField(max_length=200)

    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="productos/academicos/", blank=True, null=True)

    class Meta:
        db_table = "productosacademicos"

    def __str__(self):
        return self.nombrerecurso


# ===============================
# ✅ PRODUCTOS LABORALES
# ===============================
class ProductosLaborales(models.Model):
    idproductolaboral = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")

    nombreproducto = models.CharField(max_length=120)
    fechaproducto = models.DateField(blank=True, null=True)
    descripcion = models.CharField(max_length=200)

    activarparaqueseveaenfront = models.BooleanField(default=True)
    rutacertificado = models.FileField(upload_to="productos/laborales/", blank=True, null=True)

    class Meta:
        db_table = "productoslaborales"

    def __str__(self):
        return self.nombreproducto


# ===============================
# ✅ VENTA DE GARAGE
# ===============================
class VentaGarage(models.Model):
    ESTADO_CHOICES = [
        ("Disponible", "Disponible"),
        ("Vendido", "Vendido"),
    ]

    idventagarage = models.AutoField(primary_key=True)
    perfil = models.ForeignKey(DatosPersonales, on_delete=models.CASCADE, db_column="idperfilconqueestaactivo")

    nombreproducto = models.CharField(max_length=120)
    valordelbien = models.DecimalField(max_digits=10, decimal_places=2)
    estadoproducto = models.CharField(max_length=20, choices=ESTADO_CHOICES, default="Disponible")
    descripcion = models.CharField(max_length=250)

    activarparaqueseveaenfront = models.BooleanField(default=True)

    class Meta:
        db_table = "ventagarage"

    def __str__(self):
        return f"{self.nombreproducto} - {self.estadoproducto}"

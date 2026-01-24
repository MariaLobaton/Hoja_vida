from django.shortcuts import render, redirect
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.lib.utils import ImageReader

from urllib.request import urlopen
from io import BytesIO

from .models import (
    DatosPersonales, ExperienciaLaboral, CursosRealizados, Reconocimientos,
    ProductosAcademicos, ProductosLaborales, VentaGarage
)

from .forms import DatosPersonalesForm


# ======================================================
# ✅ VISTA PARA EDITAR PERFIL (SUBE FOTO A CLOUDINARY)
# ======================================================
def editar_perfil(request):
    """
    ✅ Edita el perfil activo.
    ✅ Si no existe uno, te deja CREARLO llenando el formulario.
    ✅ IMPORTANTE: usa request.FILES para subir imagen a Cloudinary
    """

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    if request.method == "POST":
        form = DatosPersonalesForm(request.POST, request.FILES, instance=perfil)

        if form.is_valid():
            nuevo = form.save(commit=False)

            # ✅ Si estás creando por primera vez, dejar activo
            if not perfil:
                nuevo.perfilactivo = 1

            nuevo.save()
            return redirect("cv_view")
    else:
        form = DatosPersonalesForm(instance=perfil)

    return render(request, "cv/editar_perfil.html", {
        "form": form,
        "perfil": perfil
    })


# ======================================================
# ✅ VISTA NORMAL HTML
# ======================================================
def cv_view(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    experiencia = []
    cursos = []
    reconocimientos = []
    productos_academicos = []
    productos_laborales = []
    garage = []

    if perfil:
        experiencia = ExperienciaLaboral.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        cursos = CursosRealizados.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        reconocimientos = Reconocimientos.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        productos_academicos = ProductosAcademicos.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        productos_laborales = ProductosLaborales.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        garage = VentaGarage.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        ).exclude(estadoproducto="Vendido")

    return render(request, "cv/cv.html", {
        "perfil": perfil,
        "experiencia": experiencia,
        "cursos": cursos,
        "reconocimientos": reconocimientos,
        "certificados": reconocimientos,  # ✅ para mostrar en Secciones como lista
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "garage": garage,
    })


# ======================================================
# ✅ PDF (REPORTLAB) + FOTO CLOUDINARY
# ======================================================
def cv_pdf(request):
    secciones = request.GET.getlist("sec")

    # ✅ IDs seleccionados de certificados (blindado)
    certificados_ids_raw = request.GET.getlist("cert")
    certificados_ids = []
    for x in certificados_ids_raw:
        try:
            if str(x).strip() != "":
                certificados_ids.append(int(x))
        except:
            pass

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    experiencia = []
    cursos = []
    reconocimientos = Reconocimientos.objects.none()
    productos_academicos = []
    productos_laborales = []
    garage = []

    if perfil:
        experiencia = ExperienciaLaboral.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        cursos = CursosRealizados.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        # ✅ Solo certificados seleccionados
        if certificados_ids:
            reconocimientos = Reconocimientos.objects.filter(
                perfil=perfil,
                activarparaqueseveaenfront=True,
                id__in=certificados_ids
            )
        else:
            reconocimientos = Reconocimientos.objects.none()

        productos_academicos = ProductosAcademicos.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        productos_laborales = ProductosLaborales.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        )

        garage = VentaGarage.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        ).exclude(estadoproducto="Vendido")

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="hoja_vida.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    x_left = 2 * cm
    x_right = width - 2 * cm
    y = height - 2 * cm

    # ======================================================
    # ✅ FUNCIÓN PARA CARGAR IMAGEN DESDE URL (CLOUDINARY)
    # ======================================================
    def draw_image_from_url(img_url, x, y_pos, w, h):
        try:
            with urlopen(img_url, timeout=7) as response_img:
                image_bytes = response_img.read()

            image_file = BytesIO(image_bytes)
            img = ImageReader(image_file)
            p.drawImage(img, x, y_pos, width=w, height=h, mask="auto")
            return True
        except:
            return False

    def nueva_pagina_si_es_necesario(min_y=3 * cm):
        nonlocal y
        if y < min_y:
            p.showPage()
            y = height - 2 * cm

    def draw_section_title(text):
        nonlocal y
        nueva_pagina_si_es_necesario()

        y -= 0.15 * cm
        p.setFillColor(colors.HexColor("#1f2937"))
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_left, y, text.upper())

        y -= 0.55 * cm

        if text.lower() != "datos personales":
            p.setStrokeColor(colors.HexColor("#1f2937"))
            p.setLineWidth(1)
            p.line(x_left, y, x_right, y)

        y -= 0.45 * cm

    def draw_wrapped_text(text, font="Helvetica", size=10, leading=16, max_width=None):
        nonlocal y
        if not text:
            return

        if max_width is None:
            max_width = x_right - x_left

        p.setFont(font, size)
        p.setFillColor(colors.black)

        words = str(text).split()
        line = ""

        for w in words:
            test = (line + " " + w).strip()
            if stringWidth(test, font, size) <= max_width:
                line = test
            else:
                nueva_pagina_si_es_necesario()
                p.drawString(x_left, y, line)
                y -= leading
                line = w

        if line:
            nueva_pagina_si_es_necesario()
            p.drawString(x_left, y, line)
            y -= leading

        y -= 4

    def draw_card(title, subtitle=None, body=None):
        nonlocal y
        nueva_pagina_si_es_necesario()

        padding = 12
        leading = 12
        text_width = (x_right - x_left - 2 * padding)

        def contar_lineas(texto, font="Helvetica", size=9, max_width=text_width):
            if not texto:
                return 0
            palabras = str(texto).split()
            linea = ""
            lineas = 1
            for w in palabras:
                prueba = (linea + " " + w).strip()
                if stringWidth(prueba, font, size) <= max_width:
                    linea = prueba
                else:
                    lineas += 1
                    linea = w
            return lineas

        card_height = 10
        card_height += 16

        if subtitle:
            card_height += 13

        if body:
            lineas_body = contar_lineas(body, font="Helvetica", size=9)
            card_height += (lineas_body * leading)

        card_height += 14

        p.setFillColor(colors.HexColor("#F3F4F6"))
        p.setStrokeColor(colors.HexColor("#D1D5DB"))
        p.roundRect(
            x_left, y - card_height,
            x_right - x_left, card_height,
            10, fill=1, stroke=1
        )

        text_y = y - 20

        p.setFillColor(colors.HexColor("#111827"))
        p.setFont("Helvetica-Bold", 11)
        p.drawString(x_left + padding, text_y, str(title))
        text_y -= 14

        if subtitle:
            p.setFillColor(colors.HexColor("#374151"))
            p.setFont("Helvetica", 9)
            p.drawString(x_left + padding, text_y, str(subtitle))
            text_y -= 12

        if body:
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 9)

            palabras = str(body).split()
            linea = ""

            for w in palabras:
                prueba = (linea + " " + w).strip()
                if stringWidth(prueba, "Helvetica", 9) <= text_width:
                    linea = prueba
                else:
                    p.drawString(x_left + padding, text_y, linea)
                    text_y -= leading
                    linea = w

            if linea:
                p.drawString(x_left + padding, text_y, linea)

        y -= (card_height + 14)

    # --------------------------
    # Encabezado con foto
    # --------------------------
    if not perfil:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(x_left, y, "No existe un perfil activo.")
        p.save()
        return response

    foto_size = 3.6 * cm
    foto_x = x_right - foto_size - 0.6 * cm
    foto_y = height - 5.0 * cm

    if perfil.fotoperfil:
        try:
            img_url = perfil.fotoperfil.url
            draw_image_from_url(img_url, foto_x, foto_y, foto_size, foto_size)
        except:
            pass

    p.setFillColor(colors.HexColor("#111827"))
    p.setFont("Helvetica-Bold", 18)
    p.drawString(x_left, y, f"{perfil.nombres} {perfil.apellidos}")
    y -= 22

    p.setFillColor(colors.HexColor("#4b5563"))
    p.setFont("Helvetica", 11)
    p.drawString(x_left, y, perfil.descripcionperfil)
    y -= 25

    # =========================
    # ✅ SECCIONES CV NORMAL
    # =========================
    if "datos" in secciones:
        draw_section_title("Datos personales")
        draw_wrapped_text(f"Cédula: {perfil.numerocedula}", size=10)
        draw_wrapped_text(f"Nacionalidad: {perfil.nacionalidad}", size=10)
        draw_wrapped_text(f"Dirección: {perfil.direcciondomiciliaria}", size=10)

    if "experiencia" in secciones:
        draw_section_title("Experiencia laboral")
        if experiencia:
            for e in experiencia:
                draw_card(
                    title=f"{e.cargodesempenado} - {e.nombrempresa}",
                    subtitle=e.lugarempresa,
                    body=e.descripcionfunciones
                )
        else:
            draw_card("No hay experiencia registrada.")

    if "cursos" in secciones:
        draw_section_title("Cursos realizados")
        if cursos:
            for c in cursos:
                draw_card(
                    title=f"{c.nombrecurso} ({c.totalhoras} horas)",
                    subtitle=f"{c.fechainicio} - {c.fechafin}",
                    body=c.descripcioncurso
                )
        else:
            draw_card("No hay cursos registrados.")

    if "prod_academicos" in secciones:
        draw_section_title("Productos académicos")
        if productos_academicos:
            for pa in productos_academicos:
                draw_card(
                    title=pa.nombrerecurso,
                    subtitle=pa.clasificador,
                    body=pa.descripcion
                )
        else:
            draw_card("No hay productos académicos registrados.")

    if "prod_laborales" in secciones:
        draw_section_title("Productos laborales")
        if productos_laborales:
            for pl in productos_laborales:
                draw_card(
                    title=pl.nombreproducto,
                    subtitle=str(pl.fechaproducto),
                    body=pl.descripcion
                )
        else:
            draw_card("No hay productos laborales registrados.")

    if "garage" in secciones:
        draw_section_title("Venta de garage")
        if garage:
            for g in garage:
                draw_card(
                    title=f"{g.nombreproducto} - ${g.valordelbien}",
                    subtitle=f"Estado: {g.estadoproducto}",
                    body=g.descripcion
                )
        else:
            draw_card("No hay productos disponibles en garage.")

    # ======================================================
    # ✅ ANEXOS: CERTIFICADOS SELECCIONADOS AL FINAL
    # ======================================================
    if "reconocimientos" in secciones:
        if reconocimientos.exists():
            for r in reconocimientos:
                if getattr(r, "rutacertificado", None):
                    try:
                        url_cert = r.rutacertificado.url

                        # ✅ SOLO IMÁGENES
                        if url_cert.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                            p.showPage()

                            # ✅ Título
                            p.setFillColor(colors.HexColor("#111827"))
                            p.setFont("Helvetica-Bold", 14)
                            p.drawString(x_left, height - 2 * cm, "ANEXO: CERTIFICADO")

                            p.setFont("Helvetica", 10)
                            p.setFillColor(colors.HexColor("#4b5563"))
                            p.drawString(
                                x_left,
                                height - 2.7 * cm,
                                f"{r.tiporeconocimiento} - {r.descripcionreconocimiento}"
                            )

                            # ✅ Descargar imagen
                            with urlopen(url_cert, timeout=7) as response_img:
                                image_bytes = response_img.read()

                            image_file = BytesIO(image_bytes)
                            img = ImageReader(image_file)

                            img_w, img_h = img.getSize()

                            # ✅ área disponible
                            max_w = width - (4 * cm)
                            max_h = height - (6 * cm)

                            # ✅ escalar proporcional
                            scale = min(max_w / img_w, max_h / img_h)
                            new_w = img_w * scale
                            new_h = img_h * scale

                            # ✅ centrar
                            x_img = (width - new_w) / 2
                            y_img = (height - new_h) / 2 - 0.5 * cm

                            p.drawImage(img, x_img, y_img, width=new_w, height=new_h, mask="auto")

                        else:
                            # ✅ si es PDF
                            p.showPage()
                            p.setFont("Helvetica-Bold", 12)
                            p.drawString(x_left, height - 2 * cm, "ANEXO: CERTIFICADO (PDF)")
                            p.setFont("Helvetica", 10)
                            p.drawString(
                                x_left,
                                height - 2.8 * cm,
                                f"{r.tiporeconocimiento} - {r.descripcionreconocimiento}"
                            )
                            p.setFont("Helvetica", 9)
                            p.setFillColor(colors.HexColor("#374151"))
                            p.drawString(
                                x_left,
                                height - 3.6 * cm,
                                "📌 Este certificado está en PDF y ReportLab no lo imprime como imagen."
                            )

                    except:
                        p.showPage()
                        p.setFont("Helvetica-Bold", 12)
                        p.drawString(x_left, height - 2 * cm, "❌ Error al cargar certificado")
                        p.setFont("Helvetica", 10)
                        p.drawString(x_left, height - 2.8 * cm, f"{r.tiporeconocimiento}")

        else:
            # Si no eligió ninguno
            draw_section_title("Certificados / Reconocimientos")
            draw_card("No seleccionaste certificados para imprimir.")

    p.save()
    return response

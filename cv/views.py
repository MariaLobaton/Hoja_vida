from django.shortcuts import render
from django.http import HttpResponse

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.pdfbase.pdfmetrics import stringWidth

from .models import (
    DatosPersonales, ExperienciaLaboral, CursosRealizados, Reconocimientos,
    ProductosAcademicos, ProductosLaborales, VentaGarage
)


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

        # ✅ Solo mostrar lo que NO esté vendido (si existe ese estado)
        garage = VentaGarage.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        ).exclude(estadoproducto="Vendido")

    return render(request, "cv/cv.html", {
        "perfil": perfil,
        "experiencia": experiencia,
        "cursos": cursos,
        "reconocimientos": reconocimientos,
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "garage": garage,
    })


# ======================================================
# ✅ PDF
# ======================================================
def cv_pdf(request):
    secciones = request.GET.getlist("sec")
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

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="hoja_vida.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # ✅ Márgenes
    x_left = 2 * cm
    x_right = width - 2 * cm
    y = height - 2 * cm

    # --------------------------
    # Funciones de apoyo
    # --------------------------
    def nueva_pagina_si_es_necesario():
        nonlocal y
        if y < 3 * cm:
            p.showPage()
            y = height - 2 * cm

    def draw_section_title(text):
        """
        ✅ Título de sección y línea separada correctamente (NO roza el texto)
        """
        nonlocal y
        nueva_pagina_si_es_necesario()

        # Aire arriba (para que no se pegue a la tarjeta anterior)
        y -= 0.15 * cm

        # ✅ Título
        p.setFillColor(colors.HexColor("#1f2937"))
        p.setFont("Helvetica-Bold", 12)
        p.drawString(x_left, y, text.upper())

        # bajar un poquito para que NO roce
        y -= 0.55 * cm

        # ✅ Línea abajo (NO en datos personales si no quieres)
        if text.lower() != "datos personales":
            p.setStrokeColor(colors.HexColor("#1f2937"))
            p.setLineWidth(1)
            p.line(x_left, y, x_right, y)

        # bajar un poquito para empezar tarjetas/texto
        y -= 0.45 * cm

    def draw_wrapped_text(text, font="Helvetica", size=10, leading=16, max_width=None):
        """
        ✅ Texto con salto de línea automático
        """
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

        y -= 4  # aire

    def draw_card(title, subtitle=None, body=None):
        """
        ✅ Tarjeta gris que cubre TODO el texto
        """
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

        # ✅ altura real
        card_height = 10
        card_height += 16  # título

        if subtitle:
            card_height += 13

        if body:
            lineas_body = contar_lineas(body, font="Helvetica", size=9)
            card_height += (lineas_body * leading)

        card_height += 14

        # ✅ dibujar tarjeta
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
        p.showPage()
        p.save()
        return response

    # ✅ Foto más grande + buena posición
    foto_size = 3.6 * cm
    foto_x = x_right - foto_size - 0.6 * cm
    foto_y = height - 5.0 * cm

    if hasattr(perfil, "fotoperfil") and perfil.fotoperfil:
        try:
            p.drawImage(perfil.fotoperfil.path, foto_x, foto_y,
                        width=foto_size, height=foto_size, mask="auto")
        except:
            pass

    # ✅ Nombre
    p.setFillColor(colors.HexColor("#111827"))
    p.setFont("Helvetica-Bold", 18)
    p.drawString(x_left, y, f"{perfil.nombres} {perfil.apellidos}")
    y -= 22

    # ✅ Descripción
    p.setFillColor(colors.HexColor("#4b5563"))
    p.setFont("Helvetica", 11)
    p.drawString(x_left, y, perfil.descripcionperfil)
    y -= 25

    # --------------------------
    # Datos personales
    # --------------------------
    if "datos" in secciones:
        draw_section_title("Datos personales")
        draw_wrapped_text(f"Cédula: {perfil.numerocedula}", size=10)
        draw_wrapped_text(f"Nacionalidad: {perfil.nacionalidad}", size=10)
        draw_wrapped_text(f"Dirección: {perfil.direcciondomiciliaria}", size=10)

    # --------------------------
    # Experiencia
    # --------------------------
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

    # --------------------------
    # Cursos
    # --------------------------
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

    # --------------------------
    # Reconocimientos
    # --------------------------
    if "reconocimientos" in secciones:
        draw_section_title("Reconocimientos")
        if reconocimientos:
            for r in reconocimientos:
                draw_card(
                    title=f"{r.tiporeconocimiento}: {r.descripcionreconocimiento}",
                    subtitle=r.entidadpatrocinadora,
                    body=""
                )
        else:
            draw_card("No hay reconocimientos registrados.")

    # --------------------------
    # Productos académicos
    # --------------------------
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

    # --------------------------
    # Productos laborales
    # --------------------------
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

    # --------------------------
    # Venta de garage
    # --------------------------
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

    p.showPage()
    p.save()
    return response         
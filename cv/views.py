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
from datetime import date

from .models import (
    DatosPersonales, ExperienciaLaboral, CursosRealizados, Reconocimientos,
    ProductosAcademicos, ProductosLaborales, VentaGarage
)
from .forms import DatosPersonalesForm


# ======================================================
# ✅ VISTA PARA EDITAR PERFIL
# ======================================================
def editar_perfil(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    if request.method == "POST":
        form = DatosPersonalesForm(request.POST, request.FILES, instance=perfil)
        if form.is_valid():
            nuevo = form.save(commit=False)
            if not perfil:
                nuevo.perfilactivo = 1
            nuevo.save()
            return redirect("cv_view")
    else:
        form = DatosPersonalesForm(instance=perfil)

    return render(request, "cv/editar_perfil.html", {"form": form, "perfil": perfil})


# ======================================================
# ✅ VISTA NORMAL HTML
# ✅ Lista de CERTIFICADOS (Cursos + Reconocimientos + Productos)
# ======================================================
def cv_view(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    experiencia = []
    cursos = []
    reconocimientos = []
    productos_academicos = []
    productos_laborales = []
    garage = []
    certificados = []

    if perfil:
        experiencia = ExperienciaLaboral.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        cursos = CursosRealizados.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        reconocimientos = Reconocimientos.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        productos_academicos = ProductosAcademicos.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        productos_laborales = ProductosLaborales.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)

        garage = VentaGarage.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        ).exclude(estadoproducto="Vendido")

        # ✅ CERTIFICADOS DE CURSOS
        for c in cursos:
            if getattr(c, "rutacertificado", None):
                fecha = getattr(c, "fechafin", None) or getattr(c, "fechainicio", None)
                certificados.append({"value": f"CUR-{c.pk}", "nombre": c.nombrecurso, "tipo": "Curso", "fecha": fecha})

        # ✅ CERTIFICADOS DE RECONOCIMIENTOS
        for r in reconocimientos:
            if getattr(r, "rutacertificado", None):
                fecha = getattr(r, "fechareconocimiento", None)
                certificados.append({
                    "value": f"REC-{r.pk}",
                    "nombre": f"{r.tiporeconocimiento} - {r.descripcionreconocimiento}",
                    "tipo": "Reconocimiento",
                    "fecha": fecha
                })

        # ✅ CERTIFICADOS DE PRODUCTOS ACADÉMICOS
        for pa in productos_academicos:
            if getattr(pa, "rutacertificado", None):
                fecha = getattr(pa, "fecharecurso", None)
                certificados.append({
                    "value": f"PA-{pa.pk}",
                    "nombre": f"{pa.nombrerecurso} - {pa.clasificador}",
                    "tipo": "Producto académico",
                    "fecha": fecha
                })

        # ✅ CERTIFICADOS DE PRODUCTOS LABORALES
        for pl in productos_laborales:
            if getattr(pl, "rutacertificado", None):
                fecha = getattr(pl, "fechaproducto", None)
                certificados.append({
                    "value": f"PL-{pl.pk}",
                    "nombre": pl.nombreproducto,
                    "tipo": "Producto laboral",
                    "fecha": fecha
                })

        # ✅ ORDEN: MÁS ACTUAL → MÁS ANTIGUO (None al final)
        certificados.sort(key=lambda x: x["fecha"] or date.min, reverse=True)

    return render(request, "cv/cv.html", {
        "perfil": perfil,
        "experiencia": experiencia,
        "cursos": cursos,
        "reconocimientos": reconocimientos,
        "productos_academicos": productos_academicos,
        "productos_laborales": productos_laborales,
        "garage": garage,
        "certificados": certificados,
    })


# ======================================================
# ✅ PDF (REPORTLAB) + ANEXOS CERTIFICADOS
# ======================================================
def cv_pdf(request):
    secciones = request.GET.getlist("sec")
    certificados_tokens = request.GET.getlist("cert")

    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    experiencia = []
    cursos = []
    productos_academicos = []
    productos_laborales = []
    reconocimientos_cv = Reconocimientos.objects.none()

    if perfil:
        experiencia = ExperienciaLaboral.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        cursos = CursosRealizados.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        reconocimientos_cv = Reconocimientos.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        productos_academicos = ProductosAcademicos.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)
        productos_laborales = ProductosLaborales.objects.filter(perfil=perfil, activarparaqueseveaenfront=True)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'inline; filename="hoja_vida.pdf"'

    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    x_left = 2 * cm
    x_right = width - 2 * cm
    y = height - 2 * cm

    # =========================
    # Helpers
    # =========================
    def fmt_fecha(d):
        if not d:
            return ""
        try:
            return d.strftime("%d/%m/%Y")
        except:
            return str(d)

    def safe_text(t):
        return str(t).strip() if t is not None else ""

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

    def wrap_lines(text, font="Helvetica", size=10, max_width=200):
        text = safe_text(text)
        if not text:
            return []
        words = text.split()
        lines, line = [], ""
        for w_ in words:
            test = (line + " " + w_).strip()
            if stringWidth(test, font, size) <= max_width:
                line = test
            else:
                if line:
                    lines.append(line)
                line = w_
        if line:
            lines.append(line)
        return lines

    def draw_wrapped_at(x, y_top, text, font="Helvetica", size=10, leading=14, max_width=200, color=colors.black):
        """
        Dibuja texto con wrap en (x,y_top). Devuelve el nuevo y (más abajo).
        """
        if not text:
            return y_top
        lines = wrap_lines(text, font=font, size=size, max_width=max_width)
        p.setFillColor(color)
        p.setFont(font, size)
        yy = y_top
        for ln in lines:
            p.drawString(x, yy, ln)
            yy -= leading
        return yy

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
            linea, lineas = "", 1
            for w_ in palabras:
                prueba = (linea + " " + w_).strip()
                if stringWidth(prueba, font, size) <= max_width:
                    linea = prueba
                else:
                    lineas += 1
                    linea = w_
            return lineas

        card_height = 10 + 16
        if subtitle:
            card_height += 13
        if body:
            card_height += (contar_lineas(body, "Helvetica", 9) * leading)
        card_height += 14

        # ✅ Fondo blanco para mejor lectura en PDF
        p.setFillColor(colors.white)
        p.setStrokeColor(colors.HexColor("#D1D5DB"))
        p.roundRect(x_left, y - card_height, x_right - x_left, card_height, 10, fill=1, stroke=1)

        text_y = y - 20

        p.setFillColor(colors.HexColor("#111827"))
        p.setFont("Helvetica-Bold", 11)
        p.drawString(x_left + padding, text_y, safe_text(title))
        text_y -= 14

        if subtitle:
            p.setFillColor(colors.HexColor("#374151"))
            p.setFont("Helvetica", 9)
            p.drawString(x_left + padding, text_y, safe_text(subtitle))
            text_y -= 12

        if body:
            p.setFillColor(colors.black)
            p.setFont("Helvetica", 9)
            palabras = safe_text(body).split()
            linea = ""
            for w_ in palabras:
                prueba = (linea + " " + w_).strip()
                if stringWidth(prueba, "Helvetica", 9) <= text_width:
                    linea = prueba
                else:
                    p.drawString(x_left + padding, text_y, linea)
                    text_y -= leading
                    linea = w_
            if linea:
                p.drawString(x_left + padding, text_y, linea)

        y -= (card_height + 14)

    def draw_info_card(x, y_top, w, title, items, min_y=3 * cm):
        """
        Tarjeta en 2 columnas para Datos Personales.
        Retorna el y_final (parte baja).
        """
        nonlocal y

        clean = []
        for label, val in items:
            val_str = safe_text(val)
            if val_str and val_str.lower() != "none":
                clean.append((label, val_str))

        if not clean:
            clean = [("Sin datos", "")]

        padding = 12
        title_h = 16
        leading = 12
        font = "Helvetica"
        size = 10  # ✅ un poquito más grande para que se lea mejor
        text_w = w - 2 * padding

        wrapped_rows = []
        total_lines = 0
        for label, val in clean:
            row_text = f"{label}: {val}"
            lines = wrap_lines(row_text, font=font, size=size, max_width=text_w)
            if not lines:
                lines = [row_text]
            wrapped_rows.append(lines)
            total_lines += len(lines)

        card_h = padding + title_h + 8 + (total_lines * leading) + padding

        if (y_top - card_h) < min_y:
            p.showPage()
            y = height - 2 * cm
            y_top = y

        # ✅ Fondo blanco + borde para que contraste
        p.setFillColor(colors.white)
        p.setStrokeColor(colors.HexColor("#CBD5E1"))
        p.roundRect(x, y_top - card_h, w, card_h, 12, fill=1, stroke=1)

        # título
        p.setFillColor(colors.HexColor("#111827"))
        p.setFont("Helvetica-Bold", 10)
        p.drawString(x + padding, y_top - padding - 2, safe_text(title))

        # contenido
        text_y = y_top - padding - title_h - 6
        p.setFillColor(colors.black)
        p.setFont(font, size)

        for lines in wrapped_rows:
            for ln in lines:
                p.drawString(x + padding, text_y, ln)
                text_y -= leading

        return y_top - card_h

    # ======================================================
    # ✅ ENCABEZADO
    # ======================================================
    if not perfil:
        p.setFont("Helvetica-Bold", 14)
        p.drawString(x_left, y, "No existe un perfil activo.")
        p.save()
        return response

    # ✅ Foto
    foto_size = 3.8 * cm
    foto_margin = 0.6 * cm
    foto_x = x_right - foto_size
    foto_y = height - (2 * cm) - foto_size  # ✅ alineada con el top real

    hay_foto = False
    if getattr(perfil, "fotoperfil", None):
        hay_foto = draw_image_from_url(perfil.fotoperfil.url, foto_x, foto_y, foto_size, foto_size)

    # ✅ El texto del header no debe meterse donde está la foto
    header_right_limit = (foto_x - foto_margin) if hay_foto else x_right
    header_max_width = header_right_limit - x_left

    p.setFillColor(colors.HexColor("#111827"))
    p.setFont("Helvetica-Bold", 18)
    p.drawString(x_left, y, f"{safe_text(perfil.nombres)} {safe_text(perfil.apellidos)}")
    y -= 18

    # ✅ descripción con WRAP y sin chocar con la foto
    desc = safe_text(getattr(perfil, "descripcionperfil", ""))
    y = draw_wrapped_at(
        x_left, y,
        desc,
        font="Helvetica",
        size=11,
        leading=14,
        max_width=header_max_width,
        color=colors.HexColor("#4b5563")
    )
    y -= 8

    # ✅ IMPORTANTÍSIMO: si hay foto, forzamos que lo siguiente empiece debajo de la foto
    if hay_foto:
        limite_bajo_foto = foto_y - (0.6 * cm)
        if y > limite_bajo_foto:
            y = limite_bajo_foto

    # ======================================================
    # ✅ SECCIONES
    # ======================================================
    if "datos" in secciones:
        draw_section_title("Datos personales")

        items_left = [
            ("Cédula", getattr(perfil, "numerocedula", "")),
            ("Nacionalidad", getattr(perfil, "nacionalidad", "")),
            ("Lugar de nacimiento", getattr(perfil, "lugarnacimiento", "")),
            ("Fecha de nacimiento", fmt_fecha(getattr(perfil, "fechanacimiento", None))),
            ("Sexo", perfil.get_sexo_display() if getattr(perfil, "sexo", None) else ""),
            ("Estado civil", getattr(perfil, "estadocivil", "")),
        ]

        items_right = [
            ("Licencia de conducir", getattr(perfil, "licenciaconducir", "")),
            ("Teléfono convencional", getattr(perfil, "telefonoconvencional", "")),
            ("Teléfono", getattr(perfil, "telefonofijo", "")),
            ("Dirección domicilio", getattr(perfil, "direcciondomiciliaria", "")),
            ("Dirección trabajo", getattr(perfil, "direcciontrabajo", "")),
            ("Sitio web", getattr(perfil, "sitioweb", "")),
        ]

        gap = 0.6 * cm
        col_w = (x_right - x_left - gap) / 2
        y_top = y

        bottom_left = draw_info_card(x_left, y_top, col_w, "Identificación", items_left)
        bottom_right = draw_info_card(x_left + col_w + gap, y_top, col_w, "Contacto", items_right)

        y = min(bottom_left, bottom_right) - (0.8 * cm)

    if "experiencia" in secciones:
        draw_section_title("Experiencia laboral")
        if experiencia:
            for e in experiencia:
                fi = fmt_fecha(getattr(e, "fechainiciogestion", None))
                ff = fmt_fecha(getattr(e, "fechafingestion", None))
                rango = ""
                if fi and ff:
                    rango = f"{fi} - {ff}"
                elif fi and not ff:
                    rango = f"{fi} - Actualidad"
                elif ff and not fi:
                    rango = ff

                sub = safe_text(getattr(e, "lugarempresa", ""))
                if rango:
                    sub = f"{sub} | {rango}" if sub else rango

                draw_card(
                    title=f"{safe_text(e.cargodesempenado)} - {safe_text(e.nombrempresa)}",
                    subtitle=sub or None,
                    body=safe_text(getattr(e, "descripcionfunciones", ""))
                )
        else:
            draw_card("No hay experiencia registrada.")

    if "cursos" in secciones:
        draw_section_title("Cursos realizados")
        if cursos:
            for c in cursos:
                fi = fmt_fecha(getattr(c, "fechainicio", None))
                ff = fmt_fecha(getattr(c, "fechafin", None))
                sub = ""
                if fi and ff:
                    sub = f"{fi} - {ff}"
                elif fi:
                    sub = fi
                elif ff:
                    sub = ff

                draw_card(
                    title=f"{safe_text(c.nombrecurso)} ({getattr(c, 'totalhoras', '')} horas)",
                    subtitle=sub or None,
                    body=safe_text(getattr(c, "descripcioncurso", ""))
                )
        else:
            draw_card("No hay cursos registrados.")

    if "reconocimientos" in secciones:
        draw_section_title("Reconocimientos")
        if reconocimientos_cv:
            for r in reconocimientos_cv:
                fecha_rec = fmt_fecha(getattr(r, "fechareconocimiento", None))
                sub = safe_text(getattr(r, "entidadpatrocinadora", ""))
                if fecha_rec:
                    sub = f"{sub} | {fecha_rec}" if sub else fecha_rec

                draw_card(
                    title=f"{safe_text(r.tiporeconocimiento)}: {safe_text(r.descripcionreconocimiento)}",
                    subtitle=sub or None,
                    body=""
                )
        else:
            draw_card("No hay reconocimientos registrados.")

    if "prod_academicos" in secciones:
        draw_section_title("Productos académicos")
        if productos_academicos:
            for pa in productos_academicos:
                fecha_pa = fmt_fecha(getattr(pa, "fecharecurso", None))
                sub = safe_text(getattr(pa, "clasificador", ""))
                if fecha_pa:
                    sub = f"{sub} | {fecha_pa}" if sub else fecha_pa

                draw_card(
                    title=safe_text(pa.nombrerecurso),
                    subtitle=sub or None,
                    body=safe_text(getattr(pa, "descripcion", ""))
                )
        else:
            draw_card("No hay productos académicos registrados.")

    if "prod_laborales" in secciones:
        draw_section_title("Productos laborales")
        if productos_laborales:
            for pl in productos_laborales:
                fecha_pl = fmt_fecha(getattr(pl, "fechaproducto", None))
                draw_card(
                    title=safe_text(pl.nombreproducto),
                    subtitle=fecha_pl or None,
                    body=safe_text(getattr(pl, "descripcion", ""))
                )
        else:
            draw_card("No hay productos laborales registrados.")

    # ======================================================
    # ✅ ANEXOS
    # ======================================================
    if certificados_tokens:
        contador = 1

        for token in certificados_tokens:
            token = str(token).strip()
            if "-" not in token:
                continue

            tipo, idx = token.split("-", 1)
            try:
                idx = int(idx)
            except:
                continue

            nombre = ""
            url_cert = None

            if tipo == "CUR":
                obj = CursosRealizados.objects.filter(pk=idx, perfil=perfil).first()
                if obj and getattr(obj, "rutacertificado", None):
                    nombre = obj.nombrecurso
                    url_cert = obj.rutacertificado.url

            elif tipo == "REC":
                obj = Reconocimientos.objects.filter(pk=idx, perfil=perfil).first()
                if obj and getattr(obj, "rutacertificado", None):
                    nombre = f"{obj.tiporeconocimiento} - {obj.descripcionreconocimiento}"
                    url_cert = obj.rutacertificado.url

            elif tipo == "PA":
                obj = ProductosAcademicos.objects.filter(pk=idx, perfil=perfil).first()
                if obj and getattr(obj, "rutacertificado", None):
                    nombre = f"{obj.nombrerecurso} - {obj.clasificador}"
                    url_cert = obj.rutacertificado.url

            elif tipo == "PL":
                obj = ProductosLaborales.objects.filter(pk=idx, perfil=perfil).first()
                if obj and getattr(obj, "rutacertificado", None):
                    nombre = obj.nombreproducto
                    url_cert = obj.rutacertificado.url

            if not url_cert:
                continue

            p.showPage()

            p.setFillColor(colors.HexColor("#111827"))
            p.setFont("Helvetica-Bold", 14)
            p.drawString(x_left, height - 2 * cm, f"ANEXO {contador}: CERTIFICADO")

            p.setFillColor(colors.HexColor("#4b5563"))
            p.setFont("Helvetica", 10)
            p.drawString(x_left, height - 2.7 * cm, safe_text(nombre))

            y_temp = height - 4.0 * cm

            try:
                if url_cert.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                    with urlopen(url_cert, timeout=7) as response_img:
                        image_bytes = response_img.read()

                    image_file = BytesIO(image_bytes)
                    img = ImageReader(image_file)

                    img_w, img_h = img.getSize()
                    max_w = width - (4 * cm)
                    max_h = height - (6 * cm)

                    scale = min(max_w / img_w, max_h / img_h)
                    new_w = img_w * scale
                    new_h = img_h * scale

                    x_img = (width - new_w) / 2
                    y_img = (height - new_h) / 2 - 0.8 * cm

                    p.drawImage(img, x_img, y_img, width=new_w, height=new_h, mask="auto")
                else:
                    p.setFillColor(colors.red)
                    p.setFont("Helvetica-Bold", 11)
                    p.drawString(x_left, y_temp, "⚠️ El certificado está en PDF y ReportLab NO lo imprime.")
                    p.setFillColor(colors.black)
                    p.setFont("Helvetica", 10)
                    p.drawString(x_left, y_temp - 18, "Convierte el PDF a PNG/JPG para que se imprima.")
            except:
                p.setFillColor(colors.red)
                p.setFont("Helvetica-Bold", 11)
                p.drawString(x_left, y_temp, "❌ Error al cargar el certificado.")

            contador += 1

    p.save()
    return response


# ======================================================
# ✅ PÁGINA APARTE: GARAGE BONITO
# ======================================================
def garage_list(request):
    perfil = DatosPersonales.objects.filter(perfilactivo=1).first()

    productos = VentaGarage.objects.none()
    if perfil:
        productos = VentaGarage.objects.filter(
            perfil=perfil,
            activarparaqueseveaenfront=True
        ).exclude(estadoproducto="Vendido")

    whatsapp_number = "59397871697"

    return render(request, "cv/garage_list.html", {
        "perfil": perfil,
        "productos": productos,
        "whatsapp_number": whatsapp_number,
    })

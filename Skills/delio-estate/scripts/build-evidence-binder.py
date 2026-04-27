#!/usr/bin/env python3
"""Build the Delio Estate Evidence Binder PDF.

Combines:
  - Cover + executive summary + tab dividers (markdown -> PDF via weasyprint)
  - Evidence image pages (reportlab)
  - Existing source PDFs (caso-herencia, estate-plan-of-action)

Output: Documents/Delio-Estate-Evidence-Binder.pdf
"""

import os
import subprocess
import tempfile
from datetime import date
from pathlib import Path

from pypdf import PdfWriter, PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor, black, grey
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak, Table, TableStyle
)
from PIL import Image as PILImage

ROOT = Path("/home/workspace/Skills/delio-estate")
EVID = ROOT / "evidence"
OUT = Path("/home/workspace/Documents/Delio-Estate-Evidence-Binder.pdf")
BUILD = Path(tempfile.mkdtemp(prefix="delio-binder-"))

TODAY = date.today().isoformat()

# ---------- Styles ----------

styles = getSampleStyleSheet()
H1 = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=22, spaceAfter=12,
                   textColor=HexColor("#111111"))
H2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=15, spaceAfter=8,
                   textColor=HexColor("#222222"))
H3 = ParagraphStyle("H3", parent=styles["Heading3"], fontSize=12, spaceAfter=6,
                   textColor=HexColor("#333333"))
P  = ParagraphStyle("P",  parent=styles["BodyText"], fontSize=10.5, leading=14,
                   spaceAfter=6)
SMALL = ParagraphStyle("S", parent=styles["BodyText"], fontSize=9, leading=12,
                       textColor=grey)
TAB   = ParagraphStyle("TAB", parent=styles["Heading1"], fontSize=40,
                       alignment=1, textColor=HexColor("#8B0000"),
                       spaceBefore=6*cm, spaceAfter=cm)
TABSUB = ParagraphStyle("TABSUB", parent=styles["BodyText"], fontSize=16,
                        alignment=1, textColor=HexColor("#333333"))
CAPTION = ParagraphStyle("CAP", parent=styles["BodyText"], fontSize=9.5,
                         alignment=1, textColor=HexColor("#333333"),
                         spaceBefore=6, spaceAfter=0)

# ---------- Helpers ----------

def make_doc(path):
    return SimpleDocTemplate(
        str(path), pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
        title="Delio Estate — Evidence Binder",
        author="Dioni Vásquez"
    )

def build_cover():
    path = BUILD / "01-cover.pdf"
    doc = make_doc(path)
    story = []
    story.append(Spacer(1, 4*cm))
    story.append(Paragraph("EVIDENCE BINDER", H1))
    story.append(Paragraph("Sucesión Delio Antonio Vásquez Vásquez", H2))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph(
        "Causante: Delio Antonio Vásquez Vásquez · Cédula 031-0513268-6 · "
        "SSN 584-52-1788 · Fallecido 13 de junio de 2021 · Puñal, Santiago, RD",
        P))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("<b>Heredera única por testamento auténtico:</b> Gisela Vásquez (madre de Dioni Vásquez).", P))
    story.append(Paragraph("<b>Adversa:</b> Amarilys Altagracia Vásquez · Cédula 031-0235285-7.", P))
    story.append(Spacer(1, 2*cm))
    story.append(Paragraph("Contenido", H2))
    toc = [
        ["Tab", "Sección"],
        ["1",   "Resumen ejecutivo"],
        ["2",   "Causante y autoridad sucesoral"],
        ["3",   "Las partes"],
        ["4",   "Cronología del caso"],
        ["5",   "Patrón de fraude (movidas de la adversa)"],
        ["6",   "Bienes y estado de amenaza"],
        ["7",   "Evidencia bancaria y SSA (imágenes)"],
        ["8",   "Traspaso fraudulento del Nissan"],
        ["9",   "Casa — título retenido y ruta del duplicado"],
        ["10",  "Caja fuerte y documentos personales"],
        ["11",  "Preguntas abiertas para el abogado"],
        ["12",  "Documentos fuente — expediente completo"],
    ]
    t = Table(toc, colWidths=[1.5*cm, 13*cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HexColor("#EEEEEE")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("LINEBELOW", (0,0), (-1,-1), 0.3, HexColor("#CCCCCC")),
    ]))
    story.append(t)
    story.append(Spacer(1, 1.5*cm))
    story.append(Paragraph(f"Preparado: {TODAY} · Uso exclusivo del abogado y la familia.", SMALL))
    doc.build(story)
    return path

def build_tab_divider(number, title, subtitle=""):
    path = BUILD / f"tab-{number:02d}-divider.pdf"
    doc = make_doc(path)
    story = [
        Spacer(1, 6*cm),
        Paragraph(f"TAB {number}", TAB),
        Paragraph(title, TABSUB),
    ]
    if subtitle:
        story += [Spacer(1, 0.4*cm), Paragraph(subtitle, SMALL)]
    doc.build(story)
    return path

def build_text_section(number, title, paragraphs):
    path = BUILD / f"tab-{number:02d}-content.pdf"
    doc = make_doc(path)
    story = [Paragraph(f"Tab {number} · {title}", H1), Spacer(1, 0.3*cm)]
    for p in paragraphs:
        if isinstance(p, tuple):
            kind, body = p
            if kind == "h2":
                story.append(Paragraph(body, H2))
            elif kind == "h3":
                story.append(Paragraph(body, H3))
            elif kind == "table":
                t = Table(body, colWidths=[4*cm, 12*cm])
                t.setStyle(TableStyle([
                    ("BACKGROUND", (0,0), (-1,0), HexColor("#EEEEEE")),
                    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
                    ("FONTSIZE", (0,0), (-1,-1), 9.5),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                    ("TOPPADDING", (0,0), (-1,-1), 5),
                    ("LINEBELOW", (0,0), (-1,-1), 0.3, HexColor("#CCCCCC")),
                ]))
                story.append(t)
                story.append(Spacer(1, 0.3*cm))
            elif kind == "bullet":
                for b in body:
                    story.append(Paragraph("• " + b, P))
        else:
            story.append(Paragraph(p, P))
    doc.build(story)
    return path

def build_image_page(number, img_path, caption, subcaption=""):
    path = BUILD / f"tab-{number:02d}-img-{Path(img_path).stem}.pdf"
    doc = make_doc(path)
    # Fit image within page
    page_w = A4[0] - 4*cm
    page_h = A4[1] - 6*cm
    with PILImage.open(img_path) as im:
        iw, ih = im.size
    scale = min(page_w / iw, page_h / ih)
    w, h = iw * scale, ih * scale
    story = [
        Paragraph(f"Tab {number} · Evidencia", H3),
        Paragraph(f"<b>{caption}</b>", CAPTION),
        Spacer(1, 0.2*cm),
        Image(str(img_path), width=w, height=h),
    ]
    if subcaption:
        story += [Spacer(1, 0.2*cm), Paragraph(subcaption, SMALL)]
    doc.build(story)
    return path

# ---------- Tab content ----------

def tab2_authority():
    return build_text_section(2, "Causante y autoridad sucesoral", [
        ("h2", "Identidad del causante"),
        ("table", [
            ["Nombre", "Delio Antonio Vásquez Vásquez"],
            ["Cédula DR", "031-0513268-6"],
            ["SSN (EE.UU.)", "584-52-1788 (confirmado por SSA-1099 2018)"],
            ["Fecha nacimiento", "13 de abril de 1941"],
            ["Fecha defunción", "13 de junio de 2021 (en casa, causas naturales)"],
            ["Domicilio", "Los Vásquez, Puñal, Santiago, República Dominicana"],
            ["Estado civil", "SOLTERO — sin descendientes. Padres premuertos."],
        ]),
        ("h2", "Mecanismo sucesoral"),
        "El causante otorgó <b>testamento auténtico</b> ante notario. El testamento fue abierto y leído ante el notario-abogado inicial de la familia.",
        "<b>Heredera única: Gisela Vásquez</b> (madre de Dioni Vásquez). Esta es la verdad legal que rige la masa sucesoral; cualquier alegato extra-testamentario de la adversa (deudas no documentadas, promesas verbales) carece de efecto legal frente al testamento.",
        ("h2", "Autoridad actual"),
        "Gisela ha otorgado <b>Poder Especial</b> al abogado-notario de la familia (poder ya existente al 18-Abr-2026). Ese poder habilita solicitudes bancarias, Registro de Títulos, DGII sucesión, ProUsuario/SIB y cualquier acción civil.",
        "<i>Pendiente de confirmar: nombre y datos de contacto del abogado-notario actual; alcance exacto del poder.</i>",
    ])

def tab3_parties():
    return build_text_section(3, "Las partes", [
        ("h2", "Nuestra parte"),
        ("bullet", [
            "<b>Gisela Vásquez</b> — madre de Dioni. Heredera única. Firmó trámites de casa el 14-Mar-2026 en DR.",
            "<b>Dioni Vásquez</b> — hijo de Gisela. Representante autorizado desde EE.UU. Coordinación estratégica.",
            "<b>Davie Elvis Rosarios</b> — primo. Vive en Puñal en la casa de la abuela, contigua al inmueble del causante. Ejecuta todas las diligencias físicas.",
            "<b>Abogado-notario de la familia</b> (actual, desde ~4-Abr-2026) — <i>nombre y datos pendientes de confirmar</i>. Reemplazó a dos abogados previos (Lic. Angela/Clarisa, Lic. Andrew).",
        ]),
        ("h2", "Parte adversa"),
        ("bullet", [
            "<b>Amarilys Altagracia Vásquez</b> (hermana del causante) · Cédula 031-0235285-7. Retuvo el Certificado de Título original; declaró la defunción tardíamente (10-Nov-2021); presuntamente cobró pagos de Seguro Social de EE.UU. tras la muerte; intentó montar una determinación de herederos fraudulenta con testigos que no comparten el apellido.",
            "<b>“Válido”</b> — abogado de Amarilys. Honorarios pactados al 30% del monto negociado. Conocido localmente; Davie lo describe como “delincuente”.",
            "<b>Luis José</b> (“hermano de cabo”) — presunto acreedor invocado por Amarilys. Sin documentación. La deuda NO figura en el testamento (confirmado por Davie, 26-Oct-2025).",
        ]),
    ])

def tab4_timeline():
    return build_text_section(4, "Cronología del caso", [
        ("h2", "Hechos clave"),
        ("table", [
            ["13 Jun 2021", "Muerte real del causante, en casa, en Puñal."],
            ["20 Sep 2021", "<b>Traspaso fraudulento</b> del vehículo Nissan registrado en DGII — 3 meses DESPUÉS de la muerte real y ANTES de que se declarara la defunción."],
            ["10 Nov 2021", "Declaración tardía de defunción — declarante: Amarilys. 5 meses tarde."],
            ["~Oct 2025", "Se encuentra en la casa lista manuscrita: “Documentos para una determinación de herederos”, solicitando 7 cédulas de vecinos “que no tengan su apellido” — patrón clásico de acta de notoriedad fabricada."],
            ["24 Oct 2025", "El abogado de Amarilys contacta a la parte nuestra. Alega deuda a Luis José y supuesta promesa verbal. Sin documentación."],
            ["26 Oct 2025", "Amarilys exige RD$8,000,000 para arreglar. Luego baja a RD$5,000,000 (con 30% a su abogado)."],
            ["5 Dec 2025", "La familia declara pérdida del título y de la matrícula ante Policía Nacional y publica en periódico, para viabilizar duplicados."],
            ["~13 Mar 2026", "Viaje físico de Gisela a DR para firmas."],
            ["14 Mar 2026", "Gisela firma documento inicial de trámites de casa."],
            ["~4 Apr 2026", "Cambio al tercer abogado (abogado-notario de la familia)."],
            ["Abr 2026", "Se reporta que la <b>caja fuerte fue encontrada abierta</b>. Tarjeta de Seguro Social del causante en poder de Amarilys (admitido); probable que cédula y pasaporte también."],
        ]),
    ])

def tab5_fraud_pattern():
    return build_text_section(5, "Patrón de fraude — movidas de la adversa", [
        ("h2", "Suma de actos imputables"),
        ("bullet", [
            "<b>Traspaso imposible del Nissan</b> (20-Sep-2021): un causante fallecido no puede transferir un vehículo. Actuación material + documental en DGII.",
            "<b>Declaración tardía de defunción</b> (10-Nov-2021): compatible con el objetivo de mantener fluyendo depósitos mensuales de Seguro Social de EE.UU. durante 5 meses (~US$6,500+).",
            "<b>Reclutamiento de testigos falsos</b> para una determinación de herederos paralela — estrangeros a la familia que “sepan firmar”.",
            "<b>Retención del Certificado de Título</b> original de la casa como palanca de extorsión.",
            "<b>Demanda extrajudicial por RD$8,000,000</b> sin título ni documento que respalde derecho alguno (el testamento excluye expresamente a Amarilys de la masa).",
            "<b>Presunto cobro de pensión de Seguro Social de EE.UU. del causante fallecido</b> — potencial 42 USC §408, 18 USC §641, 18 USC §1343.",
            "<b>Caja fuerte abierta y documentos personales sustraídos</b> — tarjeta de SS admitidamente en poder de Amarilys.",
        ]),
        ("h2", "Marco jurídico civil (RD) — sin vía penal por defecto"),
        "Ruta preferida del cliente: <b>vía civil y administrativa primero</b>, reservando denuncia penal únicamente como contingencia si el banco retrasa respuesta o la adversa presenta contra-acción.",
        ("bullet", [
            "Nulidad del traspaso del Nissan por causa imposible + repetición — tribunal civil.",
            "Nulidad de cualquier acta de notoriedad o determinación de herederos falsa — tribunal civil.",
            "Solicitud de Certificación de Balance y Relación de Movimientos — Scotiabank, Art. 56 Ley 183-02 Monetaria y Financiera + Reglamento de Protección al Usuario.",
            "Consulta de Información Financiera (sweep todos los bancos) — ProUsuario / SIB, Ley 107-13 (plazo máx. 60 días calendario).",
            "Duplicado de Certificado de Título + Declaratoria de Herederos + impuesto sucesoral DGII — vía ordinaria registral.",
        ]),
    ])

def tab6_assets():
    return build_text_section(6, "Bienes y estado de amenaza", [
        ("h2", "Matriz de activos"),
        ("table", [
            ["Activo", "Estado / amenaza"],
            ["Casa en Puñal (Los Vásquez, Santiago)",
             "Certificado de Título original retenido por Amarilys. Familia tramita <b>duplicado</b>. Policía + publicación en periódico completas (5-Dic-2025). Parcela, DC y folio pendientes de confirmar."],
            ["Vehículo Nissan",
             "<b>Traspaso fraudulento registrado en DGII el 20-Sep-2021</b>. Recuperación vía nulidad civil + medida cautelar para frenar reventa. Matrícula / chasis / año pendientes de confirmar."],
            ["Cuenta Scotiabank 302639 (RD)",
             "Cuenta viva al momento del fallecimiento. <b>Recibió los pagos de Seguro Social de EE.UU.</b> vía Bank One International (ABA 026009797 · SWIFT FNBCUS33) hacia Scotiabank (SWIFT NOSCDOSDA · onward-credit 1058909). Post-muerte: actividad desconocida. Alegato de Amarilys (“cuentas vacías”) no aceptado."],
            ["Seguro Social EE.UU. (Título II)",
             "SSN 584-52-1788. 2018 SSA-1099 muestra US$15,888 pagados (~US$1,324/mes). Probable US$1,300–1,400/mes a 2021. Amarilys admite tener la tarjeta física. Ruta: SSA-OIG + HHS-OIG + FBU Santo Domingo."],
            ["Medicare (EE.UU.)",
             "Beneficiario confirmado (carta HHS Medicare). Verificar reclamos Parte A/B/D posteriores al 13-Jun-2021."],
            ["Otras cuentas bancarias DR",
             "Desconocidas. Barrido a través de ProUsuario/SIB <b>Consulta de Información Financiera</b> por cédula 031-0513268-6 — gratis, hasta 60 días calendario."],
            ["Contenido de caja fuerte y documentos personales",
             "Caja fuerte encontrada <b>ABIERTA</b>. Cadena de custodia rota. Documentación mediante acta notarial de comprobación pendiente."],
        ]),
    ])

def tab7_banking_images():
    pages = []
    pages.append(build_tab_divider(7, "Evidencia bancaria y SSA",
        "Imágenes originales — 2018 SSA-1099, carta Medicare, instrucciones de envío del Seguro Social a Scotiabank"))
    pages.append(build_image_page(7,
        EVID / "ssa-banking" / "ssa-1099-delio-2018.jpeg",
        "SSA-1099 año fiscal 2018 — Delio A. Vásquez Vásquez",
        "Prueba oficial (IRS/SSA) de: (1) SSN 584-52-1788; (2) ingresos anuales por Seguro Social de EE.UU. de US$15,888 "
        "(~US$1,324/mes); (3) dirección de envío en Santiago RD. Base para estimar el flujo mensual que habría continuado "
        "tras el fallecimiento del 13-Jun-2021."))
    pages.append(build_image_page(7,
        EVID / "ssa-banking" / "medicare-card-letter.jpeg",
        "Carta de tarjeta Medicare — HHS · Delio A. Vásquez Vásquez",
        "Confirma que el causante era beneficiario Medicare. Relevante para verificar si hubo reclamos Parte A/B/D facturados "
        "contra su HIC con posterioridad al 13-Jun-2021 (línea separada ante HHS-OIG)."))
    pages.append(build_image_page(7,
        EVID / "ssa-banking" / "ssa-transfer-info-scotiabank-clearer.jpeg",
        "Instrucciones de pago SSA → Scotiabank — versión legible",
        "Ruta exacta del depósito federal: corresponsal Bank One International Corporation (NYC), ABA 026009797, SWIFT FNBCUS33, "
        "hacia Scotiabank (SWIFT NOSCDOSDA), onward-credit 1058909, cuenta de crédito final <b>302639</b>. "
        "Esta es la cuenta a auditar."))
    pages.append(build_image_page(7,
        EVID / "ssa-banking" / "ssa-transfer-info-scotiabank.jpeg",
        "Instrucciones de pago SSA → Scotiabank — copia adicional",
        "Copia complementaria para corroboración cruzada."))
    return pages

def tab8_nissan():
    return build_text_section(8, "Traspaso fraudulento del Nissan", [
        ("h2", "El hecho"),
        "El 20 de septiembre de 2021, la DGII registró el traspaso del vehículo Nissan del causante. <b>El causante había fallecido 3 meses antes</b>, el 13 de junio de 2021. La defunción oficial no se había declarado aún (se declaró el 10 de noviembre de 2021).",
        ("h2", "Por qué el traspaso es nulo"),
        ("bullet", [
            "Un fallecido no tiene capacidad jurídica para disponer de sus bienes (Art. 1108 Código Civil — consentimiento imposible).",
            "Cualquier firma atribuida al causante en esa fecha es forzosamente falsa o materialmente imposible.",
            "Cualquier endoso o poder “en vida” que se pretenda invocar debía haber sido ejercido antes del 13-Jun-2021; después es inejecutable.",
        ]),
        ("h2", "Ruta de recuperación (civil, sin penal)"),
        ("bullet", [
            "<b>Demanda en nulidad del traspaso + repetición</b> ante tribunal civil — pide al juez dejar sin efecto el acto y ordenar a DGII revertir la titularidad a la masa sucesoral.",
            "<b>Medida cautelar en el mismo acto</b> — prohibición de disponer o reinscribir el vehículo, notificada a DGII el mismo día para cerrar la puerta a un segundo traspaso.",
            "<b>Oficio a DGII y a la Policía (Dirección de Tránsito / AMET)</b> — notificar la litispendencia e impedir reinscripción administrativa.",
            "Tras sentencia favorable: reinscripción en nombre de Gisela como heredera única; luego venta.",
        ]),
        ("h2", "Datos pendientes antes de redactar la demanda"),
        ("bullet", [
            "Matrícula (placa).",
            "Número de chasis (VIN).",
            "Año y color.",
            "Copia del registro de traspaso del 20-Sep-2021 en DGII (quién aparece como comprador).",
            "Copia de la matrícula que la familia reportó como perdida (ya hay certificación policial + publicación).",
        ]),
    ])

def tab9_casa():
    return build_text_section(9, "Casa — título retenido y ruta del duplicado", [
        ("h2", "Situación"),
        "Amarilys retiene físicamente el Certificado de Título original. La familia persigue un <b>duplicado</b> (no una reivindicación del original) y la <b>Declaratoria de Herederos</b> para registrar la propiedad a nombre de Gisela.",
        ("h2", "Pasos ya completados"),
        ("bullet", [
            "Certificación de pérdida de título ante la Policía Nacional.",
            "Publicación de pérdida en periódico (5-Dic-2025).",
            "Trámites iniciales de casa firmados por Gisela el 14-Mar-2026.",
        ]),
        ("h2", "Pasos por completar"),
        ("bullet", [
            "Radicación en Registro de Títulos para el duplicado (confirmar número de expediente).",
            "Declaratoria de Herederos — aunque existe testamento, en la práctica registral DR se suele requerir una declaratoria judicial/notarial para inscribir.",
            "Registro de la herencia ante DGII y pago (o exención) del 3% de impuesto sucesoral.",
            "Emisión de nuevo Certificado de Título a nombre de Gisela Vásquez.",
            "Listado y venta del inmueble.",
        ]),
        ("h2", "Datos pendientes antes de afinar oposiciones/duplicado"),
        ("bullet", [
            "Matrícula registral.",
            "Designación catastral / parcela / DC / folio (formato moderno: matrícula única).",
            "Número de expediente del duplicado.",
            "Número de expediente DGII sucesoral.",
            "Copia de cualquier oposición presentada por la parte adversa.",
        ]),
    ])

def tab10_safe():
    return build_text_section(10, "Caja fuerte y documentos personales", [
        ("h2", "Lo que se sabe"),
        "La caja fuerte del causante fue encontrada <b>abierta</b> (reportado en abril de 2026). Amarilys admite tener la <b>tarjeta de Seguro Social</b> del causante. Altamente probable que también falten cédula, pasaporte y los papeles originales del vehículo.",
        ("h2", "Por qué importa probatoriamente"),
        ("bullet", [
            "La caja abierta, más la sustracción admitida de la tarjeta de SS, constituye patrón de apoderamiento de bienes muebles de la masa sucesoral.",
            "Sin un registro formal del estado de la caja y del inventario faltante, la adversa puede negar todo.",
        ]),
        ("h2", "Acciones inmediatas (no-penal)"),
        ("bullet", [
            "<b>Fotografías</b> de la caja en su estado actual (abierta, con o sin contenido remanente).",
            "<b>Acta notarial de comprobación</b> — un notario visita el inmueble, observa la caja y levanta acta; esto fija el hecho.",
            "<b>Inventario</b> de lo que permanece en el inmueble versus lo que falta, firmado por Davie y testigo.",
            "<b>Requerimiento formal a Amarilys</b> (vía abogado) de devolución inmediata de la tarjeta de SS y de cualquier documento del causante en su poder, con plazo de 5 días.",
        ]),
    ])

def tab11_open_questions():
    return build_text_section(11, "Preguntas abiertas para el abogado", [
        ("h2", "Para resolver en la próxima sesión con el abogado-notario actual"),
        ("bullet", [
            "Nombre y datos de contacto del abogado-notario actual (para nuestro propio registro).",
            "Alcance del Poder Especial ya otorgado por Gisela — ¿incluye banco, Registro de Títulos, ProUsuario/SIB, DGII, acciones civiles?",
            "¿Se contactó formalmente a Scotiabank? ¿Fecha y requerimiento exacto?",
            "¿Hay expediente sucesoral abierto en DGII? Número.",
            "¿El abogado anterior (Andrew) presentó oposiciones o medidas cautelares? (Las actuaciones no se transfieren automáticamente.)",
            "Estado del expediente de duplicado de título: fase actual, oposiciones recibidas.",
            "¿Hay contra-acción de Amarilys o de Luis José en curso?",
            "Matrícula/chasis/año del Nissan y copia del traspaso de 20-Sep-2021 ya en DGII.",
            "Parcela / DC / folio / matrícula registral exacta del inmueble.",
            "Cronograma estimado por hito (duplicado, declaratoria, sucesoral DGII, nuevo título, venta).",
        ]),
    ])

def tab12_sources():
    return build_text_section(12, "Documentos fuente — expediente completo", [
        ("h2", "Se anexan a continuación, en este mismo binder"),
        ("bullet", [
            "<b>Caso Herencia Delio — expediente base</b> (PDF original provisto por la familia).",
            "<b>Plan de acción — versión 1</b> (PDF preparado previamente).",
        ]),
        "Los tabs 7 ya incluyeron las imágenes originales de SSA-1099, Medicare y las instrucciones de envío SSA→Scotiabank. El export de WhatsApp con Davie está en el skill en texto plano y se puede anexar aparte si el abogado lo solicita (se recomienda acta notarial de comprobación del chat original para uso probatorio).",
    ])

# ---------- Build ----------

def main():
    parts = []

    parts.append(build_cover())

    parts.append(build_tab_divider(1, "Resumen ejecutivo"))
    parts.append(build_text_section(1, "Resumen ejecutivo", [
        "El causante, Delio Antonio Vásquez Vásquez, falleció el 13 de junio de 2021. Otorgó testamento auténtico que instituye a <b>Gisela Vásquez</b> como <b>heredera única</b>. Ese testamento rige la sucesión; cualquier otra reclamación es ajena a la masa.",
        "Su hermana <b>Amarilys Altagracia Vásquez</b> ha ejecutado una serie de actos que, en conjunto, configuran un patrón de apoderamiento indebido: declaración tardía de defunción (5 meses), traspaso fraudulento del Nissan tres meses después del fallecimiento, retención del Certificado de Título de la casa, reclutamiento de testigos extraños para una determinación de herederos fabricada, presunto cobro continuado del Seguro Social de EE.UU. del causante y sustracción de documentos personales de la caja fuerte.",
        "<b>Objetivo del cliente:</b> recuperar el dinero de la cuenta Scotiabank 302639 y de cualquier otra cuenta, recuperar el Nissan y vender la casa. Vía civil y administrativa primero; denuncia penal sólo como contingencia.",
        "<b>Estado:</b> Poder Especial de Gisela ya otorgado. Abogado-notario de la familia a cargo desde principios de abril de 2026 (datos pendientes de confirmar). Trámites de casa en curso desde el 14-Mar-2026.",
    ]))

    parts.append(build_tab_divider(2, "Causante y autoridad sucesoral"))
    parts.append(tab2_authority())

    parts.append(build_tab_divider(3, "Las partes"))
    parts.append(tab3_parties())

    parts.append(build_tab_divider(4, "Cronología del caso"))
    parts.append(tab4_timeline())

    parts.append(build_tab_divider(5, "Patrón de fraude"))
    parts.append(tab5_fraud_pattern())

    parts.append(build_tab_divider(6, "Bienes y estado de amenaza"))
    parts.append(tab6_assets())

    parts.extend(tab7_banking_images())

    parts.append(build_tab_divider(8, "Traspaso fraudulento del Nissan"))
    parts.append(tab8_nissan())

    parts.append(build_tab_divider(9, "Casa — título y duplicado"))
    parts.append(tab9_casa())

    parts.append(build_tab_divider(10, "Caja fuerte y documentos personales"))
    parts.append(tab10_safe())

    parts.append(build_tab_divider(11, "Preguntas abiertas para el abogado"))
    parts.append(tab11_open_questions())

    parts.append(build_tab_divider(12, "Documentos fuente"))
    parts.append(tab12_sources())

    # Append the two existing source PDFs if they exist.
    caso = EVID / "caso-herencia-delio.pdf"
    plan = EVID / "estate-plan-of-action.pdf"
    if caso.exists(): parts.append(caso)
    if plan.exists(): parts.append(plan)

    # Merge
    writer = PdfWriter()
    for p in parts:
        reader = PdfReader(str(p))
        for page in reader.pages:
            writer.add_page(page)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "wb") as f:
        writer.write(f)
    print(f"WROTE {OUT}  pages={len(writer.pages)}  parts={len(parts)}")

if __name__ == "__main__":
    main()

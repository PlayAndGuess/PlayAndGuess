
from pathlib import Path
import pandas as pd
import qrcode
from PIL import Image, ImageDraw, ImageFont
from fpdf import FPDF

def crear_index_html(path, youtube_id):
    html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Play and Guess</title>
  <style>
    body {{
      background-color: #000;
      color: #fff;
      font-family: Arial, sans-serif;
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      height: 100vh;
    }}

    #video-container {{
      position: relative;
      width: 90vw;
      max-width: 800px;
      aspect-ratio: 16 / 9;
      overflow: hidden;
      border-radius: 12px;
      box-shadow: 0 0 20px rgba(0, 0, 0, 0.7);
    }}

    iframe {{
      width: 100%;
      height: 100%;
      border: none;
      visibility: hidden;
    }}

    #overlay {{
      position: absolute;
      top: 0;
      left: 0;
      width: 100%;
      height: 100%;
      background-color: #000;
      color: #fff;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 1.5em;
      z-index: 2;
      pointer-events: all;
      cursor: pointer;
    }}

    h1 {{
      margin-bottom: 20px;
      font-size: 2rem;
    }}

    .msg {{
      margin-top: 20px;
      font-size: 1.2em;
      color: #aaa;
    }}
  </style>
</head>
<body>
  <h1>🎧 Play and Guess</h1>
  <div id="video-container">
    <div id="overlay">Haz clic para reproducir</div>
    <iframe
      id="player"
      src=""
      allow="autoplay"
      allowfullscreen>
    </iframe>
  </div>
  <div class="msg">Escucha la canción. ¿Puedes adivinar el año?</div>

  <script>
    const overlay = document.getElementById("overlay");
    const iframe = document.getElementById("player");

    overlay.addEventListener("click", function () {{
      iframe.src =
        "https://www.youtube-nocookie.com/embed/{youtube_id}?autoplay=1&controls=0&rel=0&modestbranding=1";
      overlay.innerText = "Reproduciendo...";
      overlay.style.cursor = "default";
      overlay.style.pointerEvents = "none";
    }});
  </script>
</body>
</html>
"""
    with open(path, "w", encoding="utf-8") as f:
        f.write(html.strip())

def crear_qr(path, full_url):
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(full_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(path)

def crear_imagen_info(ruta_salida, titulo, cantante, anio, id_cancion):
    ancho, alto = 600, 400
    fondo = (0, 0, 0)
    texto_color = (255, 255, 255)
    imagen = Image.new("RGB", (ancho, alto), fondo)
    draw = ImageDraw.Draw(imagen)

    try:
        fuente = ImageFont.truetype("arial.ttf", 28)
        fuente_id = ImageFont.truetype("arial.ttf", 16)
    except IOError:
        fuente = ImageFont.load_default()
        fuente_id = ImageFont.load_default()

    lineas = [
        f"Título: {titulo}",
        f"Cantante: {cantante}",
        f"Año: {anio}"
    ]

    y_texto = 100
    for linea in lineas:
        bbox = draw.textbbox((0, 0), linea, font=fuente)
        ancho_texto = bbox[2] - bbox[0]
        alto_texto = bbox[3] - bbox[1]
        x = (ancho - ancho_texto) / 2
        draw.text((x, y_texto), linea, font=fuente, fill=texto_color)
        y_texto += alto_texto + 20

    id_text = f"ID: {id_cancion}"
    bbox_id = draw.textbbox((0, 0), id_text, font=fuente_id)
    ancho_id = bbox_id[2] - bbox_id[0]
    x_id = (ancho - ancho_id) / 2
    y_id = alto - 40
    draw.text((x_id, y_id), id_text, font=fuente_id, fill=texto_color)

    imagen.save(ruta_salida)

def generar_pdfs(base_path):
    pdf_output = base_path / "pdfs"
    pdf_output.mkdir(exist_ok=True)

    for cancion_dir in sorted(base_path.iterdir()):
        if cancion_dir.is_dir() and cancion_dir.name.startswith("cancion"):
            info_path = cancion_dir / "info.png"
            qr_path = cancion_dir / "qr.png"
            if info_path.exists() and qr_path.exists():
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=16)
                pdf.cell(0, 10, cancion_dir.name.replace("cancion", "Canción "), ln=True, align="C")
                pdf.image(str(info_path), x=30, y=25, w=150)
                pdf.image(str(qr_path), x=85, y=140, w=40)
                pdf.output(str(pdf_output / f"{cancion_dir.name}.pdf"))

def procesar_excel(nombre_excel, nombre_lista, dominio_base):
    df = pd.read_excel(nombre_excel)
    output_root = Path("output") / nombre_lista
    output_root.mkdir(parents=True, exist_ok=True)

    for index, row in df.iterrows():
        id_cancion = str(row["ID"]).zfill(2)
        folder_name = f"cancion{id_cancion}"
        folder_path = output_root / folder_name
        folder_path.mkdir(parents=True, exist_ok=True)

        crear_index_html(folder_path / "index.html", row["Código YouTube"])
        full_url = f"{dominio_base}/output/{nombre_lista}/{folder_name}/"
        crear_qr(folder_path / "qr.png", full_url)
        crear_imagen_info(
            ruta_salida=folder_path / "info.png",
            titulo=row["Título de la Canción"],
            cantante=row["Cantante"],
            anio=row["Año"],
            id_cancion=id_cancion
        )

    index_html = output_root / "index.html"
    with open(index_html, "w", encoding="utf-8") as idx:
        idx.write("<!DOCTYPE html>\n<html lang='es'>\n<head>\n")
        idx.write("<meta charset='UTF-8'>\n<title>Lista de Canciones</title>\n</head>\n<body>\n")
        idx.write(f"<h1>Lista: {nombre_lista}</h1>\n<ul>\n")

        for _, row in df.iterrows():
            id_cancion = str(row["ID"]).zfill(2)
            folder = f"cancion{id_cancion}"
            titulo = row["Título de la Canción"]
            artista = row["Cantante"]
            idx.write(f"<li><a href='./{folder}/index.html' target='_blank'>{titulo} – {artista}</a></li>\n")

        idx.write("</ul>\n</body>\n</html>")

    return output_root

if __name__ == "__main__":
    print("🎵 Generador de tarjetas para Play & Guess 🎵\n")
    nombre_excel = input("📄 Nombre del archivo Excel (.xlsx): ").strip()
    nombre_lista = input("📁 Nombre de la lista (carpeta de salida): ").strip()
    dominio_base = input("🌐 Dominio base para QR (sin '/' final): ").strip()

    ruta_final = procesar_excel(nombre_excel, nombre_lista, dominio_base)
    print(f"\n✅ Archivos generados en: {ruta_final}")

    generar = input("📄 ¿Deseas generar PDFs individuales por canción? (s/n): ").strip().lower()
    if generar == "s":
        generar_pdfs(ruta_final)
        print("🖨️ PDFs generados en:", ruta_final / "pdfs")

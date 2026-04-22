from flask import Flask, request, jsonify, send_from_directory
import os
import uuid
from datetime import datetime, timedelta

app = Flask(__name__)

# Obtenemos la ruta donde guardar las imágenes, según docker-compose
UPLOAD_DIR = os.environ.get('UPLOAD_DIR', '/app/data/uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)


images_db = {}  # La "base de datos" (un diccionario en memoria)
shares_db = {}  # La "base de datos" para los enlaces compartidos

# --- ENDPOINT 1: SUBIR IMAGEN ---
@app.route('/api/upload_image', methods=['POST'])
def upload_image():
    # Comprobamos si en la petición nos han enviado el archivo 'image'
    if 'image' not in request.files:
        return jsonify({"error": "No se ha enviado ninguna imagen"}), 400
    
    file = request.files['image']
    
    # Si el usuario no seleccionó ningún archivo
    if file.filename == '':
        return jsonify({"error": "El nombre del archivo está vacío"}), 400
    
    if file:
        # Generamos un identificador único
        image_id = str(uuid.uuid4())
        
        # Creamos el nombre con el que lo guardaremos: ID + extensión original
        extension = file.filename.split('.')[-1]
        filename = f"{image_id}.{extension}"
        filepath = os.path.join(UPLOAD_DIR, filename)
        
        # Guardamos el archivo físicamente en la carpeta
        file.save(filepath)
        
        # Guardamos la info en nuestra "base de datos"
        images_db[image_id] = {
            "image_id": image_id,
            "filename": filename,
            "original_name": file.filename
        }
        
        print(f"Imagen guardada con éxito: {filename}") 
        
        return jsonify({"message": "Uploaded", "image_id": image_id}), 200

# --- ENDPOINT 2: LISTAR IMÁGENES ---
@app.route('/api/list_images', methods=['GET'])
def list_images():
    items = []
    for img_id, img_data in images_db.items():
        items.append({
            "image_id": img_id,
            "url": f"/uploads/{img_data['filename']}"
        })
    return jsonify({"items": items}), 200

# --- ENDPOINT 3: ANALIZAR IMAGEN ---
@app.route('/api/analyse_image', methods=['POST'])
def analyse_image():
    # Recibimos el JSON de la petición 
    data = request.get_json()
    
    if not data or 'image_id' not in data:
        return jsonify({"error": "Falta el image_id"}), 400
        
    image_id = data['image_id']
    
    # Comprobamos si la imagen existe en nuestro diccionario
    if image_id not in images_db:
        return jsonify({"error": "Imagen no encontrada"}), 404
        
    # Obtenemos los datos de la imagen y su ruta en el disco duro
    img_data = images_db[image_id]
    filepath = os.path.join(UPLOAD_DIR, img_data['filename'])
    
    # Calculamos el tamaño real del archivo
    try:
        size_bytes = os.path.getsize(filepath)
        size_kb = round(size_bytes / 1024, 2)
    except OSError:
        size_kb = 0
        
    real_analysis = {
        "original_name": img_data['original_name'],
        "size_kb": size_kb,
        "status": "Metadatos reales obtenidos con éxito"
    }
    
    return jsonify({
        "image_id": image_id,
        "analysis": real_analysis
    }), 200

# --- ENDPOINT 4: GENERAR ENLACE COMPARTIDO ---
@app.route('/api/share_image', methods=['POST'])
def share_image():
    data = request.get_json()
    if not data or 'image_id' not in data:
        return jsonify({"error": "Falta el image_id"}), 400
        
    image_id = data['image_id']
    if image_id not in images_db:
        return jsonify({"error": "Imagen no encontrada"}), 404
        
    # Generamos un token aleatorio
    token = uuid.uuid4().hex
    
    # Calculamos la hora actual + 10 minutos
    expires_at = datetime.now() + timedelta(minutes=10)
    
    # Guardamos el token en nuestra BD
    shares_db[token] = {
        "image_id": image_id,
        "expires_at": expires_at
    }
    
    url = f"http://localhost:8000/s/{token}"
    
    return jsonify({
        "token": token,
        "url": url,
        "expires_at": expires_at.isoformat()
    }), 200

# --- ENDPOINT 5: VER IMAGEN COMPARTIDA (PÁGINA PÚBLICA) ---
@app.route('/s/<token>', methods=['GET'])
def shared_page(token):
    if token not in shares_db:
        return "<h1>Error 404: Enlace no válido o no existe</h1>", 404
        
    share_info = shares_db[token]
    
    # Comprobamos si la fecha actual ya superó la fecha de expiración
    if datetime.now() > share_info['expires_at']:
        return "<h1>Error 410: El enlace ha caducado (pasaron los 10 minutos)</h1>", 410
        
    # Si es válido, sacamos la imagen asociada
    img_data = images_db[share_info['image_id']]
    image_url = f"http://localhost:3000/uploads/{img_data['filename']}"
    
    # Generamos el HTML con las etiquetas Open Graph (OG) pedidas
    html_content = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Imagen Compartida</title>
        <meta property="og:title" content="Imagen compartida vía LogMeal">
        <meta property="og:image" content="{image_url}">
        <meta property="og:description" content="Esta imagen ha sido compartida contigo de forma segura.">
    </head>
    <body style="text-align: center; font-family: sans-serif; padding: 40px; background-color: #f9f9f9;">
        <h2>¡Alguien ha compartido una imagen contigo!</h2>
        <p>Este enlace dejará de funcionar pronto.</p>
        <img src="{image_url}" style="max-width: 600px; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.1);">
    </body>
    </html>
    """
    return html_content, 200

# --- ENDPOINT 6: SERVIR ARCHIVOS ESTÁTICOS (IMÁGENES) ---
@app.route('/uploads/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(UPLOAD_DIR, filename)
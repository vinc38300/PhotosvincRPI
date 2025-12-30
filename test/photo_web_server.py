#!/usr/bin/env python3
"""
Serveur HTTP pour partager les photos via QR Code
Se lance automatiquement en arrière-plan
"""

from http.server import HTTPServer, SimpleHTTPRequestHandler
import threading
import socket
from pathlib import Path
import logging
import os

logger = logging.getLogger(__name__)


class PhotoHTTPHandler(SimpleHTTPRequestHandler):
    """Handler HTTP personnalisé pour servir les photos"""
    
    def __init__(self, *args, photo_directory=None, **kwargs):
        self.photo_dir = photo_directory or str(Path.home() / "Photos_photovinc")
        super().__init__(*args, directory=self.photo_dir, **kwargs)
    
    def log_message(self, format, *args):
        """Override pour logger proprement"""
        logger.info(f"HTTP: {format % args}")
    
    def end_headers(self):
        """Ajoute des headers CORS pour permettre le téléchargement"""
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        super().end_headers()
    
    def do_GET(self):
        """Gère les requêtes GET"""
        if self.path.startswith('/photo/'):
            filename = self.path[7:]
            filepath = Path(self.photo_dir) / filename
            
            if filepath.exists() and filepath.is_file():
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
                self.end_headers()
                
                with open(filepath, 'rb') as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "Photo non trouvée")
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.end_headers()
            
            html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>photovinc - Partage de Photos</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 50px auto;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-align: center;
        }
        .container {
            background: rgba(255, 255, 255, 0.1);
            padding: 40px;
            border-radius: 20px;
            backdrop-filter: blur(10px);
        }
        h1 {
            font-size: 3em;
            margin-bottom: 20px;
        }
        .emoji {
            font-size: 4em;
            margin: 20px 0;
        }
        p {
            font-size: 1.3em;
            line-height: 1.6;
        }
        .info {
            background: rgba(255, 255, 255, 0.2);
            padding: 20px;
            border-radius: 10px;
            margin-top: 30px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="emoji">📸</div>
        <h1>photovinc</h1>
        <p>Serveur de partage de photos</p>
        <div class="info">
            <p>Pour télécharger une photo :</p>
            <p><strong>Scannez le QR code</strong> affiché sur l'écran du photovinc</p>
            <p>Ou accédez à : <code>/photo/nom_fichier.jpg</code></p>
        </div>
    </div>
</body>
</html>
            """
            
            self.wfile.write(html.encode('utf-8'))


class PhotoWebServer:
    """Serveur web pour partager les photos"""
    
    def __init__(self, port=8000, photo_directory=None):
        self.port = port
        self.photo_dir = photo_directory or str(Path.home() / "Photos_photovinc")
        self.server = None
        self.thread = None
        self.running = False
        Path(self.photo_dir).mkdir(exist_ok=True)
    
    def get_local_ip(self):
        """Obtient l'adresse IP locale"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            try:
                return socket.gethostbyname(socket.gethostname())
            except:
                return "127.0.0.1"
    
    def get_server_url(self):
        """Retourne l'URL du serveur"""
        ip = self.get_local_ip()
        return f"http://{ip}:{self.port}"
    
    def start(self):
        """Démarre le serveur en arrière-plan"""
        if self.running:
            logger.warning("Serveur déjà démarré")
            return False

        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                def handler(*args, **kwargs):
                    PhotoHTTPHandler(*args, photo_directory=self.photo_dir, **kwargs)
                
                self.server = HTTPServer(('0.0.0.0', self.port), handler)
                
                self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
                self.thread.start()
                
                self.running = True
                logger.info(f"Serveur web démarré sur {self.get_server_url()}")
                return True
            
            except OSError as e:
                if e.errno == 98:
                    self.port += 1
                    logger.warning(f"Port occupé, essai sur port {self.port}")
                    continue
                raise
            except Exception as e:
                logger.error(f"Erreur démarrage serveur: {e}")
                return False
        
        logger.error(f"Impossible de démarrer le serveur après {max_attempts} tentatives")
        return False
    
    def stop(self):
        """Arrête le serveur"""
        if not self.running:
            return
        
        try:
            if self.server:
                self.server.shutdown()
                self.server = None
            
            self.running = False
            logger.info("Serveur web arrêté")
        
        except Exception as e:
            logger.error(f"Erreur arrêt serveur: {e}")
    
    def is_running(self):
        """Vérifie si le serveur tourne"""
        return self.running
    
    def get_status(self):
        """Retourne le statut du serveur"""
        return {
            'running': self.running,
            'url': self.get_server_url() if self.running else None,
            'port': self.port,
            'photo_dir': self.photo_dir,
            'local_ip': self.get_local_ip()
        }


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    server = PhotoWebServer(port=8000)
    
    if server.start():
        print(f"\n{'='*50}")
        print(f"Serveur démarré avec succès !")
        print(f"URL: {server.get_server_url()}")
        print(f"Dossier: {server.photo_dir}")
        print(f"{'='*50}\n")
        
        try:
            input("Appuyez sur Entrée pour arrêter le serveur...\n")
        except KeyboardInterrupt:
            pass
        
        server.stop()
        print("Serveur arrêté.")
    else:
        print("Échec démarrage serveur")

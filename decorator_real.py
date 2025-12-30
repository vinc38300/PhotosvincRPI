 
#!/usr/bin/env python3
"""
Decorator Plugin - CODE FONCTIONNEL
Extrait de photovinc_complet5.py avec PostcardDecorator
"""

from plugin_manager import PluginInterface, PluginConfig
from typing import Dict, List, Any
from PIL import Image, ImageDraw, ImageFont, ImageEnhance, ImageFilter
from datetime import datetime
from pathlib import Path
import logging
import random

logger = logging.getLogger(__name__)


class DecoratorPluginReal(PluginInterface):
    """Plugin de décoration avec le vrai code"""
    
    def __init__(self, config: PluginConfig):
        super().__init__(config)
        self.available_styles = []
    
    def initialize(self) -> bool:
        """Initialise le décorateur"""
        logger.info("Initialisation DecoratorPlugin")
        self.available_styles = ["polaroid", "vintage", "stamp", "fete", "normal"]
        self._initialized = True
        return True
    
    def shutdown(self):
        """Arrête le décorateur"""
        logger.info("Arrêt DecoratorPlugin")
        self._initialized = False
    
    def get_status(self) -> Dict[str, Any]:
        return {
            "initialized": self._initialized,
            "available_styles": self.available_styles
        }
    
    def get_capabilities(self) -> List[str]:
        return ["apply_style", "create_montage", "create_logo"]
    
    def create_logo(self):
        """Crée le logo avec personnage (code original)"""
        logo = Image.new('RGBA', (400, 400), (0, 0, 0, 0))
        draw = ImageDraw.Draw(logo)
        
        skin = (255, 220, 177)
        shirt = (52, 152, 219)
        pants = (44, 62, 80)
        flash = (255, 255, 100)
        camera = (50, 50, 50)
        
        # Caméra
        draw.rectangle([140, 30, 260, 90], fill=camera, outline=(30, 30, 30), width=3)
        draw.ellipse([170, 45, 230, 105], fill=(80, 80, 80), outline=(100, 100, 100), width=3)
        draw.ellipse([185, 60, 215, 90], fill=(200, 200, 255))
        
        # Flash
        for i in range(5):
            draw.line([200, 35, 180-i*8, 10], fill=flash, width=3)
            draw.line([200, 35, 220+i*8, 10], fill=flash, width=3)
        draw.rectangle([195, 25, 205, 35], fill=(255, 0, 0))
        
        # Personnage
        center_x, center_y = 200, 180
        draw.ellipse([center_x-40, center_y-40, center_x+40, center_y+40], 
                    fill=skin, outline=(200, 180, 140), width=2)
        
        # Yeux
        draw.arc([center_x-25, center_y-15, center_x-10, center_y], 
                start=0, end=180, fill=(50, 50, 50), width=3)
        draw.arc([center_x+10, center_y-15, center_x+25, center_y], 
                start=0, end=180, fill=(50, 50, 50), width=3)
        
        # Sourire
        draw.arc([center_x-30, center_y-5, center_x+30, center_y+25], 
                start=0, end=-180, fill=(50, 50, 50), width=4)
        
        # Corps
        draw.polygon([
            (center_x, center_y+40),
            (center_x-50, center_y+70),
            (center_x-45, center_y+150),
            (center_x+45, center_y+150),
            (center_x+50, center_y+70)
        ], fill=shirt, outline=(41, 128, 185), width=2)
        
        # Bras gauche
        draw.ellipse([center_x-80, center_y+50, center_x-50, center_y+80], 
                    fill=shirt, outline=(41, 128, 185), width=2)
        draw.ellipse([center_x-95, center_y+35, center_x-70, center_y+60], 
                    fill=skin, outline=(200, 180, 140), width=2)
        
        # Bras droit
        draw.ellipse([center_x+50, center_y+80, center_x+80, center_y+110], 
                    fill=shirt, outline=(41, 128, 185), width=2)
        draw.ellipse([center_x+75, center_y+100, center_x+100, center_y+125], 
                    fill=skin, outline=(200, 180, 140), width=2)
        
        # Jambes
        draw.polygon([
            (center_x-40, center_y+150),
            (center_x-30, center_y+250),
            (center_x-10, center_y+250),
            (center_x-5, center_y+150)
        ], fill=pants, outline=(35, 50, 63), width=2)
        
        draw.polygon([
            (center_x+5, center_y+150),
            (center_x+10, center_y+250),
            (center_x+30, center_y+250),
            (center_x+40, center_y+150)
        ], fill=pants, outline=(35, 50, 63), width=2)
        
        # Chaussures
        draw.ellipse([center_x-35, center_y+245, center_x-5, center_y+265], 
                    fill=(200, 50, 50), outline=(150, 40, 40), width=2)
        draw.ellipse([center_x+5, center_y+245, center_x+35, center_y+265], 
                    fill=(200, 50, 50), outline=(150, 40, 40), width=2)
        
        # Étoiles
        stars = [(50, 150), (350, 150), (100, 280), (300, 280)]
        for sx, sy in stars:
            for angle in range(0, 360, 72):
                import math
                x1 = sx + 15 * math.cos(math.radians(angle))
                y1 = sy + 15 * math.sin(math.radians(angle))
                draw.line([sx, sy, x1, y1], fill=(255, 215, 0), width=3)
        
        # Texte
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "CHEESE!"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text(((400 - text_width) // 2, 310), text, fill=(255, 100, 100), font=font)
        
        return logo
    
    def create_vintage_border(self, img, border_width=30):
        """Bordure vintage"""
        width, height = img.size
        new_img = Image.new('RGB', 
            (width + border_width*2, height + border_width*2), 
            '#f5f5dc')
        new_img.paste(img, (border_width, border_width))
        return new_img
    
    def add_stamp_mark(self, img):
        """Ajoute un tampon"""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        stamp_x = width - 200
        stamp_y = 50
        stamp_radius = 80
        
        for i in range(3):
            draw.ellipse(
                [stamp_x-stamp_radius+i, stamp_y-stamp_radius+i,
                 stamp_x+stamp_radius-i, stamp_y+stamp_radius-i],
                outline=(180, 50, 50),
                width=2
            )
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
        except:
            font = font_small = ImageFont.load_default()
        
        date = datetime.now().strftime("%d.%m.%Y")
        draw.text((stamp_x-50, stamp_y-25), "SOUVENIR", fill=(180, 50, 50), font=font)
        draw.text((stamp_x-30, stamp_y+5), date, fill=(180, 50, 50), font=font_small)
        
        return img
    
    def add_party_border(self, img):
        """Bordure de fête"""
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        party_colors = [
            (255, 107, 107), (255, 195, 18), (72, 219, 251),
            (255, 121, 198), (162, 155, 254), (129, 236, 236), (253, 203, 110)
        ]
        
        border_width = 15
        
        for i in range(border_width):
            color = party_colors[i % len(party_colors)]
            draw.rectangle([i, i, width-1-i, height-1-i], outline=color, width=2)
        
        random.seed(42)
        
        # Confettis haut et bas
        for _ in range(30):
            x = random.randint(20, width - 20)
            y = random.randint(5, 40)
            color = random.choice(party_colors)
            size = random.randint(3, 8)
            shape = random.choice(['circle', 'rect', 'triangle'])
            
            if shape == 'circle':
                draw.ellipse([x, y, x+size, y+size], fill=color)
            elif shape == 'rect':
                draw.rectangle([x, y, x+size, y+size], fill=color)
            else:
                draw.polygon([(x, y+size), (x+size//2, y), (x+size, y+size)], fill=color)
        
        # Ballons
        balloon_positions = [
            (30, 30), (width - 50, 30), (40, height - 60), (width - 60, height - 60)
        ]
        
        for bx, by in balloon_positions:
            color = random.choice(party_colors)
            draw.ellipse([bx, by, bx+25, by+35], fill=color, outline=(0,0,0), width=1)
            draw.line([bx+12, by+35, bx+12, by+50], fill=(100,100,100), width=2)
        
        return img
    
    def create_polaroid_style(self, img, title=""):
        """Style Polaroid"""
        width, height = img.size
        
        top_margin = 40
        side_margin = 40
        bottom_margin = 120
        
        new_width = width + side_margin * 2
        new_height = height + top_margin + bottom_margin
        
        polaroid = Image.new('RGB', (new_width, new_height), '#f5f5dc')
        polaroid.paste(img, (side_margin, top_margin))
        
        draw = ImageDraw.Draw(polaroid)
        for i in range(5):
            alpha = 50 - i*10
            draw.rectangle([side_margin+i, top_margin+i, 
                          new_width-side_margin-i, new_height-bottom_margin-i],
                         outline=(alpha, alpha, alpha))
        
        if not title:
            title = datetime.now().strftime("%d/%m/%Y")
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (new_width - text_width) // 2
        text_y = new_height - bottom_margin + 30
        
        draw.text((text_x, text_y), title, fill=(60, 60, 60), font=font)
        
        return polaroid
    
    def add_vintage_filter(self, img):
        """Filtre vintage sépia"""
        sepia_img = img.convert('RGB')
        pixels = sepia_img.load()
        width, height = sepia_img.size
        
        for py in range(height):
            for px in range(width):
                r, g, b = pixels[px, py]
                
                tr = int(0.393 * r + 0.769 * g + 0.189 * b)
                tg = int(0.349 * r + 0.686 * g + 0.168 * b)
                tb = int(0.272 * r + 0.534 * g + 0.131 * b)
                
                pixels[px, py] = (min(tr, 255), min(tg, 255), min(tb, 255))
        
        enhancer = ImageEnhance.Color(sepia_img)
        return enhancer.enhance(0.8)
    
    def create_film_strip(self, images, style, output_path):
        """Crée un montage de 4 photos (code original)"""
        if len(images) < 4:
            logger.error("Pas assez de photos pour le montage")
            return False
        
        strip_width = 1772
        strip_height = 1181
        
        if style == "vintage":
            film = Image.new('RGB', (strip_width, strip_height), '#f5f5dc')
        elif style == "polaroid":
            film = Image.new('RGB', (strip_width, strip_height), '#e8e8e0')
        elif style == "fete":
            film = Image.new('RGB', (strip_width, strip_height), '#ffffff')
        else:
            film = Image.new('RGB', (strip_width, strip_height), '#ffffff')
        
        draw = ImageDraw.Draw(film)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
            font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
        except:
            font = font_small = ImageFont.load_default()
        
        # Titre
        title = "PHOTOVINC"
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        title_color = (139, 90, 60) if style == "vintage" else (52, 73, 94)
        draw.text(((strip_width - text_width) // 2, 10), title, fill=title_color, font=font)
        
        # Date
        date_text = datetime.now().strftime("%d/%m/%Y")
        bbox_date = draw.textbbox((0, 0), date_text, font=font_small)
        date_width = bbox_date[2] - bbox_date[0]
        draw.text(((strip_width - date_width) // 2, 45), date_text, fill=(127, 140, 141), font=font_small)
        
        # Positions des photos
        photo_width = 850
        photo_height = 530
        padding = 12
        start_y = 75
        
        total_width_photos = photo_width * 2 + padding
        start_x = (strip_width - total_width_photos) // 2
        
        positions = [
            (start_x, start_y),
            (start_x + photo_width + padding, start_y),
            (start_x, start_y + photo_height + padding),
            (start_x + photo_width + padding, start_y + photo_height + padding)
        ]
        
        # Coller les photos
        for i, (img_path, (x, y)) in enumerate(zip(images[:4], positions)):
            try:
                img = Image.open(img_path)
                
                if style == "vintage":
                    img = self.add_vintage_filter(img)
                
                img.thumbnail((photo_width, photo_height), Image.Resampling.LANCZOS)
                
                paste_x = x + (photo_width - img.width) // 2
                paste_y = y + (photo_height - img.height) // 2
                
                border = 4
                border_color = (245, 245, 220) if style == "polaroid" else (52, 73, 94)
                
                draw.rectangle([paste_x - border, paste_y - border,
                              paste_x + img.width + border, paste_y + img.height + border],
                             fill=border_color)
                
                film.paste(img, (paste_x, paste_y))
                
                draw.text((x + 8, y + 8), f"{i+1}", fill=(231, 76, 60), font=font_small)
                
            except Exception as e:
                logger.error(f"Erreur photo {i+1}: {e}")
        
        if style == "stamp":
            film = self.add_stamp_mark(film)
        elif style == "fete":
            film = self.add_party_border(film)
        
        try:
            film.save(output_path, quality=95)
            logger.info(f"Montage créé: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Erreur sauvegarde montage: {e}")
            return False
    
    def apply_style(self, input_path, style, output_path):
        """Applique un style à une photo"""
        if not self._initialized:
            return False
        
        try:
            img = Image.open(input_path)
            img.thumbnail((1600, 1200), Image.Resampling.LANCZOS)
            
            if style == "polaroid":
                styled = self.create_polaroid_style(img)
            elif style == "vintage":
                styled = self.add_vintage_filter(img)
                styled = self.create_vintage_border(styled)
            elif style == "stamp":
                styled = self.create_vintage_border(img)
                styled = self.add_stamp_mark(styled)
            elif style == "fete":
                styled = self.add_party_border(img)
            else:
                styled = img
            
            styled.save(output_path, quality=95)
            logger.info(f"Style appliqué: {style} -> {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Erreur application style: {e}")
            return False


def register_real_decorator(manager):
    """Enregistre le vrai décorateur"""
    from plugin_manager import PluginConfig
    
    if "decorator" not in manager.plugin_configs:
        manager.plugin_configs["decorator"] = PluginConfig(
            name="decorator",
            enabled=True,
            priority=3,
            settings={}
        )
        manager.save_config()
    
    manager.register_plugin("decorator", DecoratorPluginReal)
    logger.info("Vrai plugin Decorator enregistré")

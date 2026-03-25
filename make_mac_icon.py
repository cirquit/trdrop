import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QPainter, QPainterPath, QImage, QPixmap
from PyQt6.QtCore import Qt, QSize

def main():
    app = QApplication(sys.argv)
    
    icon_path = "trdrop_logo_new.png"
    img = QImage(icon_path)
    
    if img.isNull():
        print(f"Failed to load {icon_path}.")
        return
        
    pix = QPixmap.fromImage(img)
    
    w, h = pix.width(), pix.height()
    if w < 512:
        pix = pix.scaled(512, 512, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        w, h = 512, 512

    pad = int(w * 0.1)
    inner_w = w - 2 * pad
    inner_pix = pix.scaled(inner_w, inner_w, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
    
    canvas = QImage(w, h, QImage.Format.Format_ARGB32_Premultiplied)
    canvas.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(canvas)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
    painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
    
    path = QPainterPath()
    radius = inner_w * 0.225
    path.addRoundedRect(float(pad), float(pad), float(inner_w), float(inner_w), radius, radius)
    
    painter.setClipPath(path)
    painter.drawPixmap(pad, pad, inner_pix)
    painter.end()
    
    canvas.save("trdrop_mac.png")
    print("trdrop_mac.png created successfully.")

if __name__ == "__main__":
    main()

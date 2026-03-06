from flask import Flask, render_template, request, redirect, send_from_directory
from werkzeug.exceptions import RequestEntityTooLarge
import os

from PIL import Image

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # 16MB
app.config['ALLOWED_EXTENSIONS'] = [ '.png', '.jpg', '.jpeg']

app.config['RESULTS_FOLDER'] = 'results/'

CANVAS_SIZE = (1080, 1440)

def resize_and_crop_cover(image, target_size):
    target_w, target_h = target_size
    img_w, img_h = image.size

    # Skalierungsfaktor berechnen (größeren nehmen!)
    scale = max(target_w / img_w, target_h / img_h)

    new_w = int(img_w * scale)
    new_h = int(img_h * scale)

    # Bild skalieren
    image = image.resize((new_w, new_h), Image.LANCZOS)

    # Mittig zuschneiden
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    right = left + target_w
    bottom = top + target_h

    return image.crop((left, top, right, bottom))

# Test Function
@app.route('/test')
def hello_world():  # put application's code here
    return 'Test erfolgreich!'

# Standart Function
@app.route('/')
def index():
    return render_template('index.html')

# Upload Function
@app.route('/upload', methods=['POST'])
def upload():
    try:
        file = request.files['file']
        extension = os.path.splitext(file.filename)[1].lower()

        if file:

            if extension not in app.config['ALLOWED_EXTENSIONS']:
                return 'Ausgewählte Datei ist kein Bild.'

            file.save(os.path.join(
                app.config['UPLOAD_FOLDER'],
                'background.jpg'
            ))

            selection = request.form['selection']

            # Bilder laden
            if selection == "chirurgisch":
                overlay = Image.open("overlays/Vorlage_Chirurgisch.png").convert("RGBA")
            elif selection == "internistisch":
                overlay = Image.open("overlays/Vorlage_Internistisch.png").convert("RGBA")
            elif selection == "neurologisch":
                overlay = Image.open("overlays/Vorlage_Neurologisch.png").convert("RGBA")
            elif selection == "reanimation":
                overlay = Image.open("overlays/Vorlage_Reanimation.png").convert("RGBA")
            else:
                overlay = Image.open("overlays/Vorlage_Verkehrsunfall.png").convert("RGBA")

            background = Image.open("uploads/background.jpg").convert("RGBA")

            # Background passend machen
            background = resize_and_crop_cover(background, CANVAS_SIZE)

            # Kombinieren
            result = Image.alpha_composite(background, overlay)

            # Speichern
            result.save("results/Einsatz_Bild.png")

    except RequestEntityTooLarge:
        return 'Bild ist größer als das Limit von 16MB.'

    return redirect('/preview')

    #Download Browser
    #return send_from_directory(app.config['RESULTS_FOLDER'], 'Einsatz_Bild.png', as_attachment=True)

# Vorschau Seite
@app.route('/preview')
def preview():
    files = os.listdir(app.config['RESULTS_FOLDER'])

    images = []

    for file in files:
        extension = os.path.splitext(file)[1].lower()
        if extension in app.config['ALLOWED_EXTENSIONS']:
            images.append(file)

    return render_template('preview.html', images=images)

# Serve Image Function
@app.route('/serve-image/<filename>', methods=['GET'])
def serve_image(filename):
    return send_from_directory(app.config['RESULTS_FOLDER'], filename)

if __name__ == '__main__':
    app.run()

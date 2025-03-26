from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
from image_handler import is_spravka 
import os

app = Flask("spravka vision")
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['PROCESSED_FOLDER'] = 'processed'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

@app.route("/", methods = ["GET", "POST"])
def home():
    if (request.method == "POST"):
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        filename = secure_filename(file.filename)
        print(filename)
        input_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(input_path)
                
        return redirect(url_for('is_spravka_route', filename=filename))
    return render_template("upload.html")


@app.route('/processed/<filename>')
def processed_file(filename):
    return render_template('processed.html', filename=filename)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/processed_images/<filename>')
def processed_image(filename):
    return send_from_directory(app.config['PROCESSED_FOLDER'], filename)

@app.route("/is_spravka/<filename>")
def is_spravka_route(filename):
    if (is_spravka(filename)):
        return render_template("is_spravka.html", text="СПРАВОЧКА")
    else: return render_template("is_spravka.html", text="не справка(((")

if __name__ == "__main__":
    app.run()



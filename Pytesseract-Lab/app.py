from flask import Flask, render_template, url_for, request, redirect
from flask import session as login_session
from PIL import Image
import pytesseract
import requests
import json

pytesseract.pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

url = "https://deep-translate1.p.rapidapi.com/language/translate/v2"

headers = {
	"X-RapidAPI-Key": "e8e05e43e3msh9a82649a3281818p1f74e6jsnc48e32fbc2b0",
	"X-RapidAPI-Host": "deep-translate1.p.rapidapi.com"
}


def translate(language, text):
    payload = {
	"q": text,
	"target": language
    }
    
    response = requests.request("POST", url, json=payload, headers=headers)

    print(type(json.loads(response.text)))
    return json.loads(response.text)['data']['translations']['translatedText']


app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

app.config['SECRET_KEY'] = "Your_secret_string"


@app.route('/')
def form():
    return render_template('form.html')


@app.route('/translated', methods=['GET', 'POST'])
def translated():
    if request.method == 'POST':
        image = Image.open(request.files['pic'])
        text = pytesseract.image_to_string(image)
        translated = translate(request.form['lang'], text)
        return render_template('translated.html', text=translated)

    return render_template('translated.html')


if __name__ == "__main__":  # Makes sure this is the main process
    app.run(  # Starts the site
        debug=True
    )

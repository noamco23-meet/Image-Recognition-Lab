from flask import Flask, render_template, url_for, request, redirect
from flask import session as login_session
import face_recognition
import pyrebase
import os

app = Flask(  # Create a flask app
    __name__,
    template_folder='templates',  # Name of html file folder
    static_folder='static'  # Name of directory for static files
)

config = {
  "apiKey": "AIzaSyAEfpcAlxO6wtXzUnXWkFEsIeMV5K3YFXo",
  "authDomain": "face-recognition-project-faa88.firebaseapp.com",
  "projectId": "face-recognition-project-faa88",
  "storageBucket": "face-recognition-project-faa88.appspot.com",
  "messagingSenderId": "374763925057",
  "appId": "1:374763925057:web:869d01db2af309fb4720c0",
  "measurementId": "G-1K8V52LQK6",
  "databaseURL": "https://face-recognition-project-faa88-default-rtdb.firebaseio.com/"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()

app.config['SECRET_KEY'] = "Your_secret_string"
UPLOAD_FOLDER = 'images\\faces\\'
ALLOWED_EXTENSIONS = ['png', 'jpg', 'jpeg']


@app.route('/home')
def home():
    return render_template('home.html', person=db.child("Users").child(login_session['user']['localId']).get().val())


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        face = request.files['face']
        upload_file(face)
        try:
            login_session['user'] = auth.create_user_with_email_and_password(email, password)
            person = {"email": email, "face": face.filename, "password": password}
            db.child("Users").child(login_session['user']['localId']).set(person)
            return redirect(url_for('login'))
        except:
            return render_template('signup.html')
    else:
        return render_template('signup.html')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method=='POST':
        email = request.form['email']
        password = request.form['password']
        face = request.files['face']
        try:
            login_session['user'] = auth.sign_in_with_email_and_password(email, password)
        except:
            error = "Your credentials didn't match"
            return render_template("login.html", error=error)
        print("intest")
        saved_face_path = os.path.join(app.static_folder,UPLOAD_FOLDER, db.child("Users").child(login_session['user']['localId']).child("face").get().val())
        print(saved_face_path)
        saved_face = face_recognition.load_image_file(saved_face_path)
        saved_face_enc = face_recognition.face_encodings(saved_face)[0]
        print(saved_face_enc)
        input_face = face_recognition.load_image_file(face)
        input_face_enc = face_recognition.face_encodings(input_face)[0]
        print(input_face_enc)
        results = face_recognition.compare_faces([saved_face_enc], input_face_enc)
        if results[0]==True:
            return redirect(url_for('home'))
        return render_template("login.html", error="The faces don't match")
    else:
        return render_template("login.html")

        

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


def upload_file(file):
    if request.method == 'POST':
        if file and allowed_file(file.filename):
            filename = file.filename
            fn = os.path.join(app.static_folder,UPLOAD_FOLDER, filename)
            file.save(fn)


if __name__ == "__main__":  # Makes sure this is the main process
    app.run(  # Starts the site
        debug=True
    )

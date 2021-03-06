from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user

app = Flask(__name__)

app.config['SECRET_KEY'] = 'any-secret-key-you-choose'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "oladimehi"
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)



##CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))
#Line below only required once, when creating DB. 
# db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        password = generate_password_hash(request.form.get('password'), method='pbkdf2:sha256', salt_length=8)
        email = request.form.get("email")
        if User.query.filter_by(email=email).first():
            flash("That email already exist")
            return render_template("register.html")
        else:
            new_user = User(
                email=email,
                name=request.form.get('name'),
                password=password
            )
            db.session.add(new_user)
            db.session.commit()
            return render_template("secrets.html", name=new_user.name)
    return render_template("register.html")


@app.route('/login', methods = ["POST", 'GET'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        use = User.query.filter_by(email=email).first()
        check_pass = check_password_hash(use.password,request.form.get('password'))
        if not check_pass:
            flash("That password is incorrect")
        elif use and check_pass:
            login_user(use)
            return redirect(url_for('secrets', name=use.name))
        else:
            flash("That email or password is incorrect")
            return render_template("login.html")
    return render_template("login.html")


@app.route('/secrets/<name>')
def secrets(name):
    return render_template("secrets.html", name=name)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/download')
def download():
    return send_from_directory('static', filename="files/cheat_sheet.pdf")




if __name__ == "__main__":
    app.run(debug=True)

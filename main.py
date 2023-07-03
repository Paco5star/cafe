from flask import Flask , render_template, redirect, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import secrets 

secret_key = secrets.token_hex(16)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///D:/Starting+Files+-+cafe-api-start/instance/cafes.db.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = secret_key
class Cafe(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    map_url = db.Column(db.String(200), default='default_map_url')
    img_url = db.Column(db.String(200), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    has_sockets = db.Column(db.Boolean, default=False)
    has_toilet = db.Column(db.Boolean, default=False)
    has_wifi = db.Column(db.Boolean, default=False)
    can_take_calls = db.Column(db.Boolean, default=False)
    seats = db.Column(db.Integer, default=20)
    coffee_price = db.Column(db.Float, default=3.0)


class CafeForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    wifi = BooleanField('Has Wifi')
    sockets = BooleanField('has sockets')
    img_url = StringField('image URL', validators=[DataRequired()])
    submit = SubmitField('Add Cafe')





@app.route("/")
def home_page():
    cafes = db.session.execute("SELECT * FROM cafe").fetchall()
    
    return render_template("index.html", cafes=cafes)


@app.route("/add", methods=["GET", "POST"])
def add():
    form = CafeForm()
    if form.validate_on_submit():
        name = form.name.data
        location = form.location.data
        has_sockets = form.sockets.data
        has_wifi = form.wifi.data
        img_url = form.img_url.data

        cafe = Cafe(name=name, location=location, has_sockets=has_sockets, has_wifi=has_wifi, img_url=img_url )
        db.session.add(cafe)
        db.session.commit()
        print("data added")
        return redirect(url_for('home_page'))

    return render_template("add.html", form=form )

@app.route("/delete/<int:cafe_id>", methods=["POST"])
def delete_cafe(cafe_id):
    cafe = Cafe.query.get(cafe_id)
    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for("home_page"))

if __name__ == "__main__":
    app.run(debug=True)
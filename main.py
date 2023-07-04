from flask import Flask , render_template, redirect, url_for
import sqlite3
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, SubmitField
from wtforms.validators import DataRequired
import secrets 
import os 

import psycopg2

secret_key = secrets.token_hex(16)

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL2", "sqlite:///d:\Starting+Files+-+cafe-api-start\instance\cafes.db.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
app.secret_key = secret_key


class Cafe(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    map_url = db.Column(db.String(200), default='default_map_url')
    img_url = db.Column(db.String(500), nullable=False)
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


def transfer_data():
    

    # Connect to SQLite database
    sqlite_conn = sqlite3.connect('d:\Starting+Files+-+cafe-api-start\instance\cafes.db.db')
    sqlite_cursor = sqlite_conn.cursor()

    # Connect to PostgreSQL database
    pg_conn = psycopg2.connect(
        host='ec2-54-208-11-146.compute-1.amazonaws.com',
        port='5432',
        dbname='dff9c667bdv8sh',
        user='gaprimukshvzcp',
        password='56ca6d92752dd52c03bacd467cf34d54148104af3c003c6793e2a3ac4aec0f10'
    )
    pg_cursor = pg_conn.cursor()

    alter_query = "ALTER TABLE cafe ALTER COLUMN img_url TYPE VARCHAR(500);"
    pg_cursor.execute(alter_query)
    # Retrieve data from SQLite
    sqlite_cursor.execute("SELECT * FROM cafe")
    rows = sqlite_cursor.fetchall()
    pg_cursor.execute("ALTER TABLE cafe ALTER COLUMN img_url TYPE VARCHAR(700)")
    # Insert data into PostgreSQL
    for row in rows:
        row = list(row)

        row[5] = bool(row[5])  # has_sockets
        row[6] = bool(row[6])  # has_toilet
        row[7] = bool(row[7])  # has_wifi
        row[8] = bool(row[8])  # can_take_calls

        seats = row[9]
        try:
            seats = int(seats)
        except ValueError:
            seats = None
            row[9] = seats

        coffee_price = row[10].lstrip('£')
        try:
            coffee_price = float(coffee_price)
        except ValueError:
            coffee_price = None
        row[10] = coffee_price

        query = """
        INSERT INTO cafe (
            id, name, map_url, img_url, location, has_sockets,
            has_toilet, has_wifi, can_take_calls, seats, coffee_price
        ) VALUES (
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
        )
        """
        pg_cursor.execute(query, tuple(row))
        



    # Commit the changes and close the connections
    pg_conn.commit()
    pg_cursor.close()
    pg_conn.close()
    sqlite_cursor.close()
    sqlite_conn.close()




if __name__ == "__main__":
    
    app.run(debug=True)
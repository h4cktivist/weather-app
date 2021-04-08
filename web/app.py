import sys
import requests
import json

from flask import Flask, render_template, redirect, request, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///weather.db'
app.secret_key = 'secret_key'

db = SQLAlchemy(app)


class City(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return self.name


@app.route('/')
def index():
    cities = City.query.all()
    weather = []

    for city in cities:
        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid=5b307cb345d3bef73b070c9b38e5ca4a&units=metric')

        content = json.loads(response.text)
        weather_info = {'degrees': f"{content['main']['temp']}",
                        'state': f"{content['weather'][0]['main']}",
                        'city': f"{content['name']}",
                        'id': f"{city.id}"}
        weather.append(weather_info)

    return render_template("index.html", weather=weather)


@app.route('/add_city', methods=['POST'])
def add_city():
    if request.method == 'POST':
        city_name = request.form.get('city_name')

        response = requests.get(
            f'https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid=5b307cb345d3bef73b070c9b38e5ca4a&units=metric')

        if response.status_code == 404:
            flash("The city doesn't exist!")
            return redirect('/')

        cities = City.query.all()
        for city in cities:
            if city.name == city_name:
                flash("The city has already been added to the list!")
                return redirect('/')

        else:
            city = City(name=city_name)
            db.session.add(city)
            db.session.commit()

            return redirect('/')


@app.route('/delete/<int:id>', methods=['POST'])
def delete(id):
    if request.method == 'POST':
        city = City.query.filter_by(id=id).first()
        db.session.delete(city)
        db.session.commit()
        return redirect('/')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        db.create_all()
        arg_host, arg_port = sys.argv[1].split(':')
        app.run(host=arg_host, port=arg_port)
    else:
        db.create_all()
        app.run()

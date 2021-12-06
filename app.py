import os
import requests
from flask import Flask,render_template,request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app=Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,"data.sqlite")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
Migrate(app,db)

class City(db.Model):

    __tablename__ = 'cities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    def __init__(self,name):
        self.name = name

@app.route('/',methods=['GET','POST'])
def home():
    url = 'https://api.openweathermap.org/data/2.5/weather?q={}&units=metric&appid=3d50f726802c1142e1057b562fdfbdb0'
    
    if request.method == 'POST':
        new_city = request.form.get('city')
        r =  requests.get(url.format(new_city)).json()

        if 200<= int(r['cod']) <= 299:
            new_city_obj = City(new_city)
            db.session.add(new_city_obj)
            db.session.commit()      

    cities = City.query.all()   
    
    weather_data = []
    
    for city in cities:

        r = requests.get(url.format(city.name)).json()
        weather = {
            "city": city.name,
            "temperature": r["main"]['temp'],
            "description": r["weather"][0]["description"],
            "icon" : r["weather"][0]["icon"],
            "id" : city.id
        }

        weather_data.append(weather)
    
    return render_template('weather.html', weather_data = weather_data)

@app.route('/delete/<int:city_id>')
def delete(city_id):
    city = City.query.get(city_id)
    db.session.delete(city)
    db.session.commit()
    return redirect(url_for('home'))

    
if __name__ == '__main__':
    app.run(port=5000,debug=True)
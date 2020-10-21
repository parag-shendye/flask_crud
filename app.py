from flask import Flask, request, jsonify, render_template, Markup
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os
import plotly.graph_objs as go
import plotly
import pandas as pd
import numpy as np
import json
import time
import re

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

# DataBase
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# init db
db = SQLAlchemy(app)
# init ma
ma = Marshmallow(app)

# product model


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db .Column(db.String(100), unique=True)
    array = db.Column(db.String(3000))
    matrix = db.Column(db.String(20000))
    day = db.Column(db.String(50), unique=True)

    def __init__(self, date, array, matrix, day):
        self.date = date
        self.array = array
        self.day = day
        self.matrix = matrix


# product schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id', 'date', 'day', 'array','matrix')


# init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# render dummy page


@app.route("/d3", methods=["GET"])
def serveplots():
    mat = generateMatrixFromString(faskeString())
    bar = create_plot()
    
    return render_template('index.html', plot=bar,mat=mat)


@app.route("/dummy", methods=['GET'])
def dummy():
    bar = create_plot()
    return render_template('index.html', plot=bar)


# Create a product


@app.route('/product', methods=['POST'])
def add_product():
    date = request.form.get("date")
    array = request.form.get("array")
    matrix = request.form.get("matrix")
    day = time.strftime("%A", time.strptime(date, "%Y-%m-%d"))
    product = Product.query.filter_by(day=day).first()
    if(product != None):
        selected = Product.query.get(product.id)
        db.session.delete(selected)
        db.session.commit()

    new_product = Product(date, array, day, matrix)
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)


@app.route('/product', methods=['GET'])
def getProducts():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)


@app.route('/product/<id>', methods=['GET'])
def getParticaularProductByID(id):
    product = Product.query.filter_by(id=id).first()
    result = product_schema.dump(product)
    return jsonify(result)


@app.route('/product/<day>', methods=['GET'])
def getParticaularProductByDay(day):
    product = Product.query.filter_by(day=day).first()
    print(product)
    result = product_schema.dump(product)
    return jsonify(result)


# @app.route('/product/<id>', methods=['PUT'])
# def updateProduct(id):
#     product = Product.query.get(id)

#     name = request.form.get("name")
#     description = request.form.get("description")
#     price = request.form.get("price")
#     qty = request.form.get("qty")

#     product.name = name
#     product.descritption = description
#     product.price = price
#     product.qty = qty

#     db.session.commit()

#     return product_schema.jsonify(product)


@app.route('/product/<id>', methods=['DELETE'])
def deleteProduct(id):
    product = Product.query.get(id)
    db.session.delete(product)
    db.session.commit()

    return product_schema.jsonify(product)


@app.route('/product', methods=['DELETE'])
def deleteAll():
    try:
        num_rows_deleted = db.session.query(Product).delete()
        db.session.commit()
    except:
        db.session.rollback()

    return jsonify({'rows deleted': num_rows_deleted})

# Helper functions


def create_plot():

    N = 736
    x = np.asarray([i for i in range(N)])

    mon = readFromDataBase("Monday")
    tue = readFromDataBase("Tuesday")
    wed = readFromDataBase("Wednesday")
    thu = readFromDataBase("Thursday")
    fri = readFromDataBase("Friday")
    sat = readFromDataBase("Saturday")
    sun = readFromDataBase("Sunday")

    df = pd.DataFrame({'lines': x, 'mon': mon, 'tue': tue, 'wed': wed,
                       'thu': thu, 'fri': fri, 'sat': sat, 'sun': sun})  # creating a dataframe

    data = [
        go.Bar(
            name="Monday",
            x=df['lines'],
            y=df['mon']
        ),
        go.Bar(
            name="Tuesday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['tue']
        ),
        go.Bar(
            name="Wednesday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['wed']
        ),
        go.Bar(
            name="Thursday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['thu']
        ),
        go.Bar(
            name="Friday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['fri']
        ),
        go.Bar(
            name="Saturday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['sat']
        ),
        go.Bar(
            name="Sunday",
            x=df['lines'],  # assign x as the dataframe column 'x'
            y=df['sun']
        )
    ]

    graphJSON = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON


def readFromDataBase(dayOfWeek):
    product = Product.query.filter_by(day=dayOfWeek).first()
    if(product == None):
        x = [i for i in range(736)]
        y = [0 for i in range(736)]
    else:
        x = [i for i in range(736)]
        y = [0 for i in range(736)]
        count = 0
        for line in product.array.split(","):
            if(int(line.split("=")[0]) in x):
                count += 1
                y[int(line.split("=")[0])] = int(line.split("=")[1])

    return y


def generateMatrixFromString(stringData):
    """
    takes in string data to generate np array
    """
    lengthOfColumns = len(stringData.split(","))
    x = np.asarray([i for i in range(lengthOfColumns)])
    y = np.asarray([i for i in range(lengthOfColumns)])
    values = np.asarray([int(re.findall(r'\d+',i)[0]) for i in stringData.split(",")])

    df = pd.DataFrame({'x': x, 'y': y, 'values': values})
    return json.dumps(df.to_dict(orient='records'))
def faskeString():
    val = list(np.random.randint(256,size=736*23))
    return "','".join(map(str, val))

# Run server
if __name__ == "__main__":
    app.run()

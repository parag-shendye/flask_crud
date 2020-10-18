from flask import Flask , request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))

#DataBase
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///'+os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False

#init db
db = SQLAlchemy(app)
#init ma
ma = Marshmallow(app)

#product model
class Product(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db .Column(db.String(100),unique=True)
    descritption = db.Column(db.String(200))
    price = db.Column(db.Float)
    qty = db.Column(db.Integer)

    def __init__(self,name, description,price,qty):
        self.name = name
        self.descritption=description
        self.price = price
        self.qty = qty

# product schema
class ProductSchema(ma.Schema):
    class Meta:
        fields = ('id','name','description','price','qty')
# init schema
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# Create a product
@app.route('/product', methods=['POST'])
def add_product():
    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    qty = request.form.get("qty")

    new_product = Product(name, description, price, qty)
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product)

@app.route('/product',methods=['GET'])
def getProducts():
    all_products = Product.query.all()
    result = products_schema.dump(all_products)
    return jsonify(result)

@app.route('/product/<id>', methods=['GET'])
def getParticaularProduct(id):
    product = Product.query.filter_by(id=id).first()
    result = product_schema.dump(product)
    return jsonify(result)

@app.route('/product/<id>', methods=['PUT'])
def updateProduct(id):
    product = Product.query.get(id)

    name = request.form.get("name")
    description = request.form.get("description")
    price = request.form.get("price")
    qty = request.form.get("qty")

    product.name = name
    product.descritption = description
    product.price = price
    product.qty = qty

    db.session.commit()

    return product_schema.jsonify(product)

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

    return  jsonify({'rows deleted': num_rows_deleted})
# Run server
if __name__ == "__main__":
    app.run()
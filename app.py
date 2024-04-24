from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

app.config['SECRET_KEY'] = '706d7fd0-0ce3-4a7b-818c-9a18dac1a18e'

db = SQLAlchemy(app)

CORS(app)

login_manager = LoginManager()

login_manager.init_app(app)

login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)


@app.route('/login', methods=['POST'])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get('username')).first()

    if user and data.get('password') == user.password:
        login_user(user)

        return jsonify({'message': 'Logged in successfully!'})

    return jsonify({'message': 'Unauthorized! Invalid credentials!'}), 401


@app.route('/api/products/add', methods=["POST"])
def add_product():
    data = request.json

    if 'name' in data and 'price' in data:
        product = Product(name=data['name'], price=data['price'],
                          description=data.get('description', ''))

        db.session.add(product)

        db.session.commit()

        return jsonify({'message': 'Product added successfully!'}), 201

    return jsonify({'message': 'Invalid product data!'}), 400


@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)

    if product:
        db.session.delete(product)

        db.session.commit()

        return jsonify({'message': 'Product deleted successfully!'})

    return jsonify({'message': 'Product not found!'}), 404


@app.route('/api/products/<int:product_id>', methods=['GET'])
def get_product_details(product_id):
    product = Product.query.get(product_id)

    if product:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'description': product.description,
        })

    return jsonify({'message': 'Product not found!'}), 404


@app.route('/api/products/update/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    product = Product.query.get(product_id)

    if not product:
        return jsonify({'message': 'Product not found!'}), 404

    data = request.json

    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit()

    return jsonify({'message': 'Product updated successfully!'})


@app.route('/api/products', methods=['GET'])
def get_products():
    products = Product.query.all()

    products_list = []

    for product in products:
        product_data = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
        }

        products_list.append(product_data)

    return jsonify(products_list)


@app.route('/')
def main_endpoint():
    return 'E-commerce API'


if __name__ == '__main__':
    app.run(debug=True)

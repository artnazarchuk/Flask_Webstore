import os
import secrets
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_from_directory

# from cloudipsp import Api, Checkout

# api = Api(merchant_id=1396424,
#           secret_key='test')
# checkout = Checkout(api=api)
# data = {
#     "currency": "USD",
#     "amount": 10000
# }
# url = checkout.url(data).get('checkout_url')


UPLOAD_FOLDER = 'static/image'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

secret_key = secrets.token_hex(16)

app = Flask(__name__)
app.config['SECRET_KEY'] = secret_key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
db = SQLAlchemy(app)

class Categories(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.String(50), nullable=False, unique=True)
    image = db.Column(db.String(50), nullable=True, unique=False)

    def __repr__(self):
        return f'<category {self.id}>'

class Products(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    product = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    isActive = db.Column(db.Boolean, default=True)
    image = db.Column(db.String(50), nullable=True, unique=False)
    category_id = db.Column(db.Integer(), db.ForeignKey('categories.id'))

    def __repr__(self):
        return f'<product {self.id}>'


@app.route('/')
def index():
    categories = Categories.query.order_by(Categories.category).all()
    return render_template('index.html', data=categories)

@app.route('/category_products/<int:id>')
def category_products(id):
    products_category = Products.query.filter_by(category_id=id)
    category_name = Categories.query.get(id)
    return render_template('category_products.html', data=products_category, category_name=category_name)

@app.route('/products')
def products():
    products = Products.query.order_by(Products.created_on.desc()).all()
    return render_template('products.html', data=products)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':

        if request.form.get('category_create'):

            file = request.files['image']

            if file.filename == '':
                flash('?????????????????????? ???? ??????????????')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            category = request.form['category_create']
            category_create = Categories(category=category, image=file.filename)

            try:
                db.session.add(category_create)
                db.session.commit()
                return redirect('/create')
            except:
                db.session.rollback()
                return '?????? ???????????????????? ?????????????????? ?????????????????? ????????????'

        if request.form.get('product'):

            file = request.files['image']

            if file.filename == '':
                flash('?????????????????????? ???? ??????????????')
                return redirect(request.url)
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            category = request.form['category']
            category_create = Categories.query.filter_by(category=category).first()

            product = request.form['product']
            price = request.form['price']
            description = request.form['description']
            isActive = bool(request.form.get('isActive'))
            category_id = category_create.id
            product_create = Products(product=product, price=price, description=description, isActive=isActive,
                                      category_id=category_id, image=file.filename)
            try:
                db.session.add(product_create)
                db.session.commit()
                return redirect('/products')
            except:
                db.session.rollback()
                return '?????? ???????????????????? ???????????? ?????????????????? ????????????'
        else:
            return redirect('/create')
    else:
        categories = Categories.query.order_by(Categories.category).all()
        return render_template('create.html', data=categories)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

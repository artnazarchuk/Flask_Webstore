import os
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import send_from_directory

UPLOAD_FOLDER = 'static/image'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
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

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

app.add_url_rule(
    "/uploads/<name>", endpoint="download_file", build_only=True
)
@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':

        if request.form.get('category_create'):

            if 'image' not in request.files:
                flash('No image part')
                return redirect(request.url)
            file = request.files['image']
            # If the user does not select a image, the browser submits an
            # empty image without a filename.
            if file.filename == '':
                flash('No selected image')
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
                return 'При добавлении категории произошла ошибка'

        if request.form.get('product'):

            category = request.form['category']
            category_create = Categories.query.filter_by(category=category).first()

            product = request.form['product']
            price = request.form['price']
            description = request.form['description']
            isActive = bool(request.form.get('isActive'))
            category_id = category_create.id
            product_create = Products(product=product, price=price, description=description, isActive=isActive,
                                      category_id=category_id)
            try:
                db.session.add(product_create)
                db.session.commit()
                return redirect('/products')
            except:
                db.session.rollback()
                return 'При добавлении товара произошла ошибка'
        else:
            return redirect('/create')
    else:
        categories = Categories.query.order_by(Categories.category).all()
        return render_template('create.html', data=categories)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS




@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

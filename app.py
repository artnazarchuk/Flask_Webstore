from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///store.db'
db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    category = db.Column(db.String(30), nullable=False)
    product = db.Column(db.String(50), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_on = db.Column(db.DateTime, default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow, onupdate=datetime.utcnow)
    isActive = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return self.id

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create', methods=['POST', 'GET'])
def create():
    if request.method == 'POST':
        category = request.form['category']
        product = request.form['product']
        price = request.form['price']
        description = request.form['description']
        isActive = bool(request.form.get('isActive'))
        product_create = Item(category=category, product=product, price=price, description=description, isActive=isActive)
        try:
            db.session.add(product_create)
            db.session.commit()
            return redirect('/')
        except:
            return 'При добавлении товара произошла ошибка'
    else:
        return render_template('create.html')

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)

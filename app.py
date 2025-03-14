from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Product, Customer, Transaction, TransactionDetail
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/products', methods=['GET', 'POST'])
@login_required
def products():
    if request.method == 'POST':
        name = request.form['name']
        price = request.form['price']
        stock = request.form['stock']
        barcode = request.form['barcode']
        category = request.form['category']
        new_product = Product(name=name, price=price, stock=stock, barcode=barcode, category=category)
        db.session.add(new_product)
        db.session.commit()
        flash('Product added successfully!')
        return redirect(url_for('products'))
    all_products = Product.query.all()
    return render_template('products.html', products=all_products)

@app.route('/customers', methods=['GET', 'POST'])
@login_required
def customers():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        address = request.form['address']
        new_customer = Customer(name=name, phone=phone, email=email, address=address)
        db.session.add(new_customer)
        db.session.commit()
        flash('Customer added successfully!')
        return redirect(url_for('customers'))
    all_customers = Customer.query.all()
    return render_template('customer.html', customers=all_customers)

@app.route('/new_transaction', methods=['GET', 'POST'])
@login_required
def new_transaction():
    if request.method == 'POST':
        customer_id = request.form['customer_id']
        payment_method = request.form['payment_method']
        total = 0
        transaction = Transaction(total=total, payment_method=payment_method, user_id=current_user.id, customer_id=customer_id)
        db.session.add(transaction)
        db.session.commit()
        
        # Process items and update total
        for item in request.form.getlist('items'):
            product = Product.query.get(item['product_id'])
            quantity = item['quantity']
            total += product.price * quantity
            transaction_detail = TransactionDetail(transaction_id=transaction.id, product_id=product.id, quantity=quantity, price=product.price)
            db.session.add(transaction_detail)
        transaction.total = total
        db.session.commit()
        flash('Transaction completed successfully!')
        return redirect(url_for('transactions'))
    products = Product.query.all()
    customers = Customer.query.all()
    return render_template('new_transaction.html', products=products, customers=customers)

@app.route('/transactions')
@login_required
def transactions():
    all_transactions = Transaction.query.all()
    return render_template('transactions.html', transactions=all_transactions)

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
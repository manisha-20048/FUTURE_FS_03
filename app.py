from flask import Flask,redirect,url_for,render_template,session,request,flash
import mysql.connector

app=Flask(__name__)
app.secret_key='mysecretekey123'
mydb=mysql.connector.connect(host='localhost',user='root',password='admin',database='task3')
cursor=mydb.cursor(buffered=True)

@app.route('/')
def welcome():
    return render_template('welcome.html')
@app.route('/admin_page')
def admin_page():
    return render_template('admin_page.html')
@app.route('/user_page')
def user_page():
    return render_template('user_page.html')
@app.route('/register',methods=['GET','POST'])
def register():
    if request.method=='POST':
        try:
            name=request.form['username']
            email=request.form['email']
            password=request.form['password']
            sql="insert into task3 (name,email,password) values (%s,%s,%s)"
            values=(name,email,password)
            cursor.execute(sql,values)
            mydb.commit()
            return redirect(url_for('login'))
        except Exception as e:
            flash(e)
    return render_template('register.html')
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        email=request.form['email']
        password=request.form['password']

        sql='select id,name,email from task3 where email=%s and password=%s'
        values=(email,password)
        cursor.execute(sql,values)
        user=cursor.fetchone()
        if user:
            session['id']=user[0]
            session['name']=user[1]
            session['email']=user[2]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid user or password')
    return render_template('login.html')
@app.route('/admin_register',methods=['GET','POST'])
def admin_register():
    if request.method=='POST':
        try:
            name=request.form['username']
            email=request.form['email']
            password=request.form['password']
            sql='insert into admin (name,email,password) values(%s,%s,%s)'
            values=(name,email,password)
            cursor.execute(sql,values)
            mydb.commit()
            flash('registered successfully')
            return redirect(url_for('admin_login'))
        except Exception as e:
            flash('registered already')
    return render_template('admin_register.html')
@app.route('/admin_login',methods=['GET','POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        sql = "SELECT * FROM admin WHERE email=%s AND password=%s"
        cursor.execute(sql, (email, password))
        admin = cursor.fetchone()
        if admin:
            session['user_id'] = admin[0]
            session['username'] = admin[1]
            session['admin'] = email
            return redirect(url_for('allorders'))
        else:
            flash("Invalid email or password")

    return render_template('admin_login.html')
@app.route('/dashboard',methods=['GET','POST'])
def dashboard():
    if 'name' in session:
        name=session.get('name')
        return render_template('index.html',name=name)
    else:
        flash('invalid user')
        return redirect(url_for('login'))
@app.route('/menu',methods=['GET','POST'])
def menu():
    if 'email' in session:
        try:
            sql='select * from products'
            cursor.execute(sql)
            products=cursor.fetchall()
            return render_template('menu.html',products=products)
        except Exception as e:
            flash(e)
            return redirect(url_for('login'))
@app.route('/cart/<int:product_id>',methods=['GET','POST'])
def cart(product_id):
    if 'id' in session:
        user_id=session['id']
        #check if product already in cart
        sql='select quantity from cart where user_id=%s and product_id=%s'
        cursor.execute(sql,(user_id,product_id))
        result=cursor.fetchone()
        if result:
            #product exists increase quantity
            quantity=result[0]+1
            update_sql='update cart set quantity=%s where user_id=%s and product_id=%s'
            cursor.execute(update_sql,(quantity,user_id,product_id))
        else:
            insert_sql='insert into cart(user_id,product_id,quantity) values(%s,%s,%s)'
            cursor.execute(insert_sql,(user_id,product_id,1))
        mydb.commit()
        return redirect(url_for('view_cart'))
    else:
        return redirect(url_for('login'))
@app.route('/view_cart')
def view_cart():
    if 'id' in session:
        user_id=session['id']
        sql='select p.product_id, p.product_img,p.product_name,p.product_price,c.quantity,c.cart_id from cart c join products p on c.product_id=p.product_id where c.user_id=%s'
        cursor.execute(sql,(user_id,))
        results=cursor.fetchall()
        return render_template('cart.html',results=results)
@app.route('/placeorder/<int:product_id>',methods=['GET','POST'])
def placeorder(product_id):
    if request.method=='POST':
        if 'id' in session:
            user_id=session['id']
            phno=request.form['phno']
            Address=request.form['address']
            quantity=request.form['quantity']
            payment_mode=request.form['payment_mode']
            try:
                sql='insert into placeorder (phno,address,user_id,product_id,payment_mode,quantity) values(%s,%s,%s,%s,%s,%s)'
                values=(phno,Address,user_id,product_id,payment_mode,quantity)
                cursor.execute(sql,values)
                mydb.commit()
                flash('Order placed Successfully')
                return redirect(url_for('view_orders'))

            except Exception as e:
                flash(e)
        else:
            flash('pls login')
            return redirect(url_for('login'))
    return render_template('placeorder.html')
@app.route('/view_orders')
def view_orders():
     if 'id' in session:
        user_id=session['id']
        sql='select p.product_id, p.product_img,p.product_name,p.product_price,pl.order_id,pl.quantity,pl.status,pl.address,pl.order_date,pl.payment_mode from placeorder pl  join products p on pl.product_id=p.product_id where pl.user_id=%s'
        cursor.execute(sql,(user_id,))
        results=cursor.fetchall()
        return render_template('view_orders.html',results=results)
@app.route('/allorders')
def allorders():
        if session.get('admin'):
            sql='select pl.order_id, p.product_img,p.product_name,p.product_price,pl.order_id,pl.quantity,pl.status,pl.address,pl.order_date,pl.payment_mode from placeorder pl  join products p on pl.product_id=p.product_id'
            cursor.execute(sql)
            results=cursor.fetchall()
            return render_template('allorders.html',results=results)
        else:
            flash('Access denied . Admins only.')
            return redirect(url_for('menu'))
@app.route('/update/<int:order_id>',methods=['GET','POST'])
def update_status(order_id):
    sql="update placeorder set status='Confirmed' where order_id=%s"
    cursor.execute(sql,(order_id,))
    mydb.commit()
    return redirect(url_for('allorders'))
@app.context_processor
def cartcount():
    if 'id' in session:
        user_id=session['id']
        cursor.execute('select sum(quantity) from cart where user_id=%s',(user_id,))
        count=cursor.fetchone()[0]
        if count is None:
            count=0
        return dict(cart_count=count)
    return dict(cart_count=0) 
@app.route('/delete cart/<int:cart_id>')
def deletecart(cart_id):
    if 'id' in session:
        user_id=session['id']
        cursor.execute('delete from cart where cart_id=%s',(cart_id,))
        mydb.commit()
        return redirect(url_for('view_cart'))
@app.route('/delete_account',methods=['POST'])
def delete_account():
    if 'id' in session:
        user_id=session['id']
        try:
            #delete cart
            cursor.execute('delete from cart where user_id=%s',(user_id,))
            #delete placeorder
            cursor.execute("DELETE FROM placeorder WHERE user_id=%s", (user_id,))
            #delete user
            cursor.execute("DELETE FROM task3 WHERE id=%s", (user_id,))
            mydb.commit()
            session.clear()
            return redirect(url_for('register'))
        except Exception as e:
            flash(e)
    else:
        flash('pls login first')
        return redirect(url_for('login'))
            
if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)
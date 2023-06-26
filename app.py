from flask import Flask, render_template, url_for, redirect,request,session,make_response
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from flask_bcrypt import Bcrypt
from flask_bcrypt import check_password_hash
from werkzeug.security import generate_password_hash,check_password_hash
from functools import wraps
from flask_login import logout_user
import os
import product_fetch
import base64
import shutil


app = Flask(__name__)
app.secret_key = 'SID-db'
bcrypt = Bcrypt(app)
# MySQL configurations
# app.config['MYSQL_HOST'] = 'localhost'
# app.config['MYSQL_USER'] = 'root'
# app.config['MYSQL_PASSWORD'] = ''
# app.config['MYSQL_DB'] = 'ecommerce-project-2023'

#Online Mysql Setup 
app.config['MYSQL_HOST'] = 'sql12.freesqldatabase.com'
app.config['MYSQL_USER'] = 'sql12628874'
app.config['MYSQL_PASSWORD'] = 'y8EKXWHmKw'
app.config['MYSQL_DB'] = 'sql12628874'


mysql = MySQL(app)

Dbname = ""

usermail = None
    
# Landing Page Route
@app.route("/")
def landingpage():
    session.clear()
    return render_template('index.html')

# Auth Page
@app.route("/0auth")
def auth():
    return render_template('0auth.html')

# Login Page
@app.route("/Login",methods = ['GET', 'POST'])
def Login():
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form.get('email')
        password = request.form.get("password")
        

        try:
            cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            cur.execute("SELECT * FROM user WHERE email = %s", (email,))
            user = cur.fetchone()
            # print(user)
            cur.close()
            session['loggedin'] = True
            session['userid'] = user['id']
            session['name'] = user['username']
            session['email'] = user['email']
            session['error'] = ""
            
            

            if user and check_password_hash(user['password'],password):
                global usermail
                usermail = user['email']
                return redirect(url_for("product_page"))
            else:
                session['error'] = 'Invalid username or password !'
        except Exception as e:
            session['error'] = "Fill Up The Details To Login !"+str(e)
            
    return render_template("0auth.html",err="Fill Up The Details To Login !")
    

#Register Page

@app.route("/register",methods = ['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form :
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        email = request.form['email']
        cur = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cur.execute('SELECT * FROM user WHERE username = %s OR email = %s', (username, email))
        user = cur.fetchone()
        
        if user:
            message = 'Account already exists !'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address !'
        elif not username or not password or not email:
            message = 'Please fill out the form !'
        else:
            cur.execute('INSERT INTO user(username, password, email) VALUES(%s, %s, %s)',
                       (username, password, email))
            mysql.connection.commit()
            cur.close()
            message = 'Registerd successfully!'
    elif request.method == 'POST':
        message = 'Please fill out the form !'
    return render_template('0auth.html', message = message)





# Logout Page

@app.route("/logout")
def logout():
    session.pop('email', None)
    session.clear()
    global usermail 
    usermail = None
    response = make_response(redirect(url_for('Login')))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    #Deleting The Image Folder Fetched From DataBasem:->1images
    static_folder = app.static_folder
    print(static_folder)
    images_folder = os.path.join(static_folder, '1images')

    if os.path.exists(images_folder):
        try:
            # Remove the "images" folder and its contents
            shutil.rmtree(images_folder)
            print('Images folder deleted successfully')
        except OSError as e:
            print(f'Error deleting images folder: {e}')
    else:
        print('Images folder does not exist')
    # return response
    return redirect(request.referrer or '/')
    # return redirect(url_for('/'))


# Decorator to check if user is authenticated
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session:
            return redirect(url_for('Login'))
        return f(*args, **kwargs)
    return decorated_function

# Product Page (Protected Route)
# Product Page
@app.route("/product_page",methods = ['POST','GET'])
@login_required
def product_page():
    # Fetching Product Data From DB Dynamically and showing them on the Web:
    image_data = product_fetch.save_image()
    # Create a folder inside the static folder if it doesn't exist
    image_folder = os.path.join(app.root_path, 'static', '1images')
    imagelist = []
    if not os.path.exists(image_folder):
        os.makedirs(image_folder)
        for image, filename in image_data:
            # Convert the BLOB image data to a base64-encoded string
            image_base64 = base64.b64encode(image).decode('utf-8')
            # Save the image to the static/images folder
            
            image_path = os.path.join(image_folder, f'{filename}.jpg')
            imagelist.append(filename)
            with open(image_path, 'wb') as file:
                file.write(base64.b64decode(image_base64))
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))
    
    print(imagelist)
    return render_template("products.html",name=imagelist)


# Landing - Category Page

@app.route("/L-category")
def Lcategory():
    return render_template("L-category.html")

# # Landing - products Page

@app.route("/L-products")
def Lproducts():
    return render_template("L-products.html")

# Landing - Clients Page

@app.route("/L-clients")
def Lclients():
    return render_template("L-clients.html")

# Landing - Contact Page
@app.route("/L-contact")
def Lcontact():
    return render_template("L-contact.html")



# P-blog-details page
@app.route("/product_page/P_blog_details")
def P_blog_details():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-blog-details.html")

# P-blog page
@app.route("/product_page/P_blog")
def P_blog():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-blog.html")

# P-checkout page
@app.route("/product_page/P_checkout")
def P_checkout():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-checkout.html")

# P-contact page
@app.route("/product_page/P_contact")
def P_contact():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-contact.html")


# P-main page
@app.route("/product_page/P_main")
def P_main():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-main.html")

# P-shop-details page
@app.route("/product_page/P_shop_details")
def P_shop_details():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-shop-details.html")

# P-shop-grid page
@app.route("/product_page/P_shop_grid")
def P_shop_grid():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-shop-grid.html")


# P-shoping-cart page
@app.route("/product_page/P_shoping_cart")
def P_shoping_cart():
    if 'email' not in session:
        session.clear()
        return redirect(url_for("Login"))

    return render_template("P-shoping-cart.html")










if __name__ == '__main__':
    app.run(debug=True)
import requests
from flask import Flask, redirect,render_template,request, session, url_for
import sqlite3


app = Flask(__name__)
app.secret_key = 'clavecarlota'
def obtener_conexion():
    conexion = sqlite3.connect('Apokacao.db.sqlite3')
    return conexion

@app.route('/inicio de sesion', methods=['GET', 'POST'])
def inicio_sesion():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        conexion = obtener_conexion()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND contrasena = ?", (usuario, contrasena))
        usuario_encontrado = cursor.fetchone()
        cursor.close()
        conexion.close()
        if usuario_encontrado:
            
            session['usuario'] = usuario_encontrado[1]
        return redirect(url_for('inicio'))

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return render_template('inicio_sesion.html', mensaje='Has cerrado sesión correctamente.')       

@app.route("/")
def hello_world():
    return render_template("base.html")
@app.route("/inicio")
def inicio():

    conexion = obtener_conexion()
    cursor = conexion.cursor()
    
    # 🚨 TRUCO DE MAÑANA: Creamos las tablas automáticamente si es la primera vez que corre en Render
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT NOT NULL UNIQUE,
            clave TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            precio REAL NOT NULL,
            categoria TEXT NOT NULL
            
        )
    """)
    
    # Insertamos el admin por defecto si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO usuarios (usuario, clave) VALUES ('admin', '1234')")
        conexion.commit()

    cursor.execute("SELECT * FROM productos")
    productos_db = cursor.fetchall()
    
    cursor.close()
    conexion.close()
    
    es_admin = 'usuario' in session
    return render_template('index.html', inventario=productos_db, es_admin=es_admin)

    return render_template("index.html")
@app.route("/formulario")
def formulario():
    return render_template("formulario.html")
@app.route("/registro",methods=["GET","POST"])
def registro():
    if 'usuario' not in session:
        return "Acceso denegado.", 403

    if request.method == "GET":
        # Aquí puedes procesar los datos del formulario
         return render_template("formulario.html")
    if request.method == "POST":
        # Aquí puedes procesar los datos del formulario
        nombre = request.form.get("name")
        email = request.form.get("email")
        # Realiza las acciones necesarias con los datos (por ejemplo, guardarlos en una base de datos)
        return render_template("registro.html",nombre=nombre,email=email)
@app.route("/productos")
def productos():
    url = "https://fakestoreapi.com/products"
    response = requests.get(url)
       
    datos_JSON = response.json()
    catalogo = []
    for producto in datos_JSON:
        producto_info = {
            "id": producto["id"],
            "title": producto["title"],
            "price": producto["price"],
            "description": producto["description"],
            "category": producto["category"],   
            "image": producto["image"]
        }
        catalogo.append(producto_info)


    return render_template("producto.html", productos=catalogo)

if __name__=="__main__":
    app.run(debug=True,port=5000
            )

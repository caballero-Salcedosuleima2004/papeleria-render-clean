from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_suleima'

def conectar_bd():
    # Render nos da la URL de la base de datos en esta variable
    url_bd = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url_bd, sslmode='require')

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        tipo_usuario = request.form['tipo_usuario']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        if tipo_usuario == 'cliente':
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute("SELECT id_cliente, nombre FROM clientes_web WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
                cliente = cursor.fetchone()
                cursor.close()
                conexion.close()
                
                if cliente:
                    session['id_usuario'] = cliente['id_cliente']
                    session['usuario'] = cliente['nombre']
                    session['rol'] = 'Cliente'
                    session['carrito'] = []
                    return redirect(url_for('ver_tienda'))
                else:
                    return render_template('login.html', error="Usuario o contraseña de cliente incorrectos.")
            except Exception as e:
                return f"<h1>Error</h1><p>{str(e)}</p>"
        
        elif tipo_usuario == 'empleado':
            try:
                conexion = conectar_bd()
                cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
                cursor.execute("SELECT nombre, rol FROM empleados WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
                empleado = cursor.fetchone()
                cursor.close()
                conexion.close()
                
                if empleado:
                    session['usuario'] = empleado['nombre']
                    session['rol'] = empleado['rol']
                    return redirect(url_for('panel_vendedor'))
                else:
                    return render_template('login.html', error="Usuario o contraseña de empleado incorrectos.")
            except Exception as e:
                return f"<h1>Error</h1><p>{str(e)}</p>"
                
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form['nombre']
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        try:
            conexion = conectar_bd()
            cursor = conexion.cursor()
            cursor.execute("INSERT INTO clientes_web (nombre, usuario, contrasena) VALUES (%s, %s, %s)", (nombre, usuario, contrasena))
            conexion.commit()
            cursor.execute("SELECT lastval()")
            id_nuevo = cursor.fetchone()[0]
            cursor.close()
            conexion.close()
            
            session['id_usuario'] = id_nuevo
            session['usuario'] = nombre
            session['rol'] = 'Cliente'
            session['carrito'] = []
            return redirect(url_for('ver_tienda'))
        except Exception:
            return render_template('registro.html', error="El usuario ya existe o hubo un problema.")
    return render_template('registro.html')

@app.route('/tienda')
def ver_tienda():
    if 'usuario' not in session:
        return redirect(url_for('login'))
        
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual FROM productos")
        lista_productos = cursor.fetchall()
        
        cursor.execute("""
            SELECT v.id_venta, v.fecha_hora, p.nombre_producto, v.total, c.nombre AS nombre_cliente
            FROM ventas v
            JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
            JOIN productos p ON dv.id_producto = p.id_producto
            LEFT JOIN clientes_web c ON v.id_empleado = c.id_cliente
            ORDER BY v.id_venta DESC LIMIT 5
        """)
        historial = cursor.fetchall()
        cursor.close()
        conexion.close()
        
        total_carrito = sum(item['precio'] * item['cantidad'] for item in session.get('carrito', []))
        amount_items = sum(item['cantidad'] for item in session.get('carrito', []))
        
        return render_template('interfaz.html', 
                               productos=lista_productos, 
                               historial=historial,
                               nombre_usuario=session['usuario'], 
                               carrito=session.get('carrito', []),
                               total_carrito=total_carrito,
                               cantidad_items=amount_items)
    except Exception as e:
        return f"<h1>Error al cargar</h1><p>{str(e)}</p>"

@app.route('/agregar_carrito', methods=['POST'])
def agregar_carrito():
    if 'carrito' not in session:
        session['carrito'] = []
    id_producto = request.form['id_producto']
    nombre = request.form['nombre_producto']
    precio = float(request.form['precio'])
    
    carrito = session['carrito']
    encontrado = False
    for item in carrito:
        if str(item['id_producto']) == str(id_producto):
            item['cantidad'] += 1
            encontrado = True
            break
            
    if not encontrado:
        carrito.append({'id_producto': id_producto, 'nombre': nombre, 'precio': precio, 'cantidad': 1})
        
    session['carrito'] = carrito
    return redirect(url_for('ver_tienda'))

@app.route('/vaciar_carrito')
def vaciar_carrito():
    session['carrito'] = []
    return redirect(url_for('ver_tienda'))

@app.route('/pagar_carrito', methods=['POST'])
def pagar_carrito():
    if 'usuario' not in session or not session.get('carrito'):
        return redirect(url_for('ver_tienda'))
        
    fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    carrito = session['carrito']
    total_compra = sum(item['precio'] * item['cantidad'] for item in carrito)
    id_cliente_actual = session.get('id_usuario', 1)
    
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        sql_venta = "INSERT INTO ventas (fecha_hora, forma_pago, descuento, total, id_empleado) VALUES (%s, 'Efectivo', 0.00, %s, %s)"
        cursor.execute(sql_venta, (fecha_actual, total_compra, id_cliente_actual))
        cursor.execute("SELECT lastval()")
        id_nueva_venta = cursor.fetchone()[0]
        
        for item in carrito:
            sql_details = "INSERT INTO detalle_ventas (id_venta, id_producto, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql_details, (id_nueva_venta, item['id_producto'], item['cantidad'], item['precio']))
            
            sql_stock = "UPDATE productos SET stock_actual = stock_actual - %s WHERE id_producto = %s"
            cursor.execute(sql_stock, (item['cantidad'], item['id_producto']))
            
        conexion.commit()
        cursor.close()
        conexion.close()
        session['carrito'] = []
        return redirect(url_for('ver_tienda'))
    except Exception as e:
        return f"<h1>Error al procesar el pago</h1><p>{str(e)}</p>"

@app.route('/vendedor')
def panel_vendedor():
    if 'usuario' not in session or session['rol'] == 'Cliente':
        return "<h1>⛔ Acceso Denegado</h1>"
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual FROM productos")
        productos = cursor.fetchall()
        
        cursor.execute("""
            SELECT v.id_venta, v.fecha_hora, p.nombre_producto, v.total, c.nombre AS nombre_cliente
            FROM ventas v
            JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
            JOIN productos p ON dv.id_producto = p.id_producto
            LEFT JOIN clientes_web c ON v.id_empleado = c.id_cliente
            ORDER BY v.id_venta DESC
        """)
        todas_ventas = cursor.fetchall()
        cursor.close()
        conexion.close()
        return render_template('vendedor.html', ventas=todas_ventas, productos=productos, nombre_empleado=session['usuario'], rol=session['rol'])
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>"

@app.route('/actualizar_producto', methods=['POST'])
def actualizar_producto():
    if 'usuario' not in session or session['rol'] == 'Cliente':
        return "<h1>⛔ Acceso Denegado</h1>"
    id_producto = request.form['id_producto']
    nuevo_precio = float(request.form['precio'])
    nuevo_stock = int(request.form['stock'])
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("UPDATE productos SET precio_venta_actual = %s, stock_actual = %s WHERE id_producto = %s", (nuevo_precio, nuevo_stock, id_producto))
        conexion.commit()
        cursor.close()
        conexion.close()
        return redirect(url_for('panel_vendedor'))
    except Exception as e:
        return f"<h1>Error al actualizar</h1><p>{str(e)}</p>"

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)

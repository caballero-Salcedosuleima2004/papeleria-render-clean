from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_suleima'

def conectar_bd():
    url_bd = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url_bd, sslmode='require')

# === ✨ FUNCIÓN AUTOMÁTICA PARA CREAR TODAS LAS TABLAS Y REGISTROS COMPLETOS ===
def crear_tablas_automaticas():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        # 1. Tabla: Categorias
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categorias (
                id_categoria INT PRIMARY KEY,
                nombre_categoria VARCHAR(50) NOT NULL
            );
        """)

        # 2. Tabla de Clientes Web
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes_web (
                id_cliente SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                usuario VARCHAR(50) UNIQUE,
                contrasena VARCHAR(255)
            );
        """)

        # 3. Tabla de Empleados
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS empleados (
                id_empleado INT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(50) NOT NULL,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL
            );
        """)
        
        # 4. Tabla: Proveedores
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS proveedores (
                id_proveedor INT PRIMARY KEY,
                nombre_empresa VARCHAR(100) NOT NULL,
                contacto_nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20) NOT NULL
            );
        """)

        # 5. Tabla de Productos (Estructura oficial extendida)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS productos (
                id_producto INT PRIMARY KEY,
                codigo_barras VARCHAR(50) NOT NULL,
                nombre_producto VARCHAR(100) NOT NULL,
                marca VARCHAR(50) NOT NULL,
                unidad_medida VARCHAR(20) NOT NULL,
                stock_actual INT NOT NULL,
                stock_minimo INT NOT NULL,
                precio_venta_actual NUMERIC(10, 2) NOT NULL,
                estado INT NOT NULL,
                id_categoria INT NOT NULL,
                FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
            );
        """)

        # 6. Tabla de Ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ventas (
                id_venta SERIAL PRIMARY KEY,
                fecha_hora TIMESTAMP,
                forma_pago VARCHAR(50),
                descuento NUMERIC(10, 2),
                total NUMERIC(10, 2),
                id_empleado INT
            );
        """)

        # 7. Tabla de Detalle Ventas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_ventas (
                id_detalle SERIAL PRIMARY KEY,
                id_venta INT,
                id_producto INT,
                cantidad INT,
                precio_unitario NUMERIC(10, 2),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            );
        """)

        # 8. Tabla: Compras
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS compras (
                id_compra INT PRIMARY KEY,
                fecha_compra TIMESTAMP NOT NULL,
                total_compra NUMERIC(10, 2) NOT NULL,
                id_proveedor INT NOT NULL,
                id_empleado INT NOT NULL,
                FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor),
                FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
            );
        """)

        # 9. Tabla: Detalle_Compras
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detalle_compras (
                id_detalle_compra INT PRIMARY KEY,
                id_compra INT NOT NULL,
                id_producto INT NOT NULL,
                cantidad INT NOT NULL,
                costo_unitario NUMERIC(10, 2) NOT NULL,
                FOREIGN KEY (id_compra) REFERENCES compras(id_compra),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            );
        """)

        # 10. Tabla: Ajuste_Inventario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ajuste_inventario (
                id_ajuste INT PRIMARY KEY,
                fecha_ajuste TIMESTAMP NOT NULL,
                tipo VARCHAR(20) NOT NULL,
                cantidad INT NOT NULL,
                motivo VARCHAR(255) NOT NULL,
                id_producto INT NOT NULL,
                id_empleado INT NOT NULL,
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
                FOREIGN KEY (id_empleado) REFERENCES empleados(id_empleado)
            );
        """)
        
        # --- 📥 INSERTAR DATOS REQUERIDOS ---

        # 1. Insertar Categorias
        cursor.execute("SELECT COUNT(*) FROM categorias;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO categorias (id_categoria, nombre_categoria) VALUES
                (1, 'Cuadernos y Libretas'), (2, 'Escritura y Corrección'), (3, 'Papel e Impresión'),
                (4, 'Dibujo y Arte'), (5, 'Archiveros y Carpetas'), (6, 'Pegamentos y Cintas'),
                (7, 'Geometría y Reglas'), (8, 'Servicios Digitales'), (9, 'Oficina General'), (10, 'Regalos y Envolturas');
            """)

        # 2. Insertar Empleados
        cursor.execute("SELECT COUNT(*) FROM empleados;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO empleados (id_empleado, nombre, rol, usuario, contrasena) VALUES
                (1, 'Luis Ramirez Torres', 'Propietario', 'luis_owner', 'admin123'),
                (2, 'Andres Hernandez', 'Analista', 'andres_ana', 'analista2026'),
                (3, 'Juan Perez', 'Mostrador', 'juanp', 'mostrador1'),
                (4, 'Maria Gomez', 'Mostrador', 'mariag', 'mostrador2'),
                (5, 'Carlos Lopez', 'Mostrador', 'carlosl', 'pass4'),
                (6, 'Ana Martinez', 'Mostrador', 'anam', 'pass5'),
                (7, 'Pedro Sanchez', 'Almacen', 'pedros', 'pass6'),
                (8, 'Laura Diaz', 'Mostrador', 'laurad', 'pass7'),
                (9, 'Jorge Rodriguez', 'Mostrador', 'jorger', 'pass8'),
                (10, 'Sofia Hernandez', 'Mostrador', 'sofiah', 'pass9');
            """)
            # Agregar accesos anteriores como empleados compatibles por si los usas
            cursor.execute("INSERT INTO empleados (id_empleado, nombre, rol, usuario, contrasena) VALUES (11, 'Suleima', 'Administrador', 'suleima_s', '1234') ON CONFLICT DO NOTHING;")

        # 3. Insertar Proveedores
        cursor.execute("SELECT COUNT(*) FROM proveedores;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO proveedores (id_proveedor, nombre_empresa, contacto_nombre, telefono) VALUES
                (1, 'Distribuidora Escolar S.A.', 'Roberto Gomez', '555-1234'),
                (2, 'Papeles del Centro', 'Alicia Meza', '555-5678'),
                (3, 'Scribe Mexico', 'Fernando Ruiz', '555-9012'),
                (4, 'Articulos de Oficina Monterrey', 'Laura Pena', '811-3456'),
                (5, 'Plastigraf Papelerias', 'Miguel Angel', '555-7890'),
                (6, 'Bic de Mexico', 'Elena Torres', '555-2345'),
                (7, 'Pegamentos Selectos', 'Hugo Chavez', '555-6789'),
                (8, 'Impresiones y Tintas Express', 'Diana Vazquez', '555-0123'),
                (9, 'Mayorista Pedregal', 'Raul Castro', '555-4567'),
                (10, 'Accesorios Escolares Estrella', 'Patricia Solis', '555-8901');
            """)

        # 4. Insertar Productos Completos
        cursor.execute("SELECT COUNT(*) FROM productos;")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO productos (id_producto, codigo_barras, nombre_producto, marca, unidad_medida, stock_actual, stock_minimo, precio_venta_actual, estado, id_categoria) VALUES
                (101, '75010011', 'Cuaderno Profesional Raya 100hj', 'Scribe', 'Pieza', 45, 10, 25.00, 1, 1),
                (102, '75010022', 'Cuaderno Profesional Cuadro C 100hj', 'Scribe', 'Pieza', 8, 10, 25.00, 1, 1),
                (103, '75010033', 'Pluma Punto Mediano Negro', 'Bic', 'Pieza', 150, 20, 7.50, 1, 2),
                (104, '75010044', 'Caja de Plumas Punto Mediano Azul c/12', 'Bic', 'Paquete', 25, 5, 80.00, 1, 2),
                (105, '75010055', 'Paquete Hojas Bond Carta c/500', 'Navator', 'Paquete', 30, 8, 95.00, 1, 3),
                (106, '75010066', 'Caja de Colores de Madera c/24', 'Prismacolor', 'Pieza', 15, 5, 140.00, 1, 4),
                (107, '75010077', 'Carpeta de Tres Argollas 1 pulg', 'Lefort', 'Pieza', 12, 4, 45.00, 1, 5),
                (108, '75010088', 'Lapiz Adhesivo 21g', 'Pritt', 'Pieza', 60, 15, 18.50, 1, 6),
                (109, 'SRV001', 'Copia Fotostatica TamaNo Carta', 'Generico', 'Pieza', 9999, 0, 1.50, 1, 8),
                (110, '75010100', 'Sacapuntas de Plastico Clasico', 'Generico', 'Pieza', 0, 10, 5.00, 0, 2);
            """)
            
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error al inicializar la base de datos:", e)

crear_tablas_automaticas()
# ============================================================

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
                cursor.execute("SELECT id_empleado, nombre, rol FROM empleados WHERE usuario = %s AND contrasena = %s", (usuario, contrasena))
                empleado = cursor.fetchone()
                cursor.close()
                conexion.close()
                
                if empleado:
                    session['id_usuario'] = empleado['id_empleado']
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
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual FROM productos WHERE estado = 1 ORDER BY id_producto")
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
        
    fecha_actual = datetime.now()
    carrito = session['carrito']
    total_compra = sum(item['precio'] * item['cantidad'] for item in carrito)
    id_empleado_actual = session.get('id_usuario', 3) # Asigna un ID de empleado de mostrador por defecto
    
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        sql_venta = "INSERT INTO ventas (fecha_hora, forma_pago, descuento, total, id_empleado) VALUES (%s, 'Efectivo', 0.00, %s, %s) RETURNING id_venta"
        cursor.execute(sql_venta, (fecha_actual, total_compra, id_empleado_actual))
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
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual FROM productos ORDER BY id_producto")
        productos = cursor.fetchall()
        
        cursor.execute("""
            SELECT v.id_venta, v.fecha_hora, p.nombre_producto, v.total, e.nombre AS nombre_cliente
            FROM ventas v
            JOIN detalle_ventas dv ON v.id_venta = dv.id_venta
            JOIN productos p ON dv.id_producto = p.id_producto
            LEFT JOIN empleados e ON v.id_empleado = e.id_empleado
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

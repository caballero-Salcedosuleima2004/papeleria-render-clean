from flask import Flask, render_template, request, redirect, session, url_for
import psycopg2
import psycopg2.extras
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'clave_secreta_suleima'
NOMBRE_PAPELERIA = 'Papelería Estudiante Feliz'

def conectar_bd():
    url_bd = os.environ.get('DATABASE_URL')
    return psycopg2.connect(url_bd, sslmode='require')

# === ✨ FUNCIÓN AUTOMÁTICA PARA CREAR TODAS LAS TABLAS Y REGISTROS COMPLETOS ===
def crear_tablas_automaticas():
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        # 🔥 ELIMINADOR TOTAL OBLIGATORIO: Forzamos la limpieza absoluta en cada reinicio
        cursor.execute("DROP TABLE IF EXISTS detalle_ventas CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS ventas CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS productos CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS empleados CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS clientes_web CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS proveedores CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS categorias CASCADE;")
        
        # 1. Tabla: Categorias
        cursor.execute("""
            CREATE TABLE categorias (
                id_categoria INT PRIMARY KEY,
                nombre_categoria VARCHAR(50) NOT NULL
            );
        """)

        # 2. Tabla de Clientes Web
        cursor.execute("""
            CREATE TABLE clientes_web (
                id_cliente SERIAL PRIMARY KEY,
                nombre VARCHAR(100),
                usuario VARCHAR(50) UNIQUE,
                contrasena VARCHAR(255)
            );
        """)

        # 3. Tabla de Empleados
        cursor.execute("""
            CREATE TABLE empleados (
                id_empleado INT PRIMARY KEY,
                nombre VARCHAR(100) NOT NULL,
                rol VARCHAR(50) NOT NULL,
                usuario VARCHAR(50) UNIQUE NOT NULL,
                contrasena VARCHAR(255) NOT NULL
            );
        """)
        
        # 4. Tabla: Proveedores
        cursor.execute("""
            CREATE TABLE proveedores (
                id_proveedor INT PRIMARY KEY,
                nombre_empresa VARCHAR(100) NOT NULL,
                contacto_nombre VARCHAR(100) NOT NULL,
                telefono VARCHAR(20) NOT NULL
            );
        """)

        # 5. Tabla de Productos (Usando TEXT para soportar las URLs largas de Unsplash)
        cursor.execute("""
            CREATE TABLE productos (
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
                imagen_url TEXT DEFAULT 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=400',
                FOREIGN KEY (id_categoria) REFERENCES categorias(id_categoria)
            );
        """)

        # 6. Tabla de Ventas
        cursor.execute("""
            CREATE TABLE ventas (
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
            CREATE TABLE detalle_ventas (
                id_detalle SERIAL PRIMARY KEY,
                id_venta INT,
                id_producto INT,
                cantidad INT,
                precio_unitario NUMERIC(10, 2),
                FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
            );
        """)
        
        # --- 📥 INSERTAR DATOS REQUERIDOS ---

        # Insertar Categorias
        cursor.execute("""
            INSERT INTO categorias (id_categoria, nombre_categoria) VALUES
            (1, 'Cuadernos y Libretas'), (2, 'Escritura y Corrección'), (3, 'Papel e Impresión'),
            (4, 'Dibujo y Arte'), (5, 'Archiveros y Carpetas'), (6, 'Pegamentos y Cintas'),
            (7, 'Geometría y Reglas'), (8, 'Servicios Digitales'), (9, 'Oficina General'), (10, 'Regalos y Envolturas');
        """)
        
        # Insertar Empleados
        cursor.execute("""
            INSERT INTO empleados (id_empleado, nombre, rol, usuario, contrasena) VALUES
            (1, 'Profesor Andres', 'Propietario', 'andres_a', 'profe123'),
            (2, 'Suleima Salcedo', 'Analista', 'suleima_s', 'sule2026'),
            (3, 'Zoran', 'Mostrador', 'zoran_z', 'zoran123'),
            (4, 'Fatima', 'Mostrador', 'fatima_f', 'fatima123');
        """)

        # Insertar Proveedores
        cursor.execute("""
            INSERT INTO proveedores (id_proveedor, nombre_empresa, contacto_nombre, telefono) VALUES
            (1, 'Distribuidora Escolar S.A.', 'Roberto Gomez', '555-1234'),
            (2, 'Papeles del Centro', 'Alicia Meza', '555-5678'),
            (3, 'Scribe Mexico', 'Fernando Ruiz', '555-9012');
        """)

        # Catálogo 100% corregido con imágenes reales de papelería
        cursor.execute("""
            INSERT INTO productos (id_producto, codigo_barras, nombre_producto, marca, unidad_medida, stock_actual, stock_minimo, precio_venta_actual, estado, id_categoria, imagen_url) VALUES
            (101, '75010011', 'Cuaderno Profesional Raya 100hj', 'Scribe', 'Pieza', 45, 10, 25.00, 1, 1, 'https://images.unsplash.com/photo-1531346878377-a5be20888e57?w=400&q=80'),
            (102, '75010022', 'Cuaderno Profesional Cuadro C 100hj', 'Scribe', 'Pieza', 35, 10, 25.00, 1, 1, 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400&q=80'),
            (103, '75010033', 'Libreta Italiana Raya 100hj', 'Estrella', 'Pieza', 20, 5, 18.50, 1, 1, 'https://images.unsplash.com/photo-1510172951991-856a654063f9?w=400&q=80'),
            (104, '75010044', 'Pluma Punto Mediano Negro', 'Bic', 'Pieza', 150, 20, 7.50, 1, 2, 'https://images.unsplash.com/photo-1583485088034-697b5bc54ccd?w=400&q=80'),
            (105, '75010055', 'Caja de Plumas Azul c/12', 'Bic', 'Paquete', 25, 5, 80.00, 1, 2, 'https://images.unsplash.com/photo-1511556532299-8f662fc26c06?w=400&q=80'),
            (106, '75010066', 'Lápiz Infinito Grafito HB', 'Dixon', 'Pieza', 80, 15, 6.00, 1, 2, 'https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=400&q=80'),
            (107, '75010077', 'Platón Marcador de Textos Amarillo', 'Sharpie', 'Pieza', 40, 10, 15.50, 1, 2, 'https://images.unsplash.com/photo-1569003339405-ea396a5a8a90?w=400&q=80'),
            (108, '75010088', 'Corrector en Cinta Líquida', 'Pentel', 'Pieza', 30, 5, 22.00, 1, 2, 'https://images.unsplash.com/photo-1544816155-12df9643f363?w=400&q=80'),
            (109, '75010099', 'Paquete Hojas Bond Carta c/500', 'Navator', 'Paquete', 30, 8, 95.00, 1, 3, 'https://images.unsplash.com/photo-1603481588273-2f908a9a7a1b?w=400&q=80'),
            (110, '75010101', 'Block de Notas Adhesivas Post-it', '3M', 'Pieza', 50, 10, 28.00, 1, 3, 'https://images.unsplash.com/photo-1586075010923-2dd4570fb338?w=400&q=80'),
            (111, '75010112', 'Caja de Colores de Madera c/24', 'Prismacolor', 'Pieza', 15, 5, 140.00, 1, 4, 'https://images.unsplash.com/photo-1602738328654-51ab2ae6c4ff?w=400&q=80'),
            (112, '75010123', 'Acuarelas Escolares 12 Pastillas', 'Pelikan', 'Pieza', 18, 4, 45.00, 1, 4, 'https://images.unsplash.com/photo-1513364776144-60967b0f800f?w=400&q=80'),
            (113, '75010134', 'Plumones Lavables c/12', 'Crayola', 'Paquete', 22, 6, 75.00, 1, 4, 'https://images.unsplash.com/photo-1562259949-e8e7689d7828?w=400&q=80'),
            (114, '75010145', 'Carpeta de Tres Argollas 1 pulg', 'Lefort', 'Pieza', 12, 4, 45.00, 1, 5, 'https://images.unsplash.com/photo-1610563166150-b34df4f3bcd6?w=400&q=80'),
            (115, '75010156', 'Folder Tamaño Carta Azul c/10', 'Generico', 'Paquete', 40, 10, 20.00, 1, 5, 'https://images.unsplash.com/photo-1595515106969-1ce29566ff1c?w=400&q=80'),
            (116, '75010167', 'Lápiz Adhesivo 21g', 'Pritt', 'Pieza', 60, 15, 18.50, 1, 6, 'https://images.unsplash.com/photo-1533227268212-75b790d10f44?w=400&q=80'),
            (117, '75010178', 'Pegamento Blanco Líquido 120g', 'Elmers', 'Pieza', 25, 5, 24.00, 1, 6, 'https://images.unsplash.com/photo-1607604276583-eef5d076aa5f?w=400&q=80'),
            (118, '75010189', 'Cinta Adhesiva Transparente', 'Tuck', 'Pieza', 45, 8, 12.00, 1, 6, 'https://images.unsplash.com/photo-1617791160505-6f006e121980?w=400&q=80'),
            (119, '75010190', 'Juego de Geometría Plástico', 'Baco', 'Pieza', 20, 5, 38.00, 1, 7, 'https://images.unsplash.com/photo-1509228468518-180dd4864904?w=400&q=80'),
            (120, '75010201', 'Regla de Aluminio 30 cm', 'Maped', 'Pieza', 15, 5, 29.50, 1, 7, 'https://images.unsplash.com/photo-1616628188550-808682f3926d?w=400&q=80'),
            (121, 'SRV001', 'Copia Fotostática Tamaño Carta', 'Generico', 'Pieza', 9999, 0, 1.50, 1, 8, 'https://images.unsplash.com/photo-1612815154858-60aa4c59eaa6?w=400&q=80'),
            (122, 'SRV002', 'Impresión Color Láser', 'HP', 'Pieza', 9999, 0, 5.00, 1, 8, 'https://images.unsplash.com/photo-1588702547919-26089e690ecc?w=400&q=80'),
            (123, '75010223', 'Calculadora Científica 240 fun', 'Casio', 'Pieza', 10, 2, 299.00, 1, 9, 'https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=400&q=80'),
            (124, '75010234', 'Tijeras Escolares Acero Inox', 'Barrilito', 'Pieza', 30, 5, 16.00, 1, 9, 'https://images.unsplash.com/photo-1519751138087-5bf79df52d5b?w=400&q=80'),
            (125, '75010245', 'Goma de Borrar Migajón M20', 'Factis', 'Pieza', 100, 20, 5.50, 1, 9, 'https://images.unsplash.com/photo-1588702547923-7093a6c3ba33?w=400&q=80'),
            (126, '75010256', 'Sacapuntas de Metal Doble', 'Maped', 'Pieza', 55, 10, 12.00, 1, 9, 'https://images.unsplash.com/photo-1601987177651-8edfe6c20009?w=400&q=80'),
            (127, '75010267', 'Engrapadora de Media Tira', 'Pilot', 'Pieza', 8, 2, 85.00, 1, 9, 'https://images.unsplash.com/photo-1589187775328-882e91b314f1?w=400&q=80'),
            (128, '75010278', 'Caja de Clips Estándar c/100', 'Acme', 'Paquete', 40, 10, 14.00, 1, 9, 'https://images.unsplash.com/photo-1623945191299-da18fba82e5b?w=400&q=80'),
            (129, '75010289', 'Pliego Papel Regalo Diseños', 'Generico', 'Pieza', 100, 15, 10.00, 1, 10, 'https://images.unsplash.com/photo-1549465220-1a8b9238cd48?w=400&q=80'),
            (130, '75010290', 'Moño Celofán Mediano c/10', 'Generico', 'Paquete', 25, 5, 35.00, 1, 10, 'https://images.unsplash.com/photo-1513201099495-a6697ee47407?w=400&q=80');
        """)
            
        conexion.commit()
        cursor.close()
        conexion.close()
    except Exception as e:
        print("Error al inicializar la base de datos:", e)

# 🛑 COMENTADO PARA SIEMPRE: Ya no borrará tus imágenes ni tus usuarios registrados al reiniciar
# crear_tablas_automaticas()
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
        
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual, imagen_url FROM productos WHERE estado = 1 ORDER BY id_producto")
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
        return f"<h1>Error al cargar la tienda</h1><p>{str(e)}</p>"

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
    id_usuario_actual = session.get('id_usuario', None)
    
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        
        sql_venta = "INSERT INTO ventas (fecha_hora, forma_pago, descuento, total, id_empleado) VALUES (%s, 'Efectivo', 0.00, %s, %s) RETURNING id_venta"
        cursor.execute(sql_venta, (fecha_actual, total_compra, id_usuario_actual))
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
        # ✅ Agregado: imagen_url para que cargue los links en tu tabla de vendedor
        cursor.execute("SELECT id_producto, nombre_producto, marca, precio_venta_actual, stock_actual, imagen_url FROM productos ORDER BY id_producto")
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
    nueva_imagen = request.form['imagen_url']
    
    try:
        conexion = conectar_bd()
        cursor = conexion.cursor()
        cursor.execute("""
            UPDATE productos 
            SET precio_venta_actual = %s, stock_actual = %s, imagen_url = %s 
            WHERE id_producto = %s
        """, (nuevo_precio, nuevo_stock, nueva_imagen, id_producto))
        
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

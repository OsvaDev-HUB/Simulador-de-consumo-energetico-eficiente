import os
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev_key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar Base de Datos y Login
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ============ MODELOS DE DATOS ============

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    # Relación con aparatos
    aparatos = db.relationship('Aparato', backref='owner', lazy=True, cascade="all, delete-orphan")

class Aparato(db.Model):
    __tablename__ = 'aparatos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    potencia = db.Column(db.Float, nullable=False)
    horas = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)

# Crear tablas si no existen
with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"Error al conectar con PostgreSQL: {e}")
        print("Asegúrate de que PostgreSQL esté corriendo y la base de datos exista.")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============ LÓGICA DE NEGOCIO (REFACTORIZADA) ============

def calcular_consumo_aparato(potencia_w, horas_dia):
    """Calcula el consumo mensual en kWh"""
    kwh_dia = (potencia_w * horas_dia) / 1000
    return kwh_dia

def obtener_top_consumidores_db(user_id, num_top=3):
    """Obtiene los aparatos que más consumen desde la DB"""
    aparatos = Aparato.query.filter_by(user_id=user_id).all()
    consumos = []
    for a in aparatos:
        consumo_mes = calcular_consumo_aparato(a.potencia, a.horas) * 30
        consumos.append({'id': a.id, 'nombre': a.nombre, 'consumo': consumo_mes})
    
    return sorted(consumos, key=lambda x: x['consumo'], reverse=True)[:num_top]

# ============ RUTAS DE AUTENTICACIÓN ============

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('El nombre de usuario ya existe', 'error')
            return redirect(url_for('registro'))
        
        hashed_pw = generate_password_hash(password)
        nuevo_usuario = User(username=username, password_hash=hashed_pw)
        db.session.add(nuevo_usuario)
        db.session.commit()
        
        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('login'))
        
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('inicio'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('inicio'))
        
        flash('Usuario o contraseña incorrectos', 'error')
        
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# ============ RUTAS DE LA APLICACIÓN ============

@app.route('/')
def inicio():
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/aparatos')
@login_required
def aparatos_page():
    return render_template('aparatos.html')

@app.route('/analisis')
@login_required
def analisis_page():
    return render_template('analisis.html')

@app.route('/simulacion')
@login_required
def simulacion_page():
    return render_template('simulacion.html')

@app.route('/recomendaciones')
@login_required
def recomendaciones_page():
    return render_template('recomendaciones.html')

# ============ API ENDPOINTS ============

@app.route('/api/aparatos', methods=['GET'])
@login_required
def obtener_aparatos():
    aparatos = Aparato.query.filter_by(user_id=current_user.id).all()
    return jsonify([{
        'id': a.id,
        'nombre': a.nombre,
        'potencia': a.potencia,
        'horas': a.horas
    } for a in aparatos])

@app.route('/api/aparatos', methods=['POST'])
@login_required
def agregar_aparato():
    data = request.get_json()
    try:
        nuevo = Aparato(
            nombre=data['nombre'],
            potencia=float(data['potencia_w']),
            horas=float(data['horas_dia']),
            user_id=current_user.id
        )
        db.session.add(nuevo)
        db.session.commit()
        return jsonify({'mensaje': 'Aparato agregado correctamente'})
    except Exception as e:
        return jsonify({'mensaje': f'Error: {str(e)}'}), 400

@app.route('/api/aparatos/<int:id>', methods=['DELETE'])
@login_required
def eliminar_aparato(id):
    aparato = Aparato.query.filter_by(id=id, user_id=current_user.id).first()
    if aparato:
        db.session.delete(aparato)
        db.session.commit()
        return jsonify({'mensaje': 'Aparato eliminado'})
    return jsonify({'mensaje': 'No encontrado'}), 404

@app.route('/api/aparatos/<int:id>', methods=['PUT'])
@login_required
def editar_aparato(id):
    data = request.get_json()
    aparato = Aparato.query.filter_by(id=id, user_id=current_user.id).first()
    if aparato:
        aparato.nombre = data['nombre']
        aparato.potencia = float(data['potencia_w'])
        aparato.horas = float(data['horas_dia'])
        db.session.commit()
        return jsonify({'mensaje': 'Aparato actualizado'})
    return jsonify({'mensaje': 'No encontrado'}), 404

@app.route('/api/consumo', methods=['GET'])
@login_required
def calcular_consumo():
    aparatos = Aparato.query.filter_by(user_id=current_user.id).all()
    if not aparatos:
        return jsonify({
            'aparatos': [],
            'total_diario_kwh': 0,
            'total_mensual_kwh': 0,
            'costo_mensual_clp': 0
        })

    resultado_aparatos = []
    total_diario = 0
    
    for a in aparatos:
        kwh_dia = (a.potencia * a.horas) / 1000
        kwh_mes = kwh_dia * 30
        costo_mes = kwh_mes * 120 # Precio estimado
        
        total_diario += kwh_dia
        resultado_aparatos.append({
            'nombre': a.nombre,
            'potencia_w': a.potencia,
            'horas_dia': a.horas,
            'kwh_dia': kwh_dia,
            'kwh_mes': kwh_mes,
            'costo_mes': costo_mes
        })
    
    total_mensual = total_diario * 30
    costo_mensual = total_mensual * 120
    
    return jsonify({
        'aparatos': resultado_aparatos,
        'total_diario_kwh': total_diario,
        'total_mensual_kwh': total_mensual,
        'costo_mensual_clp': costo_mensual
    })

@app.route('/api/top-consumidores')
@login_required
def top_consumidores():
    top = obtener_top_consumidores_db(current_user.id, 3)
    total_data = calcular_consumo().get_json()
    total_mensual = total_data['total_mensual_kwh']
    
    resultado = []
    for rank, item in enumerate(top, 1):
        porcentaje = (item['consumo'] / total_mensual * 100) if total_mensual > 0 else 0
        resultado.append({
            'rank': rank,
            'nombre': item['nombre'],
            'kwh_mes': item['consumo'],
            'porcentaje': porcentaje
        })
    
    return jsonify(resultado)

@app.route('/api/simulacion', methods=['POST'])
@login_required
def simular_reduccion():
    data = request.get_json()
    reduccion = data.get('porcentaje_reduccion', 0) / 100
    
    cons_data = calcular_consumo().get_json()
    original = cons_data['total_mensual_kwh']
    nuevo = original * (1 - (reduccion * 0.5)) # Asumimos ahorro en el 50% de aparatos
    
    return jsonify({
        'consumo_original': original,
        'consumo_nuevo': nuevo,
        'ahorro_kwh': original - nuevo,
        'ahorro_dinero': (original - nuevo) * 120,
        'ahorro_porcentual': (reduccion * 0.5) * 100
    })

@app.route('/api/recomendaciones')
@login_required
def recomendaciones():
    top = obtener_top_consumidores_db(current_user.id, 3)
    sugerencias = []
    
    for item in top:
        horas_reducidas = 1.0 # Ejemplo
        ahorro_kwh = (item['consumo'] / 30) - ((item['consumo'] / 30) - 1.0) # Simplificado
        sugerencias.append({
            'aparato': item['nombre'],
            'horas_recomendada': 2.0,
            'ahorro_dinero': 5000
        })
    
    return jsonify(sugerencias)

@app.route('/api/cargar-ejemplo', methods=['POST'])
@login_required
def cargar_ejemplo():
    # Eliminar actuales si se desea
    ejemplos = [
        {'nombre': 'Refrigerador', 'potencia': 250, 'horas': 24},
        {'nombre': 'Televisor', 'potencia': 150, 'horas': 5},
        {'nombre': 'Aire Acondicionado', 'potencia': 1500, 'horas': 4}
    ]
    for ej in ejemplos:
        nuevo = Aparato(nombre=ej['nombre'], potencia=ej['potencia'], horas=ej['horas'], user_id=current_user.id)
        db.session.add(nuevo)
    db.session.commit()
    return jsonify({'mensaje': 'Ejemplos cargados'})

if __name__ == '__main__':
    app.run(debug=True)
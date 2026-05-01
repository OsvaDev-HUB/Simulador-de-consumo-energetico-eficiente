from flask import Flask, render_template, request, jsonify
from datetime import datetime

# Configuracion basica
app = Flask(__name__)
PRECIO_KWH = 262.0

# Lista para guardar los aparatos
aparatos_lista = []

# ============ FUNCIONES DE CALCULO ============

def calcular_consumo_aparato(potencia, horas):
    """Calcula el consumo diario de un aparato en kWh"""
    kwh_dia = (potencia * horas) / 1000
    return kwh_dia

def calcular_costo(kwh, precio):
    """Calcula el costo en pesos"""
    return kwh * precio

def obtener_top_consumidores(num_top):
    """Identifica los aparatos que mas consumen"""
    if len(aparatos_lista) == 0:
        return []
    
    consumos = []
    for i, aparato in enumerate(aparatos_lista):
        kwh_mes = calcular_consumo_aparato(aparato['potencia'], aparato['horas']) * 30
        consumos.append({'indice': i, 'consumo': kwh_mes})
    
    consumos_ordenados = sorted(consumos, key=lambda x: x['consumo'], reverse=True)
    return consumos_ordenados[:num_top]

# ============ RUTAS DE LA APLICACION ============

@app.route('/')
def inicio():
    """Pagina principal - Dashboard"""
    return render_template('dashboard.html')

@app.route('/aparatos')
def aparatos_page():
    """Pagina de gestion de aparatos"""
    return render_template('aparatos.html')

@app.route('/analisis')
def analisis_page():
    """Pagina de analisis de consumo"""
    return render_template('analisis.html')

@app.route('/simulacion')
def simulacion_page():
    """Pagina de simulacion"""
    return render_template('simulacion.html')

@app.route('/recomendaciones')
def recomendaciones_page():
    """Pagina de recomendaciones"""
    return render_template('recomendaciones.html')

@app.route('/api/aparatos', methods=['GET'])
def obtener_aparatos():
    """Retorna la lista de aparatos"""
    return jsonify(aparatos_lista)

@app.route('/api/aparatos', methods=['POST'])
def agregar_aparato():
    """Agrega un nuevo aparato"""
    datos = request.get_json()
    
    nombre = datos.get('nombre', '').strip()
    potencia = float(datos.get('potencia_w', 0))
    horas = float(datos.get('horas_dia', 0))
    
    if not nombre or potencia <= 0 or horas <= 0:
        return jsonify({'error': 'Datos invalidos'}), 400
    
    nuevo_aparato = {
        'id': len(aparatos_lista),
        'nombre': nombre,
        'potencia': potencia,
        'horas': horas
    }
    aparatos_lista.append(nuevo_aparato)
    
    return jsonify({'mensaje': f'Aparato {nombre} agregado'}), 201

@app.route('/api/aparatos/<int:id>', methods=['DELETE'])
def eliminar_aparato(id):
    """Elimina un aparato"""
    if id >= len(aparatos_lista):
        return jsonify({'error': 'Aparato no encontrado'}), 404
    
    nombre = aparatos_lista[id]['nombre']
    aparatos_lista.pop(id)
    
    for i, aparato in enumerate(aparatos_lista):
        aparato['id'] = i
    
    return jsonify({'mensaje': f'Aparato {nombre} eliminado'})

@app.route('/api/aparatos/<int:id>', methods=['PUT'])
def editar_aparato(id):
    """Edita un aparato"""
    if id >= len(aparatos_lista):
        return jsonify({'error': 'Aparato no encontrado'}), 404
    
    datos = request.get_json()
    nombre = datos.get('nombre', '').strip()
    potencia = float(datos.get('potencia_w', 0))
    horas = float(datos.get('horas_dia', 0))
    
    if not nombre or potencia <= 0 or horas <= 0:
        return jsonify({'error': 'Datos invalidos'}), 400
    
    aparatos_lista[id]['nombre'] = nombre
    aparatos_lista[id]['potencia'] = potencia
    aparatos_lista[id]['horas'] = horas
    
    return jsonify({'mensaje': f'Aparato {nombre} actualizado'})

@app.route('/api/consumo', methods=['GET'])
def calcular_consumo():
    """Calcula el consumo total"""
    if len(aparatos_lista) == 0:
        return jsonify({'error': 'No hay aparatos'}), 400
    
    aparatos_con_consumo = []
    total_diario = 0
    
    for aparato in aparatos_lista:
        kwh_dia = calcular_consumo_aparato(aparato['potencia'], aparato['horas'])
        kwh_mes = kwh_dia * 30
        costo_mes = calcular_costo(kwh_mes, PRECIO_KWH)
        
        aparatos_con_consumo.append({
            'nombre': aparato['nombre'],
            'potencia_w': aparato['potencia'],
            'horas_dia': aparato['horas'],
            'kwh_dia': kwh_dia,
            'kwh_mes': kwh_mes,
            'costo_mes': costo_mes
        })
        
        total_diario += kwh_dia
    
    total_mensual = total_diario * 30
    costo_total = calcular_costo(total_mensual, PRECIO_KWH)
    
    return jsonify({
        'aparatos': aparatos_con_consumo,
        'total_diario_kwh': total_diario,
        'total_mensual_kwh': total_mensual,
        'costo_mensual_clp': costo_total
    })

@app.route('/api/top-consumidores', methods=['GET'])
def top_consumidores():
    """Obtiene los 3 aparatos que mas consumen"""
    top = obtener_top_consumidores(3)
    
    resultado = []
    total_consumo = sum([calcular_consumo_aparato(a['potencia'], a['horas']) for a in aparatos_lista])
    
    for rank, item in enumerate(top, 1):
        aparato = aparatos_lista[item['indice']]
        kwh_mes = item['consumo']
        porcentaje = (kwh_mes / (total_consumo * 30)) * 100
        
        resultado.append({
            'rank': rank,
            'nombre': aparato['nombre'],
            'kwh_mes': kwh_mes,
            'porcentaje': porcentaje
        })
    
    return jsonify(resultado)

@app.route('/api/simulacion', methods=['POST'])
def simular_reduccion():
    """Simula una reduccion de consumo"""
    if len(aparatos_lista) == 0:
        return jsonify({'error': 'No hay aparatos'}), 400
    
    datos = request.get_json()
    porcentaje = float(datos.get('porcentaje_reduccion', 0))
    
    if not (0 <= porcentaje <= 100):
        return jsonify({'error': 'Porcentaje invalido'}), 400
    
    consumo_original = 0
    for aparato in aparatos_lista:
        consumo_original += calcular_consumo_aparato(aparato['potencia'], aparato['horas']) * 30
    
    top = obtener_top_consumidores(3)
    consumo_nuevo = consumo_original
    
    for item in top:
        aparato = aparatos_lista[item['indice']]
        kwh_mes_actual = calcular_consumo_aparato(aparato['potencia'], aparato['horas']) * 30
        reduccion = kwh_mes_actual * (porcentaje / 100)
        consumo_nuevo -= reduccion
    
    ahorro_kwh = consumo_original - consumo_nuevo
    ahorro_porcentual = (ahorro_kwh / consumo_original) * 100
    ahorro_dinero = calcular_costo(ahorro_kwh, PRECIO_KWH)
    
    return jsonify({
        'consumo_original': consumo_original,
        'consumo_nuevo': consumo_nuevo,
        'ahorro_kwh': ahorro_kwh,
        'ahorro_porcentual': ahorro_porcentual,
        'ahorro_dinero': ahorro_dinero
    })

@app.route('/api/recomendaciones', methods=['GET'])
def recomendaciones():
    """Genera recomendaciones de ahorro"""
    if len(aparatos_lista) == 0:
        return jsonify({'error': 'No hay aparatos'}), 400
    
    top = obtener_top_consumidores(3)
    recomendaciones = []
    
    for item in top:
        aparato = aparatos_lista[item['indice']]
        horas_actual = aparato['horas']
        horas_recomendada = horas_actual * 0.8
        
        kwh_actual = calcular_consumo_aparato(aparato['potencia'], horas_actual) * 30
        kwh_nuevo = calcular_consumo_aparato(aparato['potencia'], horas_recomendada) * 30
        
        ahorro_kwh = kwh_actual - kwh_nuevo
        ahorro_dinero = calcular_costo(ahorro_kwh, PRECIO_KWH)
        
        recomendaciones.append({
            'aparato': aparato['nombre'],
            'horas_actual': horas_actual,
            'horas_recomendada': horas_recomendada,
            'ahorro_kwh': ahorro_kwh,
            'ahorro_dinero': ahorro_dinero
        })
    
    return jsonify(recomendaciones)

@app.route('/api/cargar-ejemplo', methods=['POST'])
def cargar_ejemplo():
    """Carga datos de ejemplo"""
    global aparatos_lista
    aparatos_lista = []
    
    ejemplos = [
        {"nombre": "Refrigerador", "potencia": 80, "horas": 24},
        {"nombre": "Televisor", "potencia": 30, "horas": 4},
        {"nombre": "Lavadora", "potencia": 70, "horas": 1},
        {"nombre": "Iluminacion", "potencia": 15, "horas": 5},
        {"nombre": "Computador", "potencia": 100, "horas": 6},
        {"nombre": "Congelador", "potencia": 120, "horas": 24}
    ]
    
    for i, ejemplo in enumerate(ejemplos):
        aparatos_lista.append({
            'id': i,
            'nombre': ejemplo['nombre'],
            'potencia': ejemplo['potencia'],
            'horas': ejemplo['horas']
        })
    
    return jsonify({'mensaje': 'Datos de ejemplo cargados', 'aparatos': len(aparatos_lista)})

@app.errorhandler(404)
def no_encontrado(e):
    return render_template('error.html', error='Pagina no encontrada'), 404

@app.errorhandler(500)
def error_servidor(e):
    return render_template('error.html', error='Error en el servidor'), 500

if __name__ == '__main__':
    print("Iniciando simulador...")
    print("Abre http://127.0.0.1:5000 en tu navegador")
    app.run(debug=True, host='0.0.0.0', port=5000)
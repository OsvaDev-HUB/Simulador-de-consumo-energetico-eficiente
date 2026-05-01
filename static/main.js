// Variables globales
let graficoInstance = null;

// Configuración de colores para gráficos
const COLORS = {
    primary: '#0ea5e9',
    chart: ['#0ea5e9', '#38bdf8', '#7dd3fc', '#0284c7', '#0369a1', '#0c4a6e', '#bae6fd', '#e0f2fe']
};

// Cuando carga la pagina
document.addEventListener('DOMContentLoaded', () => {
    // Inicializar scroll reveal
    revealOnScroll();
    window.addEventListener('scroll', revealOnScroll);
});

// ============ FUNCIONES DE RESUMEN (HOME) ============

function actualizarResumenHome() {
    // Obtener cantidad de aparatos
    fetch('/api/aparatos')
        .then(r => r.json())
        .then(aparatos => {
            const el = document.getElementById('summary-aparatos');
            if (el) el.textContent = aparatos.length;
        });

    // Obtener consumo total
    fetch('/api/consumo')
        .then(r => r.json())
        .then(data => {
            const el = document.getElementById('summary-consumo');
            if (el) el.textContent = data.total_mensual_kwh.toFixed(1);
        })
        .catch(() => {
            const el = document.getElementById('summary-consumo');
            if (el) el.textContent = "0.0";
        });
}

// ============ FUNCIONES DE APARATOS ============

function cargarAparatos() {
    fetch('/api/aparatos')
        .then(r => r.json())
        .then(aparatos => renderizarAparatos(aparatos))
        .catch(e => mostrarNotificacion('Error al cargar aparatos', 'error'));
}

function renderizarAparatos(aparatos) {
    const contenedor = document.getElementById('lista-aparatos');
    if (!contenedor) return;
    
    if (aparatos.length === 0) {
        contenedor.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-microchip"></i>
                <p>No has añadido ningún aparato todavía.</p>
            </div>
        `;
        return;
    }
    
    contenedor.innerHTML = aparatos.map((aparato, idx) => `
        <div class="aparato-item" style="animation: fadeIn 0.5s ease forwards ${idx * 0.1}s; opacity: 0;">
            <div class="aparato-header">
                <span class="aparato-nombre">${aparato.nombre}</span>
                <div class="aparato-actions">
                    <button onclick="editarAparato(${idx})" class="btn-icon btn-edit" title="Editar">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                    <button onclick="eliminarAparato(${idx})" class="btn-icon btn-delete" title="Eliminar">
                        <i class="fas fa-trash-alt"></i>
                    </button>
                </div>
            </div>
            <div class="aparato-body">
                <div class="aparato-spec">
                    <span class="aparato-spec-label">Potencia</span>
                    <span class="aparato-spec-value">${aparato.potencia} <small>W</small></span>
                </div>
                <div class="aparato-spec">
                    <span class="aparato-spec-label">Uso diario</span>
                    <span class="aparato-spec-value">${aparato.horas.toFixed(1)} <small>h</small></span>
                </div>
            </div>
        </div>
    `).join('');
}

function agregarAparato() {
    const nombre = document.getElementById('nombre-aparato').value.trim();
    const potencia = parseFloat(document.getElementById('potencia-aparato').value);
    const horas = parseFloat(document.getElementById('horas-aparato').value);
    
    if (!nombre || !potencia || !horas || potencia <= 0 || horas <= 0) {
        mostrarNotificacion('Por favor completa todos los campos correctamente', 'error');
        return;
    }
    
    fetch('/api/aparatos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, potencia_w: potencia, horas_dia: horas })
    })
    .then(r => r.json())
    .then(data => {
        mostrarNotificacion(data.mensaje, 'success');
        document.getElementById('nombre-aparato').value = '';
        document.getElementById('potencia-aparato').value = '';
        document.getElementById('horas-aparato').value = '';
        cargarAparatos();
    })
    .catch(e => mostrarNotificacion('Error al agregar aparato', 'error'));
}

function eliminarAparato(id) {
    if (!confirm('¿Seguro que deseas eliminar este dispositivo?')) return;
    
    fetch(`/api/aparatos/${id}`, { method: 'DELETE' })
        .then(r => r.json())
        .then(data => {
            mostrarNotificacion(data.mensaje, 'success');
            cargarAparatos();
        })
        .catch(e => mostrarNotificacion('Error al eliminar', 'error'));
}

function editarAparato(id) {
    const items = document.querySelectorAll('.aparato-item');
    const nombreActual = items[id].querySelector('.aparato-nombre').textContent;
    
    const nombre = prompt('Nombre del aparato:', nombreActual);
    if (nombre === null) return;

    const potenciaStr = prompt('Potencia (watts):', '');
    if (potenciaStr === null) return;
    const potencia = parseFloat(potenciaStr);

    const horasStr = prompt('Horas diarias:', '');
    if (horasStr === null) return;
    const horas = parseFloat(horasStr);

    if (!nombre || isNaN(potencia) || isNaN(horas) || potencia <= 0 || horas <= 0) {
        mostrarNotificacion('Datos inválidos para la edición', 'error');
        return;
    }

    fetch(`/api/aparatos/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nombre, potencia_w: potencia, horas_dia: horas })
    })
    .then(r => r.json())
    .then(data => {
        mostrarNotificacion(data.mensaje, 'success');
        cargarAparatos();
    })
    .catch(() => mostrarNotificacion('Error al editar aparato', 'error'));
}

function cargarEjemplo() {
    fetch('/api/cargar-ejemplo', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            mostrarNotificacion('Datos de ejemplo cargados con éxito', 'success');
            // Recargar página si estamos en una sección que depende de datos
            if (window.location.pathname === '/aparatos' || window.location.pathname === '/') {
                location.reload();
            }
        })
        .catch(e => mostrarNotificacion('Error al cargar ejemplo', 'error'));
}

// ============ FUNCIONES DE CONSUMO ============

function calcularConsumo() {
    const btn = document.querySelector('.btn-large');
    if (!btn) return;

    const originalText = btn.innerHTML;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
    btn.disabled = true;

    fetch('/api/consumo')
        .then(r => r.json())
        .then(data => {
            renderizarConsumo(data);
            btn.innerHTML = originalText;
            btn.disabled = false;
        })
        .catch(e => {
            mostrarNotificacion('Error al calcular consumo', 'error');
            btn.innerHTML = originalText;
            btn.disabled = false;
        });
}

function renderizarConsumo(data) {
    const container = document.getElementById('consumo-results');
    if (!container) return;
    container.style.display = 'block';
    
    document.getElementById('kpi-diario').textContent = data.total_diario_kwh.toFixed(2);
    document.getElementById('kpi-mensual').textContent = data.total_mensual_kwh.toFixed(2);
    document.getElementById('kpi-costo').textContent = '$' + data.costo_mensual_clp.toLocaleString('es-CL');
    
    const tbody = document.getElementById('tabla-consumo-body');
    tbody.innerHTML = data.aparatos.map(aparato => `
        <tr>
            <td style="font-weight: 600;">${aparato.nombre}</td>
            <td>${aparato.potencia_w} W</td>
            <td>${aparato.horas_dia.toFixed(1)} h</td>
            <td>${aparato.kwh_dia.toFixed(3)}</td>
            <td style="color: var(--primary); font-weight: 600;">${aparato.kwh_mes.toFixed(2)}</td>
            <td style="font-weight: 700;">$${aparato.costo_mes.toLocaleString('es-CL', {maximumFractionDigits: 0})}</td>
        </tr>
    `).join('');
    
    generarGrafico(data.aparatos);
    cargarTopConsumidores();
}

function generarGrafico(aparatos) {
    const canvas = document.getElementById('grafico-consumo');
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    
    if (graficoInstance) graficoInstance.destroy();
    
    graficoInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: aparatos.map(a => a.nombre),
            datasets: [{
                label: 'Consumo Mensual (kWh)',
                data: aparatos.map(a => a.kwh_mes),
                backgroundColor: aparatos.map((_, i) => COLORS.chart[i % COLORS.chart.length]),
                borderRadius: 6,
                barThickness: 40
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                tooltip: { backgroundColor: '#0f172a', padding: 12, cornerRadius: 8 }
            },
            scales: {
                y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                x: { grid: { display: false } }
            }
        }
    });
}

function cargarTopConsumidores() {
    fetch('/api/top-consumidores')
        .then(r => r.json())
        .then(top => {
            const topList = document.getElementById('top-list');
            if (!topList) return;
            topList.innerHTML = top.map(item => `
                <div class="top-item">
                    <span class="top-rank">${item.rank}</span>
                    <div class="top-info">
                        <div class="top-nombre">${item.nombre}</div>
                        <div class="top-stats">
                            Representa el <span class="top-valor" style="font-size: 0.9rem;">${item.porcentaje.toFixed(1)}%</span> del gasto total
                        </div>
                    </div>
                    <div class="top-valor">${item.kwh_mes.toFixed(1)} <small>kWh</small></div>
                </div>
            `).join('');
        });
}

// ============ FUNCIONES DE SIMULACION ============

function simularReduccion() {
    const porcentaje = document.getElementById('porcentaje-reduccion').value;
    
    fetch('/api/simulacion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ porcentaje_reduccion: parseFloat(porcentaje) })
    })
    .then(r => r.json())
    .then(data => renderizarSimulacion(data))
    .catch(e => mostrarNotificacion('Error en simulación', 'error'));
}

function renderizarSimulacion(data) {
    const container = document.getElementById('simulacion-results');
    if (!container) return;
    container.style.display = 'block';
    
    document.getElementById('sim-original').textContent = data.consumo_original.toFixed(1);
    document.getElementById('sim-nuevo').textContent = data.consumo_nuevo.toFixed(1);
    document.getElementById('sim-ahorro-kwh').textContent = data.ahorro_kwh.toFixed(1);
    document.getElementById('sim-ahorro-dinero').textContent = '$' + data.ahorro_dinero.toLocaleString('es-CL', {maximumFractionDigits: 0});
    document.getElementById('sim-ahorro-porc').textContent = data.ahorro_porcentual.toFixed(1);
}

// ============ FUNCIONES DE RECOMENDACIONES ============

function cargarRecomendaciones() {
    fetch('/api/recomendaciones')
        .then(r => r.json())
        .then(recomendaciones => renderizarRecomendaciones(recomendaciones))
        .catch(e => mostrarNotificacion('Error al generar sugerencias', 'error'));
}

function renderizarRecomendaciones(recomendaciones) {
    const contenedor = document.getElementById('recomendaciones-container');
    if (!contenedor) return;
    
    contenedor.style.display = 'grid';
    contenedor.innerHTML = recomendaciones.map((rec, idx) => `
        <div class="recommendation-card" style="animation: slideInRight 0.5s ease forwards ${idx * 0.1}s; opacity: 0;">
            <div class="rec-icon">
                <i class="fas fa-lightbulb"></i>
            </div>
            <div class="rec-content">
                <h4 style="font-family: var(--font-heading); font-size: 1.25rem; margin-bottom: 1rem; color: var(--text-main);">${rec.aparato}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                    <div>
                        <small style="color: var(--text-muted); display: block; text-transform: uppercase; font-weight: 600; font-size: 0.7rem;">Meta de Uso</small>
                        <span style="font-weight: 700; color: var(--info);">${rec.horas_recomendada.toFixed(1)}h / día</span>
                    </div>
                    <div>
                        <small style="color: var(--text-muted); display: block; text-transform: uppercase; font-weight: 600; font-size: 0.7rem;">Ahorro Mensual</small>
                        <span style="font-weight: 700; color: var(--accent);">$${rec.ahorro_dinero.toLocaleString('es-CL', {maximumFractionDigits: 0})}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

// ============ FUNCIONES AUXILIARES ============

function mostrarNotificacion(mensaje, tipo) {
    const notif = document.getElementById('notification');
    if (!notif) return;
    notif.textContent = mensaje;
    notif.className = 'notification ' + (tipo || 'success') + ' show';
    setTimeout(() => notif.classList.remove('show'), 4000);
}

function revealOnScroll() {
    document.querySelectorAll('.card').forEach(card => {
        if (card.getBoundingClientRect().top < window.innerHeight - 50) {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }
    });
}

// Estilos extra para animaciones via JS
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
    @keyframes slideInRight { from { opacity: 0; transform: translateX(20px); } to { opacity: 1; transform: translateX(0); } }
`;
document.head.appendChild(style);
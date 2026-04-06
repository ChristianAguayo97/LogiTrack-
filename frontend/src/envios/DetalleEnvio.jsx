import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { formatearFecha } from '../helpers/formatearFecha';
import './DetalleEnvio.css';

const DetalleEnvio = ({ usuarioActual}) => {
  const { tracking_id } = useParams(); //Captura el ID desde la URL
  const navigate = useNavigate();
  const [envio, setEnvio] = useState(null);
  const [error, setError] = useState(null);

  // Estado para el nuevo estado del envío
  const [nuevoEstado, setNuevoEstado] = useState('');

  const obtenerDetalle = () => {
    fetch(`http://127.0.0.1:8000/envios/${tracking_id}`)
        .then(response => {
            if (!response.ok) throw new Error('Error al obtener el envío');
            return response.json();
        })
        .then(data => {
            setEnvio(data)
            setNuevoEstado(data.estado); // Inicializa el nuevo estado con el estado actual del envío
        })
        .catch(err => setError(err.message));
  }

useEffect(() => {
    obtenerDetalle();
}, [tracking_id]);

const cambiarEstado = () => {
    if (!nuevoEstado) return;

    fetch(`http://127.0.0.1:8000/envios/${tracking_id}/estado?estado=${nuevoEstado}`, {
        method: 'PATCH',
        headers: {
            'accept': 'application/json',
            'x-usuario-id': usuarioActual.id,
            'x-usuario-nombre': usuarioActual.nombre,
            'x-usuario-rol': usuarioActual.rol

        }
    })
    .then(response => {
        if (!response.ok) throw new Error('Error al cambiar el estado');
        return response.json();
    })
    .then(() => {
        alert('Estado actualizado con éxito');
        obtenerDetalle(); // Refresca los detalles del envío para mostrar el nuevo estado
    })
    .catch(err => alert(err.message));
};

if (error) return (
    <div className="error-contenedor">
        <p>No se pudo encontrar el envio #{tracking_id}</p>
        <button onClick={() => navigate('/')}>Volver al inicio</button>
    </div>
);

if (!envio) return <p>Cargando detalles del envío...</p>;

return (
    
    <div className="detalle-pagina">
        <div className="detalle-header">
            <button className="btn-vuelve" onClick={() => navigate('/')}>Volver</button>
            <h2>Envio #{envio.tracking_id}</h2>
        </div>

        <div className="detalle-lista">
            <p><strong>Remitente ID:</strong> {envio.remitente_id}</p>
            <p><strong>Destinatario ID:</strong> {envio.destinatario_id}</p>
            <p><strong>Creado por usuario ID:</strong> {envio.creado_por_usuario_id}</p>
            <p><strong>Peso del paquete:</strong> {envio.peso_paquete} kg</p>
            <p><strong>Distancia estimada:</strong> {envio.distancia_estimada} km</p>
            <p><strong>Tipo de envío:</strong> {envio.tipo_envio}</p>
            <p><strong>Caducidad:</strong> {envio.tiene_caducidad ? 'Sí' : 'No'}</p>
            <p><strong>Fecha de creación:</strong> {formatearFecha(envio.f_creacion)}</p>
            <p>
                <strong>Estado:</strong> 
                <span className={`tag-estado estado-${envio.estado?.toLowerCase().replace(' ', '-') || 'default'}`}>
                {envio.estado}
                </span>
            </p>
            <p>
                <strong>Prioridad:</strong>
                <span className={`tag-prioridad prioridad-${envio.prioridad?.toLowerCase() || 'default'}`}>
                {envio.prioridad || 'No asignada'}
                </span>
            </p>
            <p><strong>Ventana horaria:</strong> {envio.ventana_horario}</p>
            <p><strong>Tráfico ruta hasta destino:</strong> {(envio.saturacion_ruta * 100).toFixed(0)}%</p>
            <p><strong>Restricciones:</strong> {envio.restricciones}</p>
        </div>

        {/* Opciones del supervisor (Ahora fuera de la grilla) */}
        {usuarioActual.rol === 'Supervisor' && (
            <div className="panel-supervisor">
                <p><strong>Cambiar el estado del envio:</strong></p>
                <div className="controles-supervisor">
                    <select value={nuevoEstado} onChange={(e) => setNuevoEstado(e.target.value)} className="selector-estado">
                        <option value="Pendiente">Pendiente</option>
                        <option value="En transito">En tránsito</option>
                        <option value="Entregado">Entregado</option>
                        <option value="Cancelado">Cancelado</option>
                    </select>
                    <button onClick={cambiarEstado} className="btn-actualizar">
                      Actualizar
                    </button>
                </div>
            </div>
          )}
    </div>
);

};

export default DetalleEnvio;

import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import './DetalleEnvio.css';

const DetalleEnvio = () => {
  const { tracking_id } = useParams(); //Captura el ID desde la URL
  const navigate = useNavigate();
  const [envio, setEnvio] = useState(null);
  const [error, setError] = useState(null);

useEffect(() => {
    fetch(`http://127.0.0.1:8000/envios/${tracking_id}`)
        .then(response => {
            if (!response.ok) throw new Error('Error al obtener el envío');
            return response.json();
        })
        .then(data => setEnvio(data))
        .catch(err => setError(err.message));
}, [tracking_id]);

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

        <div className="detalle-grid">
            <section className = "tarjeta-info">
                <h3>Informacion personal</h3>
                <p><strong>Remitente ID:</strong> {envio.remitente_id}</p>
                <p><strong>Destinatario ID:</strong> {envio.destinatario_id}</p>
                <p><strong>Creado por usuario ID:</strong> {envio.creado_por_usuario_id}</p>

            </section>

            <section className="tarjeta-info">
                <h3>Datos del paquete</h3>
                <p><strong>Peso:</strong> {envio.peso_paquete}</p>
                <p><strong>Distancia:</strong> {envio.distancia}</p>
                <p><strong>Tipo:</strong> {envio.tipo_envio}</p>
                <p><strong>Caducidad:</strong> {envio.tiene_caducidad ? 'Sí' : 'No'}</p>
                <p><strong>Fecha de creacion:</strong> {envio.f_creacion}</p>
            </section>

           <section className = "tarjeta-info">
                <h3>Logistica</h3>
                <p><strong>Estado:</strong> <span className="tag-estado">{envio.estado}</span></p>
                <p><strong>Prioridad:</strong><span className={`tag-prioridad prioridad-${envio.prioridad?.toLowerCase() || 'default'}`}>
                        {envio.prioridad || 'No asignada'}
                    </span></p>
                <p><strong>Ventana horaria:</strong> {envio.ventana_horario}</p>
                <p><strong>Trafico ruta hasta destino:</strong> {envio.saturacion_ruta}</p>
                <p><strong>Restricciones:</strong> {envio.restricciones}</p>
                </section>
        </div>
    </div>
);

};

export default DetalleEnvio;

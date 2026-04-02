import { useNavigate } from "react-router-dom";
import './Auditoria.css';
import { useState, useEffect } from "react";

const Auditoria = ( {usuarioActual} ) => {
    const navigate = useNavigate();
    const [auditorias, setAuditorias] = useState([]);
    const [error, setError] = useState(null);

    const cargarAuditorias = () => {

        fetch('http://127.0.0.1:8000/auditoria/?skip=0&limit=100', {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'x-usuario-id': usuarioActual.id.toString(),
                'x-usuario-nombre': usuarioActual.nombre,
                'x-usuario-rol': usuarioActual.rol   
            }
        })
            .then(response => {
                if (!response.ok) throw new Error('Error al cargar auditorias');
                return response.json();
            })
            .then(data => {
                setAuditorias(data);
            })
            .catch(err => {
                setError(err.message);
            })
    };

    useEffect(() => {
        cargarAuditorias();
    }   , []);

    return (
        <div className="auditoria-contenedor">
            <div className ="auditoria-header">
                <h2 className = "auditoria-titulo">Historial de auditoria</h2>
                <button className = "btn-volver-auditoria" onClick={() => navigate('/')}>
                Volver al inicio
                </button>
            </div>

            <div>
                <table className = "tabla-auditoria">
                    <thead>
                        <tr>
                            <th>ID Auditoría</th>
                            <th>Fecha y hora</th>
                            <th>Acción</th>
                            <th>ID Envío</th>
                            <th>ID Usuario</th>
                            <th>Nombre usuario</th>
                            <th>Rol</th>
                            <th>Detalle</th>
                        </tr>
                    </thead>
                    <tbody>
                        {auditorias.map(registro => ( 
                            <tr key={registro.id} className = "fila-auditoria">
                                <td>{registro.id}</td>
                                <td>{registro.f_accion}</td>
                                <td>{registro.accion}</td>
                                <td>{registro.envio_id}</td>
                                <td>{registro.usuario_id}</td>
                                <td>{registro.nombre_usuario}</td>
                                <td>{registro.usuario_rol}</td>
                                <td className = "celda-detalle" title={registro.detalle}>{registro.detalle}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>

                {auditorias.length === 0 && (
                    <p className="auditoria-mensaje">
                        No se encontraron registros de auditoría para mostrar.
                    </p>
                )}
            </div>
            

        </div>
    );

}

export default Auditoria;
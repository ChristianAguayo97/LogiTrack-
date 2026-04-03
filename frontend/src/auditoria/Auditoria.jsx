import { useNavigate } from "react-router-dom";
import './Auditoria.css';
import TablaAuditoria from "./TablaAuditoria";
import BuscadorAuditorias from "./BuscadorAuditorias";
import { useState, useEffect, use } from "react";

const Auditoria = ( {usuarioActual} ) => {
    const navigate = useNavigate();
    const [auditorias, setAuditorias] = useState([]);
    const [error, setError] = useState(null);

    // Verificar que el usuario tenga rol de Supervisor, si no redirigir al inicio
    useEffect(() => {
        if (usuarioActual.rol !== 'Supervisor') {
            alert('Acceso denegado. Solo los supervisores pueden acceder a la auditoria.');
            navigate('/');
        }
    }   , [usuarioActual, navigate]);

    const cargarAuditorias = (idUsuarioParaBuscar = '') => {

    
        const url = idUsuarioParaBuscar
            ? `http://127.0.0.1:8000/auditoria/usuarios/${idUsuarioParaBuscar}?skip=0&limit=100`
            : 'http://127.0.0.1:8000/auditoria/?skip=0&limit=100';

        fetch(url, {
            method: 'GET',
            headers: {
                'accept': 'application/json',
                'x-usuario-id': usuarioActual.id.toString(),
                'x-usuario-nombre': usuarioActual.nombre,
                'x-usuario-rol': usuarioActual.rol   
            }
        })
            .then(response => {
                if (response.status === 404) return null;
                if (!response.ok) throw new Error('Error al cargar auditorias');
                return response.json();
            })
            .then(data => {
                if (data == null) {
                setAuditorias([]);
                } else if (Array.isArray(data)) {
                setAuditorias(data);
                } else {
                setAuditorias([data]);
                }
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
            
            <BuscadorAuditorias onBuscarAuditorias={cargarAuditorias} />
            <TablaAuditoria auditorias={auditorias} />
        </div>
    );

}

export default Auditoria;
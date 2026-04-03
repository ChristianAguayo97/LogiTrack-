import { useNavigate } from "react-router-dom";
import './Auditoria.css';
import TablaAuditoria from "./TablaAuditoria";
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
            
            <TablaAuditoria auditorias={auditorias} />
        </div>
    );

}

export default Auditoria;
import { useNavigate } from "react-router-dom";
import './Auditoria.css';

const Auditoria = () => {
    const navigate = useNavigate();

    return (
        <div className="auditoria-contenedor">
            <h2 className = "auditoria-titulo">Panel de auditoria</h2>
            <p className = "auditoria-mensaje">Modulo en construccion</p>
            <button className = "btn-volver-auditoria" onClick={() => navigate('/')}>
                Volver al inicio
            </button>
        </div>
    );
}

export default Auditoria;
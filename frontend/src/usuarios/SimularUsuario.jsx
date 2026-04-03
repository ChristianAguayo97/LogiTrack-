import './SimularUsuario.css';

const SimularUsuario = ({ usuarioActual, onAlternar }) => {
    return (
        <div className = "simulador-usuario">
            <span>
                <strong>{usuarioActual.nombre}</strong> ({usuarioActual.rol})
            </span>
            <button onClick={onAlternar} className = {`btn-toggle-rol ${usuarioActual.rol.toLowerCase()}`}>
            Cambiar a {usuarioActual.rol === 'Operador' ? 'Supervisor' : 'Operador'}
            </button>

        </div>
    )
};

export default SimularUsuario;
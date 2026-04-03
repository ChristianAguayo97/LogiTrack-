import './TablaAuditoria.css';
import { formatearFecha } from '../helpers/formatearFecha';

const TablaAuditoria = ({ auditorias }) => {
    return (
        <div>
            <table className = "tabla-auditoria">
                <thead>
                       <tr>
                        <th>ID Auditoría</th>
                        <th>Fecha y hora</th>
                        <th>Acción</th>
                        <th>ID Envío</th>
                        <th>ID Supervisor</th>
                        <th>Nombre Supervisor</th>
                        <th>Rol</th>
                        <th>Detalle</th>
                        </tr>
                </thead>
                <tbody>
                {auditorias.map(registro => ( 
                    <tr key={registro.id} className = "fila-auditoria">
                        <td>{registro.id}</td>
                        <td>{formatearFecha(registro.f_accion)}</td>
                        <td>{registro.accion}</td>
                        <td>{registro.envio_id}</td>
                        <td>{registro.usuario_id}</td>
                        <td>{registro.usuario_nombre}</td>
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
    );
};

export default TablaAuditoria;
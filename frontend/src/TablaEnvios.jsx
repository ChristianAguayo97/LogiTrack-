/*
* Componente encargado de mostrar la tabla de envíos. Recibe un array de envíos como prop y los muestra en una tabla HTML.
*/
import { formatearFecha } from './helpers/formatearFecha';
import './TablaEnvios.css';
import { Link } from 'react-router-dom';

const TablaEnvios = ({ envios }) => {
  return (
    <div>
      <p>Lista de envíos</p>
      
      <table className='tabla-envios'>
        <thead>
          <tr>
            <th>Tracking ID</th>
            <th>Fecha de alta</th>
            <th>Remitente ID</th>
            <th>Destinatario ID</th>
            <th>Peso (kg)</th>
            <th>Estado</th>
            <th>Prioridad</th>
            <th>Acciones</th>
          </tr>
        </thead>
        <tbody>
          {envios.map(envio => (
            <tr key={envio.tracking_id} className='fila-envio'>
              <td>{envio.tracking_id}</td>
              <td>{formatearFecha(envio.f_creacion)}</td>
              <td>{envio.remitente_id}</td>
              <td>{envio.destinatario_id}</td>
              <td>{envio.peso_paquete}</td>
              <td>{envio.estado}</td>
              <td>{envio.prioridad}</td>
              <td>
                <Link to={`/envio/${envio.tracking_id}`} className = "btn-ver-detalle">
                Ver detalle
                </Link>
              </td>
            </tr>
          ))} 
        </tbody>
      </table>

      {envios.length === 0 && (
        <p className="mensaje-vacio">
          No se encontraron envíos para mostrar.
        </p>
      )}
    </div>
  );
};

export default TablaEnvios;
import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import BuscadorEnvios from './envios/BuscadorEnvios';
import TablaEnvios from './envios/TablaEnvios';
import './Inicio.css';

const Inicio = ({ usuarioActual }) => {
  const [envios, setEnvios] = useState([]);
  
  const cargarEnvios = (idParaBuscar = '') => {
    // Verifica si se proporcionó un ID para buscar, y construye la URL adecuada
    const url = idParaBuscar 
      ? `http://127.0.0.1:8000/envios/${idParaBuscar}`
      : 'http://127.0.0.1:8000/envios';

    // Realiza la solicitud al backend para obtener los envíos (o el envío específico)
    fetch(url)
      .then(response => {
        if (response.status === 404) return null;
        if (!response.ok) throw new Error('Error al cargar los envíos');
        return response.json();
      })
      .then(data => {
        if (data == null) {
          setEnvios([]);
        } else if (Array.isArray(data)) {
          setEnvios(data);
        } else {
          setEnvios([data]);
        }
      })
      .catch(error => console.error('Error fetching envios:', error));
  };

/*
  * useEffect: es un hook de React que permite sincronizar un componente con un sistema externo (el backend por ejemplo)
  * En este caso, se utiliza para cargar la lista de envios cuando la pagina se inicia.
  *  https://react.dev/reference/react/useEffect
  *  https://react.dev/learn/synchronizing-with-effects
  */
  useEffect(() => {
    cargarEnvios();
  }   , []);

  return (
    <div>
        <div className='inicio-contenedor'>
            <div className = 'inicio-encabezado'>
                <h2>Gestión de envios</h2>
                <p>Lista y administración de todos los paquetes activos.</p>
            </div>

            <div className = 'contenedor-acciones contenedor-acciones-buscador'>
                <BuscadorEnvios onBuscar={cargarEnvios} />  

                <div className = 'contenedor-acciones-auditoria-crear'>
                  {usuarioActual?.rol?.toLowerCase() === 'supervisor' && (
                  <Link to="/auditoria" className="boton-auditoria">Auditoría</Link>
                  )}
                  <Link to="/nuevo-envio" className="boton-nuevo-envio">+ Nuevo envío</Link>
                </div>
            </div>

            <div className = 'contenedor-acciones'>
              <TablaEnvios envios={envios} />
            </div>
        </div>
    </div>
  );
};

export default Inicio;

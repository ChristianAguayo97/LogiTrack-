import { useState, useEffect } from 'react';
import './App.css';
import FormularioEnvio from './FormularioEnvio';
import BuscadorEnvios from './BuscadorEnvios';
import TablaEnvios from './TablaEnvios';

const App = () => {

  // Constante que guarda los envios, inicialmente es un array vacio
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
    <div className='contenedor'>
      <h1>LogiTrack - Panel de control</h1>
      <FormularioEnvio alCompletar={() => cargarEnvios()} />
      <BuscadorEnvios onBuscar={cargarEnvios} />
      <TablaEnvios envios={envios} />
    </div>
  );
};

export default App;
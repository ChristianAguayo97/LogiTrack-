import { useState, useEffect } from 'react';
import './App.css';
import FormularioEnvio from './FormularioEnvio';

const App = () => {

  // Constante que guarda los envios, inicialmente es un array vacio
  const [envios, setEnvios] = useState([]);
  
  /*
  * useEffect: es un hook de React que permite sincronizar un componente con un sistema externo (el backend por ejemplo)
  *  https://react.dev/reference/react/useEffect
  *  https://react.dev/learn/synchronizing-with-effects
  */
  useEffect(() => {
    fetch('http://127.0.0.1:8000/envios')
      .then(response => response.json())
      .then(data => setEnvios(data))
      .catch(error => console.error('Error fetching envios:', error));
  }   , []);

  return (
    <div className='contenedor'>
      <h1>LogiTrack - Panel de control</h1>
      <p>Lista de envios</p>

      <FormularioEnvio alCompletar={() => buscarEnvios('')} />
      <table className='tabla-envios'>
        <thead>
          <tr>
            <th>ID envio</th>
            <th>Destinatario</th>
            <th>Peso (kg)</th>
            <th>Estado</th>
          </tr>
        </thead>
        <tbody>
          {envios.map(envio => (
            <tr key={envio.tracking_id} className='fila-envio'>
              <td>{envio.tracking_id}</td>
              <td>{envio.destinatario_id}</td>
              <td>{envio.peso_paquete}</td>
              <td>{envio.estado}</td>
            </tr>
          ))} 
        </tbody>
      </table>
    </div>
  );
};

export default App;
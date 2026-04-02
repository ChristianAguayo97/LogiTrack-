import { useState, useEffect } from 'react';

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
    <div style={{ padding: '20px' , fontFamily: 'sans-serif' }}>
      <h1>LogiTrack - Listado de envios</h1>
      <p>Lista de envios</p>

      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '20px' }}>
        <thead>
          <tr style={{ background: '#f4f4f4', borderBottom: '2px solid #ddd' }}>
            <th style={{ padding: '10px', textAlign: 'left' }}>ID envio</th>
            <th style={{ padding: '10px', textAlign: 'left' }}>Destinatario</th>
            <th style={{ padding: '10px', textAlign: 'left' }}>Peso (kg)</th>
            <th style={{ padding: '10px', textAlign: 'left' }}>Estado</th>
          </tr>
        </thead>
        <tbody>
          {envios.map(envio => (
            <tr key={envio.tracking_id} style={{ borderBottom: '1px solid #ddd' }}>
              <td style={{ padding: '10px' }}>{envio.tracking_id} </td>
              <td style={{ padding: '10px' }}>{envio.destinatario_id}</td>
              <td style={{ padding: '10px' }}>{envio.peso_paquete} </td>
              <td style={{ padding: '10px' }}>{envio.estado} </td>
            </tr>
          ))} 
        </tbody>
      </table>
    </div>
  );
};

export default App;
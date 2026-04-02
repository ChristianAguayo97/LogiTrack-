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

      <pre style={{ background: '#f4f4f4', padding: '15px', borderRadius: '5px' }}>
        {JSON.stringify(envios, null, 2)}</pre>
    </div>
  );
};

export default App;
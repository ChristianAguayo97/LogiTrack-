import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import { useState } from 'react';
import './App.css';
import Inicio from './Inicio';
import FormularioEnvio from './FormularioEnvio';
import DetalleEnvio from './DetalleEnvio';
import SimularUsuario from './SimularUsuario';

const App = () => {

  const [usuarioActual, setUsuarioActual] = useState({
      id : 1,
      nombre : "Usuario demo",
      rol: "Operador"
  });

  const alternarUsuario = () => {
    setUsuarioActual(prevUsuario => 
      prevUsuario.rol === 'Operador' 
        ? { id: 2, nombre: 'Supervisor Demo', rol: 'Supervisor' }
        : { id: 1, nombre: 'Usuario Demo', rol: 'Operador' }
    );
  };

  return (
    <BrowserRouter>
      <div className='contenedor'>
        <header className='encabezado'>
          <Link to="/" className='titulo'>
            <h1>LogiTrack</h1>
          </Link>

          <SimularUsuario usuarioActual={usuarioActual} onAlternar={alternarUsuario} />
        </header>

        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/nuevo-envio" element={<FormularioEnvio usuarioActual={usuarioActual} />} />
          <Route path='/envio/:tracking_id' element={<DetalleEnvio usuarioActual={usuarioActual} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
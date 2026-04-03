import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Inicio from './Inicio';
import FormularioEnvio from './envios/FormularioEnvio';
import DetalleEnvio from './envios/DetalleEnvio';
import SimularUsuario from './SimularUsuario';
import Auditoria from './auditoria/Auditoria';
import { useUsuario } from './useUsuario';

const App = () => {

  const { usuarioActual, alternarUsuario } = useUsuario();

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
          <Route path="/" element={<Inicio usuarioActual={usuarioActual} />} />
          <Route path="/nuevo-envio" element={<FormularioEnvio usuarioActual={usuarioActual} />} />
          <Route path='/envio/:tracking_id' element={<DetalleEnvio usuarioActual={usuarioActual} />} />
          <Route path='/auditoria' element={<Auditoria usuarioActual={usuarioActual} />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
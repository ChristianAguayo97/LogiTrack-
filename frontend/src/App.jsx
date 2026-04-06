import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Inicio from './Inicio';
import FormularioEnvio from './envios/FormularioEnvio';
import DetalleEnvio from './envios/DetalleEnvio';
import SimularUsuario from './usuarios/SimularUsuario';
import Auditoria from './auditoria/Auditoria';
import { useUsuario } from './usuarios/useUsuario';

const App = () => {
  const { usuarioActual, alternarUsuario } = useUsuario();

  return (
    <BrowserRouter>
      <div className='contenedor-app'>
        
        {/* 1. LA BARRA LATERAL (Izquierda) */}
        <aside className='sidebar'>
          <div className='sidebar-arriba'>
            <Link to="/" className='sidebar-logo'>
              LogiTrack
            </Link>
          </div>

          <div className='sidebar-abajo'>
            <div className='perfil-usuario'>
              <div className='avatar'>👤</div>
              <p className='nombre-usuario'>{usuarioActual.nombre}</p>
              <p className='rol-usuario'>{usuarioActual.rol}</p>
              
              {/* Aquí reutilizamos tu componente o ponemos el botón directo */}
              <button className='btn-cambiar-rol' onClick={alternarUsuario}>
                Cambiar a {usuarioActual.rol === 'Operador' ? 'Supervisor' : 'Operador'}
              </button>
            </div>
          </div>
        </aside>

        {/* 2. EL CONTENIDO PRINCIPAL (Derecha) */}
        <main className='contenido-principal'>
          <Routes>
            <Route path="/" element={<Inicio usuarioActual={usuarioActual} />} />
            <Route path="/nuevo-envio" element={<FormularioEnvio usuarioActual={usuarioActual} />} />
            <Route path='/envio/:tracking_id' element={<DetalleEnvio usuarioActual={usuarioActual} />} />
            <Route path="/auditoria" element={<Auditoria usuarioActual={usuarioActual} />} />
          </Routes>
        </main>

      </div>
    </BrowserRouter>
  );
};
export default App;
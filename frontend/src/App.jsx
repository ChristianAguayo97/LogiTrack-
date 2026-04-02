import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import './App.css';
import Inicio from './Inicio';
import FormularioEnvio from './FormularioEnvio';

const App = () => {

  return (
    <BrowserRouter>
      <div className='contenedor'>
        <header className='encabezado'>
          <Link to="/" className='titulo'>
            <h1>LogiTrack</h1>
          </Link>
        </header>

        <Routes>
          <Route path="/" element={<Inicio />} />
          <Route path="/nuevo-envio" element={<FormularioEnvio />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
};

export default App;
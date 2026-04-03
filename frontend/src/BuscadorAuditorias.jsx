import { useState } from 'react';
import './BuscadorAuditorias.css';

const BuscadorAuditorias = ({ onBuscarAuditorias }) => {
  const [busquedaId, setBusquedaId] = useState('');

  const manejarBusqueda = (e) => {
    e.preventDefault();
    onBuscarAuditorias(busquedaId); 
  };

  const limpiarBusqueda = () => {
    setBusquedaId('');
    onBuscarAuditorias(''); 
  };

  return (
    <div className="buscador-contenedor">
        <p>Buscar auditoría por ID usuario</p>
        <form onSubmit={manejarBusqueda} className="buscador-formulario">
        <input 
          type="number" 
          placeholder="Buscar por ID usuario exacto..." 
          value={busquedaId}
          onChange={(e) => setBusquedaId(e.target.value)}
          className="buscador-input"
        />
        <button type="submit" className="btn-buscar">
          Buscar
        </button>
        <button type="button" onClick={limpiarBusqueda} className="btn-limpiar">
          Ver todos
        </button>
      </form>
    </div>
  );
};

export default BuscadorAuditorias;
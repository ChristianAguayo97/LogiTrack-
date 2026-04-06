import { useState } from 'react';
import './BuscadorEnvios.css';

const BuscadorEnvios = ({ onBuscar }) => {
  const [busquedaId, setBusquedaId] = useState('');

  const manejarBusqueda = (e) => {
    e.preventDefault();
    onBuscar(busquedaId); 
  };

  const limpiarBusqueda = () => {
    setBusquedaId('');
    onBuscar(''); 
  };

  return (
    <div className="buscador-contenedor">
        <p>Buscar envio por tracking ID</p>
        <form onSubmit={manejarBusqueda} className="buscador-formulario">
        <input 
          type="number" 
          placeholder="Buscar por Tracking ID..." 
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

export default BuscadorEnvios;
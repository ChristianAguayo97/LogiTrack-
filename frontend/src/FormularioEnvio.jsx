import { useState } from "react";  
import './FormularioEnvio.css';

const FormularioEnvio = ({ alCompletar }) => {
    const [formData, setFormData] = useState({  
        remitente_id: '',  
        destinatario_id: '',
        peso_paquete: '',
        distancia_estimada: '',
        restricciones: 'Ninguno',
        tiene_caducidad: false,
        tipo_envio: 'Normal',
        ventana_horario: 'Mañana',
        saturacion_ruta: 0,
        creado_por_usuario_id: 1,
        consentimiento_datos: false
});

    const manejarCambio = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prevData => ({
            ...prevData,
            [name]: type === 'checkbox' ? checked : value
        }));
    };


const enviarFormulario = (e) => {
    e.preventDefault();
    fetch('http://127.0.0.1:8000/envios/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // Simulacion de estar logeado como usuario
            'x-usuario-id': '1',
            'x-usuario-nombre': 'Usuario demo',
            'x-usuario-rol': 'Operador'
        },
        body: JSON.stringify(formData)
    }) 
    .then(response => {
        if (!response.ok) throw new Error('Error al enviar el formulario');
        return response.json();
    })
    .then(data => {
        alert(`Envío creado con éxito, Tracking ID: ${data.tracking_id}`);
        alCompletar(); // Llamar a la función para actualizar la lista de envíos
    })
    .catch(error => console.error('Error:', error));
};

return (
    <div className="formulario-tarjeta">
        <h2>Crear Envío</h2>
        <form onSubmit={enviarFormulario} className="grilla-formulario">
<div className="campo">
            <label>ID remitente</label>
            <input type="number" name="remitente_id" value={formData.remitente_id} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>ID destinatario</label>
            <input type="number" name="destinatario_id" value={formData.destinatario_id} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>Peso (KG)</label>
            <input type="number" name="peso_paquete" value={formData.peso_paquete} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>Distancia (KM)</label>
            <input type="number" name="distancia_estimada" value={formData.distancia_estimada} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>Tipo de envio</label>
            <select name="tipo_envio" value={formData.tipo_envio} onChange={manejarCambio}>
                <option value="Normal">Normal</option>
                <option value="Express">Express</option>
            </select>
        </div>

        <div className="campoCheckbox">
            <label>
                <input type="checkbox" name="consentimiento_datos" checked={formData.consentimiento_datos} onChange={manejarCambio} />
                Acepto el consentimiento y tratado de datos segun la Ley 25.326
            </label>
        </div>

        <button type="submit" className="btn-guardar">Registrar envio</button>
        </form>
    </div>
);
};

export default FormularioEnvio;
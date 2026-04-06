import { useState } from "react";  
import { useNavigate } from "react-router-dom";
import './FormularioEnvio.css';

const FormularioEnvio = ({ usuarioActual}) => {

    // Función que se llamará al completar el formulario para actualizar la lista de envíos
    const navigate = useNavigate();

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
        creado_por_usuario_id: usuarioActual.id,
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
            // Inyectamos los datos del usuario actual
            'x-usuario-id': usuarioActual.id.toString(),
            'x-usuario-nombre': usuarioActual.nombre,
            'x-usuario-rol': usuarioActual.rol
        },
        body: JSON.stringify(formData)
    }) 
    .then(response => {
        if (!response.ok) throw new Error('Error al enviar el formulario');
        return response.json();
    })
    .then(data => {
        alert(`Envío creado con éxito, Tracking ID: ${data.tracking_id}`);
        navigate('/'); // Redirige a la página principal después de crear el envío
    })
    .catch(error => console.error('Error:', error));
};

return (
    <div className="formulario-tarjeta">
        <div className="botones-control">
            <h2>Crear Envío</h2>
            <button onClick={() => navigate('/')} className='btn-volver'>Volver atras</button>
        </div>
        
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
            <label>Peso en KG</label>
            <input type="number" name="peso_paquete" value={formData.peso_paquete} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>Distancia en KM</label>
            <input type="number" name="distancia_estimada" value={formData.distancia_estimada} onChange={manejarCambio} required/>
        </div>

        <div className="campo">
            <label>Restricciones del envio</label>
            <select name="restricciones" value={formData.restricciones} onChange={manejarCambio}>
                <option value="Ninguno">Ninguno</option>
                <option value="Frio">Frio</option>
                <option value="Fragil">Fragil</option>
                <option value="Toxico">Toxico</option>
                <option value="Inflamable">Inflamable</option>
                <option value="Perecedero">Perecedero</option>
            </select>
        </div>

        <div className="campo">
            <label>¿Tiene caducidad?</label>
            <select name="tiene_caducidad" value={formData.tiene_caducidad} onChange={manejarCambio}>
                <option value="false">No</option>
                <option value="true">Sí</option>
            </select>
        </div>

        <div className="campo">
            <label>Tipo de envio</label>
            <select name="tipo_envio" value={formData.tipo_envio} onChange={manejarCambio}>
                <option value="Normal">Normal</option>
                <option value="Express">Express</option>
            </select>
        </div>

        <div className="campo">
            <label>Ventana horaria</label>
            <select name="ventana_horaria" value={formData.ventana_horaria} onChange={manejarCambio}>
                <option value="Mañana">Mañana</option>
                <option value="Tarde">Tarde</option>
                <option value="Noche">Noche</option>
            </select>
        </div>

        <div className="campo-checkbox">
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
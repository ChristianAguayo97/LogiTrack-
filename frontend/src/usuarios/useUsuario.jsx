import { useState, useEffect } from 'react';

export const useUsuario = () => {

    const [usuarioActual, setUsuarioActual] = useState(() => {
        // El guardado del usuario es por si refresca la pagina, para no perder el usuario simulado actual
        const usuarioGuardado = localStorage.getItem('usuarioActual');
        if (usuarioGuardado) {
            return JSON.parse(usuarioGuardado);
        }

        return {
            id : 1,
            nombre: "Usuario demo",
            rol: "Operador"
        };
    });

    useEffect(() => {
        localStorage.setItem('usuarioActual', JSON.stringify(usuarioActual));
    }, [usuarioActual]);

    const alternarUsuario = () => {
        setUsuarioActual(prevUsuario =>
            prevUsuario.rol === 'Operador'
                ? { id: 2, nombre: 'Supervisor Demo', rol: 'Supervisor' }
                : { id: 1, nombre: 'Usuario Demo', rol: 'Operador' }
        );
    };

    return { usuarioActual, alternarUsuario };
};
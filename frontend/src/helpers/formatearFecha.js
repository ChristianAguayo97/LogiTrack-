export const formatearFecha = (stringFecha) => {
    if (!stringFecha) return '-';

    const fecha = new Date(stringFecha);

    return fecha.toLocaleString('es-AR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    });
}
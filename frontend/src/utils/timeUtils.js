/**
 * Formatea una fecha ISO a hora local del usuario
 * @param {string} isoString - Fecha en formato ISO
 * @returns {string} - Fecha formateada en hora local
 */
export const formatLocalDateTime = (isoString) => {
  if (!isoString) return 'N/A';
  
  const date = new Date(isoString);
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Formatea una fecha ISO a hora local (solo hora)
 * @param {string} isoString - Fecha en formato ISO
 * @returns {string} - Hora formateada
 */
export const formatLocalTime = (isoString) => {
  if (!isoString) return 'N/A';
  
  const date = new Date(isoString);
  return date.toLocaleTimeString('es-ES', {
    hour: '2-digit',
    minute: '2-digit'
  });
};

/**
 * Calcula la duración entre dos fechas en formato horas:minutos
 * @param {string} checkIn - Hora de entrada ISO
 * @param {string|null} checkOut - Hora de salida ISO (null si está en curso)
 * @returns {string} - Duración en formato "Xh Ym"
 */
export const calculateDuration = (checkIn, checkOut) => {
  if (!checkIn) return '0h 0m';
  
  const start = new Date(checkIn);
  const end = checkOut ? new Date(checkOut) : new Date();
  
  const diffMs = end - start;
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  
  return `${hours}h ${minutes}m`;
};

/**
 * Calcula las horas totales en formato decimal
 * @param {string} checkIn - Hora de entrada ISO
 * @param {string|null} checkOut - Hora de salida ISO
 * @returns {number} - Horas en formato decimal
 */
export const calculateTotalHours = (checkIn, checkOut) => {
  if (!checkIn || !checkOut) return 0;
  
  const start = new Date(checkIn);
  const end = new Date(checkOut);
  
  const diffMs = end - start;
  return (diffMs / (1000 * 60 * 60)).toFixed(2);
};

/**
 * Obtiene la fecha y hora actual del sistema del usuario en formato ISO
 * @returns {string} - Fecha actual en formato ISO
 */
export const getCurrentLocalDateTime = () => {
  return new Date().toISOString();
};

/**
 * Formatea una fecha ISO a formato datetime-local para inputs HTML
 * @param {string} isoString - Fecha en formato ISO
 * @returns {string} - Fecha formateada para input datetime-local
 */
export const formatForDateTimeInput = (isoString) => {
  if (!isoString) return '';
  
  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  
  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

/**
 * Convierte un valor de input datetime-local a formato ISO
 * @param {string} dateTimeLocalValue - Valor del input datetime-local
 * @returns {string} - Fecha en formato ISO
 */
export const dateTimeInputToISO = (dateTimeLocalValue) => {
  if (!dateTimeLocalValue) return null;
  return new Date(dateTimeLocalValue).toISOString();
};
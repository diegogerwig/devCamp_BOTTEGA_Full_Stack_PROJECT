// Formats an ISO date to user's local time
export const formatLocalDateTime = (isoString) => {
  if (!isoString) return "N/A";

  const date = new Date(isoString);
  return date.toLocaleString("es-ES", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Formats an ISO date to local time (time only)
export const formatLocalTime = (isoString) => {
  if (!isoString) return "N/A";

  const date = new Date(isoString);
  return date.toLocaleTimeString("es-ES", {
    hour: "2-digit",
    minute: "2-digit",
  });
};

// Calculates duration between two dates in hours:minutes format
export const calculateDuration = (checkIn, checkOut) => {
  if (!checkIn) return "0h 0m";

  const start = new Date(checkIn);
  const end = checkOut ? new Date(checkOut) : new Date();

  const diffMs = end - start;
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));

  return `${hours}h ${minutes}m`;
};

 // Calculates total hours in decimal format
export const calculateTotalHours = (checkIn, checkOut) => {
  if (!checkIn || !checkOut) return 0;

  const start = new Date(checkIn);
  const end = new Date(checkOut);

  const diffMs = end - start;
  return (diffMs / (1000 * 60 * 60)).toFixed(2);
};

// Gets current local date and time in backend-compatible format
export const getCurrentLocalDateTime = () => {
  const now = new Date();
  // Get timezone offset in minutes
  const timezoneOffset = now.getTimezoneOffset();
  // Adjust date for local time
  const localDate = new Date(now.getTime() - timezoneOffset * 60 * 1000);
  // Return ISO without Z (indicating UTC)
  return localDate.toISOString().slice(0, -1);
};

// Gets current date only in YYYY-MM-DD format
export const getCurrentLocalDate = () => {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// Formats an ISO date to datetime-local for HTML inputs
export const formatForDateTimeInput = (isoString) => {
  if (!isoString) return "";

  const date = new Date(isoString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const hours = String(date.getHours()).padStart(2, "0");
  const minutes = String(date.getMinutes()).padStart(2, "0");

  return `${year}-${month}-${day}T${hours}:${minutes}`;
};

// Converts datetime-local input value to ISO without UTC conversion
export const dateTimeInputToISO = (dateTimeLocalValue) => {
  if (!dateTimeLocalValue) return null;
  // Avoid new Date().toISOString() as it converts to UTC
  // Instead, append seconds and milliseconds
  return dateTimeLocalValue + ":00.000";
};
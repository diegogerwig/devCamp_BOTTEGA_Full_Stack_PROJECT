export interface User {
  id: number;
  name: string;
  email: string;
  role: 'admin' | 'manager' | 'worker';
  department: string;
  status: string;
  created_at: string;
}

export interface TimeEntry {
  id: number;
  user_id: number;
  date: string;
  check_in: string | null;
  check_out: string | null;
  total_hours: number | null;
  notes: string | null;
  created_at: string;
}

export interface ApiResponse<T> {
  message?: string;
  data?: T;
  success?: boolean;
}
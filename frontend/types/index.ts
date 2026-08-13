export type WorkOrderStatus = "DRAFT" | "RELEASED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CLOSED";

export type MachineStatus = "OPERATIONAL" | "IDLE" | "MAINTENANCE" | "OFFLINE" | "ERROR";

export interface Role {
  id: number;
  name: string;
  description?: string;
  created_at?: string;
}

export interface User {
  id: string;
  username: string;
  email: string;
  first_name?: string;
  last_name?: string;
  is_active: boolean;
  roles?: Role[];
}

export interface SystemHealth {
  overallStatus: "healthy" | "degraded" | "down";
  app: {
    name: string;
    environment: string;
  };
  database: {
    connected: boolean;
    details: string;
  };
  redis: {
    connected: boolean;
    details: string;
  };
}

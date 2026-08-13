export type WorkOrderStatus = "DRAFT" | "RELEASED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CLOSED";

export type MachineStatus = "OPERATIONAL" | "IDLE" | "MAINTENANCE" | "OFFLINE" | "ERROR";

export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
  isActive: boolean;
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

export type WorkOrderStatus = "DRAFT" | "RELEASED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CLOSED";

export type MachineStatus = "OPERATIONAL" | "IDLE" | "MAINTENANCE" | "OFFLINE" | "ERROR";

export type ProductionPlanStatus = "DRAFT" | "PLANNED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";

export type ProductionPlanPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

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

export interface Product {
  id: string;
  product_code: string;
  name: string;
  description?: string;
  unit_of_measure: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductionPlan {
  id: string;
  plan_number: string;
  product_id: string;
  product?: Product;
  planned_quantity: number;
  start_date: string;
  due_date: string;
  priority: ProductionPlanPriority;
  status: ProductionPlanStatus;
  notes?: string;
  created_by_id?: string;
  created_by?: User;
  created_at: string;
  updated_at: string;
}

export interface PaginatedProductionPlans {
  items: ProductionPlan[];
  total: number;
  page: number;
  limit: number;
  pages: number;
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

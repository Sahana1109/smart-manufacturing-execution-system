export type WorkOrderStatus = "DRAFT" | "RELEASED" | "IN_PROGRESS" | "PAUSED" | "COMPLETED" | "CLOSED" | "CANCELLED";

export type WorkOrderPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export type ProductionPlanStatus = "DRAFT" | "PLANNED" | "IN_PROGRESS" | "COMPLETED" | "CANCELLED";

export type ProductionPlanPriority = "LOW" | "MEDIUM" | "HIGH" | "URGENT";

export type MachineStatus = "OPERATIONAL" | "AVAILABLE" | "IN_USE" | "MAINTENANCE" | "INACTIVE";

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

export interface Machine {
  id: string;
  machine_code: string;
  name: string;
  status: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Employee {
  id: string;
  employee_code: string;
  first_name: string;
  last_name: string;
  role_title?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface DowntimeRecord {
  id: string;
  work_order_id: string;
  machine_id?: string;
  machine?: Machine;
  start_time: string;
  end_time?: string;
  duration_minutes?: number;
  reason: string;
  remarks?: string;
  recorded_by_id?: string;
  recorded_by?: User;
  created_at: string;
  updated_at: string;
}

export interface WorkOrder {
  id: string;
  work_order_number: string;
  production_plan_id: string;
  production_plan?: ProductionPlan;
  product_id: string;
  product?: Product;
  planned_quantity: number;
  produced_quantity: number;
  remaining_quantity?: number;
  progress_percentage?: number;
  start_date: string;
  due_date: string;
  actual_start_time?: string;
  actual_completion_time?: string;
  priority: WorkOrderPriority;
  status: WorkOrderStatus;
  notes?: string;
  created_by_id?: string;
  created_by?: User;
  assigned_machine_id?: string;
  assigned_machine?: Machine;
  assigned_employee_id?: string;
  assigned_employee?: Employee;
  downtime_records?: DowntimeRecord[];
  quality_status?: string;
  created_at: string;
  updated_at: string;
}

export type QualityStatus = "PENDING" | "PASSED" | "FAILED" | "REWORK_REQUIRED";

export type DefectType = "DIMENSIONAL" | "SURFACE" | "MATERIAL" | "ASSEMBLY" | "FUNCTIONAL" | "COSMETIC" | "OTHER";

export type DefectSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export interface QualityDefect {
  id: string;
  inspection_id: string;
  defect_type: DefectType;
  severity: DefectSeverity;
  description?: string;
  quantity: number;
  remarks?: string;
  created_at: string;
}

export interface QualityInspection {
  id: string;
  work_order_id: string;
  inspector_id?: string;
  inspected_quantity: number;
  accepted_quantity: number;
  rejected_quantity: number;
  status: QualityStatus;
  remarks?: string;
  inspection_date: string;
  created_at: string;
  updated_at: string;
  work_order_number?: string;
  product_name?: string;
  inspector_name?: string;
  defects?: QualityDefect[];
}

export interface QualitySummary {
  total_inspections: number;
  pending: number;
  passed: number;
  failed: number;
  rework_required: number;
  total_rejected_quantity: number;
  total_defects: number;
}

export interface WorkOrderExecution {
  work_order: WorkOrder;
  downtime_records: DowntimeRecord[];
  total_downtime_minutes: number;
}

export interface PaginatedProductionPlans {
  items: ProductionPlan[];
  total: number;
  page: number;
  limit: number;
  pages: number;
}

export interface PaginatedWorkOrders {
  items: WorkOrder[];
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

export type MaterialUnit = "PCS" | "KG" | "L" | "M" | "OTHER";

export type MovementType = "RECEIPT" | "RESERVATION" | "RELEASE" | "CONSUMPTION" | "ADJUSTMENT";

export interface InventoryStock {
  id: string;
  material_id: string;
  quantity: number;
  reserved_quantity: number;
  available_quantity: number;
  location: string;
  updated_at: string;
}

export interface Material {
  id: string;
  material_code: string;
  name: string;
  description?: string;
  unit: MaterialUnit;
  reorder_level: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  stock?: InventoryStock;
}

export interface StockMovement {
  id: string;
  material_id: string;
  material_code?: string;
  material_name?: string;
  work_order_id?: string;
  work_order_number?: string;
  movement_type: MovementType;
  quantity: number;
  reference?: string;
  performed_by_id?: string;
  performed_by_name?: string;
  created_at: string;
}

export interface InventoryDashboardSummary {
  total_materials: number;
  total_stock_items: number;
  low_stock_count: number;
  total_reserved_quantity: number;
}

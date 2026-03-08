export interface Gap {
  id: string;
  name: string;
  demand: number;
  supply: number;
  status: "acute_shortage" | "emerging_shortage" | "balanced";
  statusLabel: string;
}

export const gaps: Gap[] = [
  { id: "registered_nurse", name: "Registered Nurse", demand: 120, supply: 15, status: "acute_shortage", statusLabel: "Acute Shortage" },
  { id: "hvac_technician", name: "HVAC Technician", demand: 65, supply: 22, status: "emerging_shortage", statusLabel: "Emerging Shortage" },
  { id: "warehouse_associate", name: "Warehouse Associate", demand: 112, supply: 105, status: "balanced", statusLabel: "Balanced" },
  { id: "junior_developer", name: "Junior Developer", demand: 45, supply: 10, status: "emerging_shortage", statusLabel: "Emerging Shortage" },
];

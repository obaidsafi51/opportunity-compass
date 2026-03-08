// Maps skill IDs to relevant role IDs
export const skillToRoles: Record<string, string[]> = {
  nursing: ["nursing_assistant", "care_coordinator"],
  python: ["it_support_tech", "junior_web_developer"],
  customer_service: ["customer_service_lead"],
  warehouse_ops: ["warehouse_operations"],
  retail_mgmt: ["customer_service_lead"],
  hvac_tech: ["electrician_apprentice"],
  data_entry: ["it_support_tech"],
  hospitality: ["apprentice_hospitality"],
  cdl_driver: ["warehouse_operations", "grounds_maintenance"],
};

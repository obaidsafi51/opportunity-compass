export interface Programme {
  id: string;
  name: string;
  provider: string;
  duration: string;
  cost: string;
  costType: "free" | "funded" | "earn_while_learn";
  relevantRoles: string[];
  link: string;
  supportFlags: string[];
}

export const programmes: Programme[] = [
  {
    id: "mcc_nursing_cert",
    name: "Nursing Assistant Certificate",
    provider: "Montgomery Community College",
    duration: "12 weeks",
    cost: "Free (grant-funded)",
    costType: "free",
    relevantRoles: ["nursing_assistant"],
    link: "#",
    supportFlags: ["childcare_available", "evening_classes"],
  },
  {
    id: "mws_warehouse_safety",
    name: "Warehouse Ops & OSHA",
    provider: "Workforce Solutions",
    duration: "4 weeks",
    cost: "Free",
    costType: "free",
    relevantRoles: ["warehouse_operations"],
    link: "#",
    supportFlags: ["transportation_provided", "job_placement"],
  },
  {
    id: "y_apprenticeship",
    name: "Hospitality Apprenticeship",
    provider: "Y-Apprenticeships",
    duration: "12 months",
    cost: "Earn while you learn",
    costType: "earn_while_learn",
    relevantRoles: ["apprentice_hospitality"],
    link: "#",
    supportFlags: ["mentorship", "paid_training"],
  },
  {
    id: "cs_lead_training",
    name: "Customer Service Leadership",
    provider: "AL Career Center",
    duration: "6 weeks",
    cost: "Funded by WIA",
    costType: "funded",
    relevantRoles: ["customer_service_lead"],
    link: "#",
    supportFlags: ["job_placement", "evening_classes"],
  },
  {
    id: "it_support_cert",
    name: "CompTIA A+ Bootcamp",
    provider: "TechBridge Academy",
    duration: "12 weeks",
    cost: "Free (scholarship)",
    costType: "free",
    relevantRoles: ["it_support_tech"],
    link: "#",
    supportFlags: ["laptop_provided", "mentorship"],
  },
  {
    id: "care_coord_cert",
    name: "Care Coordination Certificate",
    provider: "Montgomery Health Dept",
    duration: "8 weeks",
    cost: "Funded",
    costType: "funded",
    relevantRoles: ["care_coordinator"],
    link: "#",
    supportFlags: ["childcare_available", "flexible_schedule"],
  },
  {
    id: "web_dev_bootcamp",
    name: "Full-Stack Web Dev Bootcamp",
    provider: "Code Montgomery",
    duration: "16 weeks",
    cost: "Free (youth grant)",
    costType: "free",
    relevantRoles: ["junior_web_developer"],
    link: "#",
    supportFlags: ["laptop_provided", "mentorship", "job_placement"],
  },
  {
    id: "electrician_trade",
    name: "Electrician Pre-Apprenticeship",
    provider: "IBEW Local 136",
    duration: "8 weeks",
    cost: "Earn while you learn",
    costType: "earn_while_learn",
    relevantRoles: ["electrician_apprentice"],
    link: "#",
    supportFlags: ["tool_stipend", "paid_training"],
  },
];

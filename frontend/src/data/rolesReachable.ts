export interface Role {
  title: string;
  roleId: string;
  fitReason: string;
  wageRange: string;
  trainingTime: string;
  postings: number;
  flags?: string[];
  barrierRequirements?: string[];
}

export interface Persona {
  id: string;
  label: string;
  roles: Role[];
}

export const personas: Persona[] = [
  {
    id: "general",
    label: "Recruiters",
    roles: [
      {
        title: "Nursing Assistant",
        roleId: "nursing_assistant",
        fitReason: "Strong demand in Montgomery; clear entry pathway with steady growth.",
        wageRange: "$28k – $32k",
        trainingTime: "8–12 weeks",
        postings: 142,
        barrierRequirements: [],
      },
      {
        title: "Customer Service Lead",
        roleId: "customer_service_lead",
        fitReason: "High volume of local openings; utilizes transferable communication skills.",
        wageRange: "$35k – $42k",
        trainingTime: "4–6 weeks",
        postings: 156,
        barrierRequirements: ["experience_required"],
      },
      {
        title: "IT Support Tech",
        roleId: "it_support_tech",
        fitReason: "Rising tech hub demand; certification-based entry without degree.",
        wageRange: "$40k – $48k",
        trainingTime: "12 weeks",
        postings: 54,
        barrierRequirements: ["car_required"],
      },
    ],
  },
  {
    id: "long_term_unemployed",
    label: "Long-term Unemployed",
    roles: [
      {
        title: "Warehouse Logistics",
        roleId: "warehouse_operations",
        fitReason: "Entry role with wrap-around support (coaching, transit); no prior experience required.",
        wageRange: "$26k – $30k",
        trainingTime: "2–4 weeks",
        postings: 112,
        flags: ["Transit Support", "Career Coaching"],
        barrierRequirements: [],
      },
      {
        title: "Care Coordinator",
        roleId: "care_coordinator",
        fitReason: "Value placed on life experience; many employers offer 'Return-to-Work' mentorship.",
        wageRange: "$31k – $36k",
        trainingTime: "6–8 weeks",
        postings: 42,
        flags: ["Flexible Hours"],
        barrierRequirements: ["car_required"],
      },
      {
        title: "Grounds Maintenance",
        roleId: "grounds_maintenance",
        fitReason: "Immediate start available; local municipal contracts with stable benefits.",
        wageRange: "$25k – $29k",
        trainingTime: "On-the-job",
        postings: 38,
        flags: ["Health Benefits"],
        barrierRequirements: [],
      },
    ],
  },
  {
    id: "neet_youth",
    label: "NEET Youth",
    roles: [
      {
        title: "Hospitality Apprentice",
        roleId: "apprentice_hospitality",
        fitReason: "Earn while you learn; Montgomery youth voucher eligible; focus on social skills.",
        wageRange: "$18k – $22k",
        trainingTime: "12 months (Apprenticeship)",
        postings: 134,
        flags: ["Mentorship", "Paid Training"],
        barrierRequirements: [],
      },
      {
        title: "Junior Web Developer",
        roleId: "junior_web_developer",
        fitReason: "High engagement 'Bootcamp' path; focus on portfolio building over credentials.",
        wageRange: "$40k – $50k",
        trainingTime: "16 weeks",
        postings: 45,
        flags: ["Laptop Provided", "Remote Options"],
        barrierRequirements: ["degree_required"],
      },
      {
        title: "Electrician Apprentice",
        roleId: "electrician_apprentice",
        fitReason: "Direct pathway to $60k+ career; no debt; high demand in local construction.",
        wageRange: "$22k – $26k (Starting)",
        trainingTime: "Ongoing (Trade School)",
        postings: 29,
        flags: ["Tool Stipend"],
        barrierRequirements: ["car_required"],
      },
    ],
  },
];

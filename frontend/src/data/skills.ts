export interface Skill {
  id: string;
  name: string;
  postings: number;
  percentChange: number;
  isRising: boolean;
  icon: string;
}

export const skills: Skill[] = [
  { id: "nursing", name: "Nursing/Healthcare", postings: 142, percentChange: 12, isRising: true, icon: "PlusSquare" },
  { id: "python", name: "Software Development (Python)", postings: 89, percentChange: 5, isRising: true, icon: "Code" },
  { id: "customer_service", name: "Customer Service", postings: 156, percentChange: -3, isRising: false, icon: "Headphones" },
  { id: "warehouse_ops", name: "Warehouse & Logistics", postings: 112, percentChange: 8, isRising: true, icon: "Package" },
  { id: "retail_mgmt", name: "Retail Management", postings: 94, percentChange: 2, isRising: false, icon: "Store" },
  { id: "hvac_tech", name: "HVAC & Skilled Trades", postings: 67, percentChange: 15, isRising: true, icon: "Wrench" },
  { id: "data_entry", name: "Admin & Data Entry", postings: 45, percentChange: -10, isRising: false, icon: "FileText" },
  { id: "hospitality", name: "Hospitality & Food Service", postings: 134, percentChange: 4, isRising: true, icon: "Coffee" },
  { id: "cdl_driver", name: "Heavy Truck Driving (CDL)", postings: 78, percentChange: 9, isRising: true, icon: "Truck" },
];

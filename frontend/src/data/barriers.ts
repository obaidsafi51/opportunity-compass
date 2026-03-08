export interface Barrier {
  id: string;
  label: string;
  description: string;
}

export const barriers: Barrier[] = [
  {
    id: "degree_required",
    label: "Hide roles requiring a degree",
    description: "Exclude bachelor's degree or higher",
  },
  {
    id: "car_required",
    label: "Hide roles requiring a car/transport",
    description: "Exclude roles needing personal vehicle",
  },
  {
    id: "experience_required",
    label: "Hide roles requiring 1+ year experience",
    description: "Show only entry-level roles",
  },
];

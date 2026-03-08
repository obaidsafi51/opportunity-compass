import { useMemo } from "react";
import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "@/lib/utils";
import { skillToRoles } from "@/data/skillRoleMap";
import { Briefcase, Clock, DollarSign, Tag, AlertTriangle, ExternalLink, GraduationCap, ArrowRight, Monitor, Image, Shield } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { ScrollArea, ScrollBar } from "@/components/ui/scroll-area";

const BARRIER_LABELS: Record<string, string> = {
  degree_required: "No Degree",
  car_required: "No Car",
  experience_required: "No Experience",
};

const SUPPORT_FLAG_DISPLAY: Record<string, string> = {
  childcare_available: "🍼 Childcare",
  evening_classes: "🌙 Evening",
  transportation_provided: "🚌 Transit",
  job_placement: "💼 Placement",
  mentorship: "🤝 Mentorship",
  paid_training: "💰 Paid Training",
  laptop_provided: "💻 Laptop",
  flexible_schedule: "⏰ Flexible",
  tool_stipend: "🔧 Tool Stipend",
};

const roleIcons: Record<string, React.ElementType> = {
  nursing_assistant: Shield,
  customer_service_lead: Monitor,
  it_support_tech: Monitor,
  warehouse_operations: Briefcase,
  care_coordinator: Shield,
  grounds_maintenance: Briefcase,
  apprentice_hospitality: Briefcase,
  junior_web_developer: Image,
  electrician_apprentice: Briefcase,
};

export interface Role {
  roleId: string;
  title: string;
  fitReason: string;
  wageRange: string;
  trainingTime: string;
  barrierRequirements?: string[];
  flags?: string[];
}

export interface Programme {
  id: string;
  name: string;
  provider: string;
  duration: string;
  costType: "free" | "earn_while_learn" | "paid";
  relevantRoles: string[];
}

const RoleCard = ({
  role,
  isBlocked,
  blockedBarriers,
  isDimmed,
}: {
  role: Role;
  isBlocked: boolean;
  blockedBarriers: string[];
  isDimmed: boolean;
}) => {
  const Icon = roleIcons[role.roleId] || Briefcase;

  return (
    <div
      className={`flex flex-col rounded-lg border border-border bg-card p-5 transition-all ${
        isBlocked
          ? "opacity-40 grayscale"
          : isDimmed
            ? "opacity-30"
            : "hover:border-[hsl(270,80%,55%)]/40 hover:shadow-lg hover:shadow-[hsl(270,80%,55%)]/5"
      }`}
    >
      <div className="flex items-start justify-between">
        <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[hsl(270,80%,55%)]/15">
          <Icon className="h-4 w-4 text-[hsl(270,80%,65%)]" />
        </div>
        {role.flags && role.flags.length > 0 && (
          <div className="flex gap-1.5">
            {role.flags.map((flag) => (
              <span
                key={flag}
                className="rounded bg-[hsl(270,80%,55%)]/20 px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[hsl(270,80%,65%)]"
              >
                {flag}
              </span>
            ))}
          </div>
        )}
      </div>

      <h3 className="mt-3 text-base font-bold">{role.title}</h3>

      {isBlocked && blockedBarriers.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1.5">
          {blockedBarriers.map((b) => (
            <Badge key={b} variant="destructive" className="gap-1 text-[10px]">
              <AlertTriangle className="h-2.5 w-2.5" />
              {BARRIER_LABELS[b] || b}
            </Badge>
          ))}
        </div>
      )}

      <p className="mt-2 flex-1 text-sm leading-relaxed text-muted-foreground">{role.fitReason}</p>

      <div className="mt-3 flex flex-wrap gap-1.5">
        {role.barrierRequirements && role.barrierRequirements.length === 0 && (
          <span className="rounded bg-[hsl(152,60%,45%)]/15 px-2 py-0.5 text-[10px] font-semibold text-[hsl(152,60%,45%)]">
            No Degree
          </span>
        )}
      </div>

      <div className="mt-3 flex items-center gap-4 text-xs text-muted-foreground">
        <div className="flex items-center gap-1 text-[hsl(152,60%,45%)]">
          <DollarSign className="h-3 w-3" />
          <span className="font-mono font-semibold">{role.wageRange}</span>
        </div>
        <div className="flex items-center gap-1">
          <Clock className="h-3 w-3" />
          <span>{role.trainingTime}</span>
        </div>
      </div>

      <button
        className={`mt-4 w-full rounded-lg py-2.5 text-sm font-bold transition-all ${
          isBlocked || isDimmed
            ? "border border-border text-muted-foreground"
            : "bg-[hsl(270,80%,55%)] text-foreground hover:bg-[hsl(270,80%,60%)]"
        }`}
      >
        {isBlocked ? "Restricted" : "Apply Now"}
      </button>
    </div>
  );
};

const ProgrammeCard = ({ programme }: { programme: Programme }) => {
  const costLabel =
    programme.costType === "free"
      ? "FREE"
      : programme.costType === "earn_while_learn"
        ? "EARN WHILE YOU LEARN"
        : programme.duration.toUpperCase();

  const costColor =
    programme.costType === "free"
      ? "bg-[hsl(152,60%,45%)] text-[hsl(220,20%,7%)]"
      : programme.costType === "earn_while_learn"
        ? "bg-[hsl(38,92%,55%)] text-[hsl(220,20%,7%)]"
        : "bg-muted text-foreground";

  return (
    <div className="group flex w-[260px] shrink-0 flex-col overflow-hidden rounded-lg border border-border bg-card transition-all hover:border-[hsl(270,80%,55%)]/40">
      {/* Gradient image area */}
      <div className="relative h-28 w-full overflow-hidden bg-gradient-to-br from-[hsl(270,40%,15%)] via-[hsl(30,40%,15%)] to-[hsl(270,40%,10%)]">
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,hsl(30,60%,25%)/0.5,transparent_70%)]" />
        <span className={`absolute bottom-2 left-3 rounded px-2 py-0.5 text-[9px] font-bold uppercase tracking-wider ${costColor}`}>
          {costLabel}
        </span>
      </div>
      <div className="flex flex-1 flex-col p-4">
        <h4 className="text-sm font-bold leading-tight">{programme.name}</h4>
        <p className="mt-1 text-xs leading-relaxed text-muted-foreground">
          {programme.provider}
        </p>
        <div className="mt-auto flex items-center justify-between pt-3">
          <span className="text-[10px] font-bold uppercase tracking-wider text-[hsl(270,80%,65%)]">
            {programme.duration}
          </span>
          <ArrowRight className="h-4 w-4 text-muted-foreground transition-colors group-hover:text-[hsl(270,80%,65%)]" />
        </div>
      </div>
    </div>
  );
};

interface PersonaCardsProps {
  selectedSkill: string | null;
  activePersona: string;
  onPersonaChange: (id: string) => void;
  activeBarriers: string[];
  onBarriersChange: (barriers: string[]) => void;
}

const PersonaCards = ({ selectedSkill, activePersona, onPersonaChange, activeBarriers, onBarriersChange }: PersonaCardsProps) => {

  const { data: roles = [], isLoading: loadingRoles } = useQuery({
    queryKey: ["opportunities", activePersona],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/opportunities?persona=${activePersona}`);
      if (!res.ok) throw new Error("Failed to fetch opportunities");
      const json = await res.json();
      return (json.data || []).map((r: any) => {
        const barriers = [];
        if (r.barriers?.requires_degree) barriers.push("degree_required");
        if (r.barriers?.requires_vehicle) barriers.push("car_required");
        if (r.barriers?.requires_experience_1yr) barriers.push("experience_required");
        
        return {
          roleId: r.job_title.toLowerCase().replace(/\\s+/g, "_"),
          title: r.job_title,
          fitReason: r.fit_reason || "Matches your current experience level.",
          wageRange: r.wage_range,
          trainingTime: r.training_weeks > 0 ? `${r.training_weeks} weeks` : "No training required",
          barrierRequirements: barriers,
          flags: [r.demand_count > 10 ? "HIGH DEMAND" : ""].filter(Boolean)
        } as Role;
      });
    },
  });

  const { data: fetchProgrammes = [], isLoading: loadingProgs } = useQuery({
    queryKey: ["programs"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/programs`);
      if (!res.ok) throw new Error("Failed to fetch programs");
      const json = await res.json();
      return (json.data || []).map((p: any) => ({
        id: p.name.toLowerCase().replace(/\\s+/g, "_"),
        name: p.name,
        provider: p.provider,
        duration: "Flexible", // Stub
        costType: p.name.includes("Apprenticeship") ? "earn_while_learn" : "free",
        relevantRoles: [], // We don't have perfect mapping yet, show all dynamically below
      } as Programme));
    },
  });

  const getBlockedBarriers = (role: Role): string[] => {
    if (!role.barrierRequirements) return [];
    return role.barrierRequirements.filter((b) => activeBarriers.includes(b));
  };

  const relevantRoleIds = useMemo(() => {
    if (!selectedSkill) return null;
    return new Set(skillToRoles[selectedSkill] || []);
  }, [selectedSkill]);

  const isRoleDimmed = (role: Role): boolean => {
    if (!relevantRoleIds) return false;
    return !relevantRoleIds.has(role.roleId);
  };

  const relevantProgrammes = useMemo(() => {
    // For now we just show all since we are generating them dynamically
    return fetchProgrammes;
  }, [fetchProgrammes]);

  return (
    <div className="space-y-4">
      {/* Reachable Roles */}
      <div>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-black tracking-tight">Reachable Roles</h2>
          <span className="text-xs italic text-muted-foreground">
            {loadingRoles ? "Loading roles..." : "Showing matches for your current filters"}
          </span>
        </div>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          {roles.slice(0, 3).map((role: Role) => {
            const blocked = getBlockedBarriers(role);
            return (
              <RoleCard
                key={role.title}
                role={role}
                isBlocked={blocked.length > 0}
                blockedBarriers={blocked}
                isDimmed={isRoleDimmed(role)}
              />
            );
          })}
        </div>
      </div>

      {/* Training Paths Rail */}
      {relevantProgrammes.length > 0 && (
        <div className="rounded-lg border border-border bg-card p-4">
          <div className="mb-3 flex items-center gap-2">
            <GraduationCap className="h-4 w-4 text-[hsl(270,80%,65%)]" />
            <h3 className="text-sm font-bold">Training Paths Rail</h3>
          </div>
          <ScrollArea className="w-full">
            <div className="flex gap-4 pb-3">
              {relevantProgrammes.map((prog) => (
                <ProgrammeCard key={prog.id} programme={prog} />
              ))}
            </div>
            <ScrollBar orientation="horizontal" />
          </ScrollArea>
        </div>
      )}
    </div>
  );
};

export default PersonaCards;

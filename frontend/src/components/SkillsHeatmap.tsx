import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "@/lib/utils";
import { TrendingUp, TrendingDown, PlusSquare, Code, Headphones, Package, Store, Wrench, FileText, Coffee, Truck, Grid3X3, ChevronDown, ChevronUp } from "lucide-react";

export interface Skill {
  id: string;
  name: string;
  icon: string;
  isRising: boolean;
  percentChange: number;
  postings: number;
}

const iconMap: Record<string, React.ElementType> = {
  PlusSquare, Code, Headphones, Package, Store, Wrench, FileText, Coffee, Truck,
};

const trendLabel = (skill: Skill) => {
  if (skill.isRising && skill.percentChange >= 10) return "HIGH DEMAND";
  if (skill.isRising) return "MODERATE GROWTH";
  return "SATURATING";
};

const trendColor = (skill: Skill) => {
  if (skill.isRising && skill.percentChange >= 10) return "border-l-[hsl(152,60%,45%)]";
  if (skill.isRising) return "border-l-[hsl(200,90%,50%)]";
  return "border-l-[hsl(0,72%,55%)]";
};

const SkillRow = ({
  skill,
  isSelected,
  onClick,
}: {
  skill: Skill;
  isSelected: boolean;
  onClick: () => void;
}) => {
  const Icon = iconMap[skill.icon] || PlusSquare;

  return (
    <div
      onClick={onClick}
      className={`group flex cursor-pointer items-center gap-3 rounded-lg border-l-[3px] px-4 py-3.5 transition-all ${trendColor(skill)} ${
        isSelected
          ? "bg-[hsl(270,80%,55%)]/10 ring-1 ring-[hsl(270,80%,55%)]/30"
          : "bg-secondary/30 hover:bg-secondary/60"
      }`}
    >
      <Icon className={`h-4 w-4 shrink-0 ${isSelected ? "text-[hsl(270,80%,65%)]" : "text-muted-foreground"}`} />
      <div className="min-w-0 flex-1">
        <span className="text-sm font-semibold">{skill.name}</span>
        {skill.isRising && (
          <span className="ml-2 inline-block rounded bg-[hsl(152,60%,45%)]/20 px-1.5 py-0.5 text-[9px] font-bold uppercase tracking-wider text-[hsl(152,60%,45%)]">
            Rising Skill
          </span>
        )}
      </div>
      <div className="flex flex-col items-end gap-0.5">
        <span className={`font-mono text-sm font-bold ${skill.isRising ? "text-[hsl(152,60%,45%)]" : "text-[hsl(0,72%,55%)]"}`}>
          {skill.percentChange > 0 ? "+" : ""}{skill.percentChange}%
        </span>
        <span className="text-[9px] font-bold uppercase tracking-wider text-muted-foreground">
          {trendLabel(skill)}
        </span>
      </div>
    </div>
  );
};

const INITIAL_COUNT = 4; // Show up to Warehouse & Logistics

const SkillsHeatmap = ({
  selectedSkill,
  onSelectSkill,
}: {
  selectedSkill: string | null;
  onSelectSkill: (id: string | null) => void;
}) => {
  const [expanded, setExpanded] = useState(false);
  const { data: apiSkills = [], isLoading } = useQuery({
    queryKey: ["skills"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/skills`);
      if (!res.ok) throw new Error("Failed to fetch skills");
      const json = await res.json();
      return (json.data || []).map((row: any) => ({
        id: row.skill.toLowerCase().replace(/\\s+/g, "-"),
        name: row.skill,
        icon: "PlusSquare", // Fallback icon
        isRising: row.is_rising,
        percentChange: row.pct_change,
        postings: row.count,
      } as Skill));
    },
  });

  const sorted = [...apiSkills].sort((a, b) => b.postings - a.postings);
  const visible = expanded ? sorted : sorted.slice(0, INITIAL_COUNT);

  return (
    <div className="flex h-full flex-col rounded-lg border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
        <div className="flex items-center gap-2">
          <Grid3X3 className="h-4 w-4 text-[hsl(270,80%,65%)]" />
          <h2 className="text-sm font-bold">Skills Heatmap</h2>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-[10px] font-medium text-muted-foreground">Demand velocity (30d)</span>
          {selectedSkill && (
            <button
              onClick={() => onSelectSkill(null)}
              className="ml-2 text-[10px] font-semibold uppercase tracking-wider text-[hsl(270,80%,65%)] hover:underline"
            >
              Clear filter
            </button>
          )}
        </div>
      </div>
      <div className="flex-1 space-y-2 overflow-y-auto p-4">
        {isLoading && (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Loading skills...
          </div>
        )}
        {visible.map((skill) => (
          <SkillRow
            key={skill.id}
            skill={skill}
            isSelected={selectedSkill === skill.id}
            onClick={() => onSelectSkill(selectedSkill === skill.id ? null : skill.id)}
          />
        ))}
        {sorted.length > INITIAL_COUNT && (
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex w-full items-center justify-center gap-1.5 rounded-lg border border-border py-2 text-xs font-semibold text-muted-foreground transition-all hover:border-[hsl(270,80%,55%)]/40 hover:text-foreground"
          >
            {expanded ? (
              <>Show Less <ChevronUp className="h-3.5 w-3.5" /></>
            ) : (
              <>Show {sorted.length - INITIAL_COUNT} More <ChevronDown className="h-3.5 w-3.5" /></>
            )}
          </button>
        )}
      </div>
    </div>
  );
};

export default SkillsHeatmap;

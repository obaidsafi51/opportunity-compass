import { useQuery } from "@tanstack/react-query";
import { Calendar, ExternalLink } from "lucide-react";
import { API_BASE } from "@/lib/utils";

export interface Gap {
  id: string;
  name: string;
  demand: number;
  supply: number;
  status: "acute_shortage" | "emerging_shortage" | "balanced";
  pipelineText?: string;
}

const statusConfig: Record<Gap["status"], { label: string; color: string }> = {
  acute_shortage: { label: "ACUTE SHORTAGE", color: "text-[hsl(0,72%,55%)]" },
  emerging_shortage: { label: "EMERGING SHORTAGE", color: "text-[hsl(38,92%,55%)]" },
  balanced: { label: "BALANCED", color: "text-[hsl(152,60%,45%)]" },
};

const GapRow = ({ gap }: { gap: Gap }) => {
  const pipelineText = gap.pipelineText || `${gap.demand} Openings / ${gap.supply} Applicants`;

  return (
    <div className="flex items-center justify-between rounded-lg border border-border bg-secondary/30 px-4 py-3 transition-colors hover:bg-secondary/50">
      <span className="text-sm font-semibold">{gap.name}</span>
      <span className="text-xs text-muted-foreground">{pipelineText}</span>
    </div>
  );
};

const TrainingGapPanel = () => {
  const { data: apiGaps = [], isLoading } = useQuery({
    queryKey: ["gaps"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/gaps`);
      if (!res.ok) throw new Error("Failed to fetch gaps");
      const json = await res.json();
      return (json.data || []).map((row: any) => ({
        id: row.occupation.toLowerCase().replace(/\\s+/g, "-"),
        name: row.occupation,
        status: row.severity === "acute" ? "acute_shortage" 
              : row.severity === "emerging" ? "emerging_shortage" 
              : "balanced",
        demand: 0,
        supply: 0,
        pipelineText: row.aligned_programs?.[0] ? `Recommended: ${row.aligned_programs[0].name}` : "Needs mapping",
      } as Gap));
    },
  });

  const grouped = {
    acute_shortage: apiGaps.filter((g: Gap) => g.status === "acute_shortage"),
    emerging_shortage: apiGaps.filter((g: Gap) => g.status === "emerging_shortage"),
    balanced: apiGaps.filter((g: Gap) => g.status === "balanced"),
  };

  return (
    <div className="flex h-full flex-col rounded-lg border border-border bg-card">
      <div className="flex items-center justify-between border-b border-border px-5 py-3.5">
        <div className="flex items-center gap-2">
          <Calendar className="h-4 w-4 text-[hsl(270,80%,65%)]" />
          <h2 className="text-sm font-bold">Training Gap Panel</h2>
        </div>
        <button className="text-[10px] font-bold uppercase tracking-wider text-[hsl(270,80%,65%)] hover:underline">
          View Analysis
        </button>
      </div>
      <div className="flex-1 space-y-5 overflow-y-auto p-4">
        {isLoading && (
          <div className="flex h-full items-center justify-center text-sm text-muted-foreground">
            Loading analysis...
          </div>
        )}
        {(Object.keys(grouped) as Gap["status"][]).map((status) => {
          const items = grouped[status];
          if (items.length === 0) return null;
          const config = statusConfig[status];
          return (
            <div key={status}>
              <p className={`mb-2 text-[10px] font-bold uppercase tracking-[0.15em] ${config.color}`}>
                {config.label}
              </p>
              <div className="space-y-2">
                {items.map((gap) => (
                  <GapRow key={gap.id} gap={gap} />
                ))}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default TrainingGapPanel;

import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from "recharts";
import { skills } from "@/data/skills";

const CustomTooltip = ({ active, payload }: any) => {
  if (!active || !payload?.length) return null;
  const d = payload[0].payload;
  return (
    <div className="rounded-md border border-border bg-card px-3 py-2 text-xs shadow-lg">
      <p className="font-semibold">{d.fullName}</p>
      <p className="font-mono text-primary">{d.postings} postings</p>
      <p className={d.isRising ? "text-success" : "text-danger"}>
        {d.change > 0 ? "+" : ""}{d.change}% change
      </p>
    </div>
  );
};

const SkillsChart = ({
  selectedSkill,
  onSelectSkill,
}: {
  selectedSkill: string | null;
  onSelectSkill: (id: string | null) => void;
}) => {
  const chartData = [...skills]
    .sort((a, b) => b.postings - a.postings)
    .map((s) => ({
      id: s.id,
      name: s.name.length > 18 ? s.name.slice(0, 16) + "…" : s.name,
      fullName: s.name,
      postings: s.postings,
      change: s.percentChange,
      isRising: s.isRising,
    }));

  const handleClick = (data: any) => {
    if (data?.id) {
      onSelectSkill(selectedSkill === data.id ? null : data.id);
    }
  };

  return (
    <div className="flex h-full flex-col rounded-lg border border-border bg-card">
      <div className="border-b border-border px-4 py-3">
        <h2 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">
          Demand Overview
        </h2>
      </div>
      <div className="flex-1 p-4">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 8, right: 16, top: 4, bottom: 4 }}
            onClick={(e) => e?.activePayload?.[0] && handleClick(e.activePayload[0].payload)}
            style={{ cursor: "pointer" }}
          >
            <XAxis type="number" hide />
            <YAxis
              type="category"
              dataKey="name"
              width={120}
              tick={{ fill: "hsl(215 15% 55%)", fontSize: 11, fontFamily: "Inter" }}
              axisLine={false}
              tickLine={false}
            />
            <Tooltip content={<CustomTooltip />} cursor={{ fill: "hsl(220 14% 14%)" }} />
            <Bar dataKey="postings" radius={[0, 4, 4, 0]} barSize={18}>
              {chartData.map((entry, i) => (
                <Cell
                  key={i}
                  fill={
                    selectedSkill && selectedSkill !== entry.id
                      ? "hsl(215 15% 20%)"
                      : entry.isRising
                        ? "hsl(200 90% 50%)"
                        : "hsl(215 15% 35%)"
                  }
                  style={{ cursor: "pointer" }}
                />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

export default SkillsChart;

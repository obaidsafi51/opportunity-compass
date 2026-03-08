import { MapPin, Clock, RotateCcw, Bell, BarChart3, Menu, X } from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { API_BASE } from "@/lib/utils";

interface TopNavProps {
  onResetProfile: () => void;
}

const TopNav = ({ onResetProfile }: TopNavProps) => {
  const [mobileOpen, setMobileOpen] = useState(false);
  const { data: summaryData } = useQuery({
    queryKey: ["summary"],
    queryFn: async () => {
      const res = await fetch(`${API_BASE}/api/summary`);
      if (!res.ok) throw new Error("Failed to fetch summary");
      const json = await res.json();
      return json.data;
    },
  });

  const updated = new Date(); // Or use a timestamp from backend if available
  const formattedDate = updated.toLocaleDateString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
  });

  const city = "Montgomery, AL";
  const activePostings = summaryData?.total_open_jobs || 1420;
  const unemploymentRate = summaryData?.unemployment_rate || 2.7;

  return (
    <header className="border-b border-border bg-card">
      <div className="flex items-center justify-between px-4 py-3 sm:px-6">
        <Link to="/" className="flex items-center gap-2">
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary">
            <BarChart3 className="h-4 w-4 text-primary-foreground" />
          </div>
          <h1 className="text-base font-black uppercase tracking-tight">Workforce Pulse</h1>
        </Link>

        {/* Desktop stats */}
        <div className="hidden items-center gap-5 md:flex">
          <div className="flex items-center gap-1.5 text-xs">
            <MapPin className="h-3.5 w-3.5 text-primary" />
            <span className="font-semibold">{city}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
            <Clock className="h-3.5 w-3.5" />
            <span>Updated {formattedDate}</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <span className="font-mono font-bold text-primary">{activePostings.toLocaleString()}</span>
            <span className="text-muted-foreground">Active Postings</span>
          </div>
          <div className="flex items-center gap-1.5 text-xs">
            <span className="font-mono font-bold text-[hsl(152,60%,45%)]">{unemploymentRate}%</span>
            <span className="text-muted-foreground">Unemployment</span>
          </div>
          <button className="relative rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground">
            <Bell className="h-4 w-4" />
          </button>
          <button
            onClick={onResetProfile}
            className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all hover:bg-primary/80"
            title="Reset Profile"
          >
            <RotateCcw className="h-3.5 w-3.5" />
          </button>
        </div>

        {/* Mobile toggle */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="rounded-lg p-2 text-muted-foreground hover:bg-secondary hover:text-foreground md:hidden"
        >
          {mobileOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {/* Mobile dropdown */}
      {mobileOpen && (
        <div className="flex flex-col gap-3 border-t border-border px-4 py-3 md:hidden">
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs">
              <MapPin className="h-3.5 w-3.5 text-primary" />
              <span className="font-semibold">{city}</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
              <Clock className="h-3.5 w-3.5" />
              <span>Updated {formattedDate}</span>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-4">
            <div className="flex items-center gap-1.5 text-xs">
              <span className="font-mono font-bold text-primary">{activePostings.toLocaleString()}</span>
              <span className="text-muted-foreground">Active Postings</span>
            </div>
            <div className="flex items-center gap-1.5 text-xs">
              <span className="font-mono font-bold text-[hsl(152,60%,45%)]">{unemploymentRate}%</span>
              <span className="text-muted-foreground">Unemployment</span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button className="relative rounded-lg p-2 text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground">
              <Bell className="h-4 w-4" />
            </button>
            <button
              onClick={() => { onResetProfile(); setMobileOpen(false); }}
              className="flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground transition-all hover:bg-primary/80"
              title="Reset Profile"
            >
              <RotateCcw className="h-3.5 w-3.5" />
            </button>
          </div>
        </div>
      )}
    </header>
  );
};

export default TopNav;

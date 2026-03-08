import { useState, useCallback } from "react";
import TopNav from "@/components/TopNav";
import SkillsHeatmap from "@/components/SkillsHeatmap";
import TrainingGapPanel from "@/components/TrainingGapPanel";
import PersonaCards from "@/components/PersonaCards";
import Footer from "@/components/Footer";
import OnboardingModal from "@/components/OnboardingModal";
import { personas } from "@/data/rolesReachable";
import { barriers } from "@/data/barriers";
import { Checkbox } from "@/components/ui/checkbox";

const Index = () => {
  const [selectedSkill, setSelectedSkill] = useState<string | null>(null);
  const [showOnboarding, setShowOnboarding] = useState(() => {
    return !localStorage.getItem("pulse_profile");
  });
  const [activePersona, setActivePersona] = useState<string>("general");
  const [activeBarriers, setActiveBarriers] = useState<string[]>([]);

  const handleOnboardingComplete = useCallback((persona: string, b: string[]) => {
    setActivePersona(persona);
    setActiveBarriers(b);
    setShowOnboarding(false);
    localStorage.setItem("pulse_profile", JSON.stringify({ persona, barriers: b }));
  }, []);

  const handleResetProfile = useCallback(() => {
    localStorage.removeItem("pulse_profile");
    setActivePersona("general");
    setActiveBarriers([]);
    setShowOnboarding(true);
  }, []);

  const toggleBarrier = (id: string) => {
    setActiveBarriers((prev) =>
      prev.includes(id) ? prev.filter((b) => b !== id) : [...prev, id]
    );
  };

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <TopNav onResetProfile={handleResetProfile} />
      <OnboardingModal open={showOnboarding} onComplete={handleOnboardingComplete} />

      <div className="flex flex-1 flex-col gap-0 p-4 pt-3">
        {/* Persona Focus + Barrier Filters Bar */}
        <div className="mb-4 flex flex-wrap items-start gap-8 rounded-lg border border-border bg-card px-5 py-4">
          <div>
            <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-[hsl(270,80%,65%)]">
              Persona Focus
            </p>
            <div className="flex gap-2">
              {personas.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setActivePersona(p.id)}
                  className={`rounded-md px-4 py-2 text-sm font-semibold transition-all ${
                    p.id === activePersona
                      ? "bg-[hsl(270,80%,55%)] text-foreground"
                      : "bg-secondary text-secondary-foreground hover:bg-secondary/80"
                  }`}
                >
                  {p.label}
                </button>
              ))}
            </div>
          </div>

          <div>
            <p className="mb-2 text-[10px] font-bold uppercase tracking-[0.15em] text-[hsl(270,80%,65%)]">
              Barrier Filters
            </p>
            <div className="flex flex-wrap gap-4">
              {barriers.map((b) => (
                <label
                  key={b.id}
                  className={`flex cursor-pointer items-center gap-2.5 rounded-lg border px-4 py-2 text-xs transition-all ${
                    activeBarriers.includes(b.id)
                      ? "border-[hsl(270,80%,55%)] bg-[hsl(270,80%,55%)]/10 text-foreground"
                      : "border-border text-muted-foreground hover:border-muted-foreground/40 hover:text-foreground"
                  }`}
                >
                  <Checkbox
                    checked={activeBarriers.includes(b.id)}
                    onCheckedChange={() => toggleBarrier(b.id)}
                    className="data-[state=checked]:bg-[hsl(270,80%,55%)] data-[state=checked]:border-[hsl(270,80%,55%)]"
                  />
                  <span>{b.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        {/* Skills Heatmap + Training Gap Panel — 2 col */}
        <div className="mb-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <SkillsHeatmap selectedSkill={selectedSkill} onSelectSkill={setSelectedSkill} />
          <TrainingGapPanel />
        </div>

        {/* Reachable Roles + Training Rail */}
        <PersonaCards
          selectedSkill={selectedSkill}
          activePersona={activePersona}
          onPersonaChange={setActivePersona}
          activeBarriers={activeBarriers}
          onBarriersChange={setActiveBarriers}
        />
      </div>
      <Footer />
    </div>
  );
};

export default Index;

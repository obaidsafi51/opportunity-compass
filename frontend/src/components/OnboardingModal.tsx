import { useState } from "react";
import { Dialog, DialogContent, DialogTitle } from "@/components/ui/dialog";
import { Checkbox } from "@/components/ui/checkbox";
import { Users, Briefcase, GraduationCap, ArrowRight, ArrowLeft } from "lucide-react";

const personaOptions = [
  { id: "general", label: "Recruiters", description: "Hiring and talent acquisition", icon: Briefcase },
  { id: "long_term_unemployed", label: "Long-term Unemployed", description: "Returning to the workforce", icon: Users },
  { id: "neet_youth", label: "NEET Youth", description: "Starting your career journey", icon: GraduationCap },
] as const;

const barrierOptions = [
  { id: "degree_required", label: "No Degree", description: "I don't have a college degree" },
  { id: "car_required", label: "No Car", description: "I don't have reliable transportation" },
  { id: "experience_required", label: "No Experience", description: "I have little or no work experience" },
] as const;

interface OnboardingModalProps {
  open: boolean;
  onComplete: (persona: string, barriers: string[]) => void;
}

const OnboardingModal = ({ open, onComplete }: OnboardingModalProps) => {
  const [step, setStep] = useState(1);
  const [selectedPersona, setSelectedPersona] = useState<string | null>(null);
  const [selectedBarriers, setSelectedBarriers] = useState<string[]>([]);

  const toggleBarrier = (id: string) => {
    setSelectedBarriers((prev) =>
      prev.includes(id) ? prev.filter((b) => b !== id) : [...prev, id]
    );
  };

  const handleComplete = () => {
    if (selectedPersona) {
      onComplete(selectedPersona, selectedBarriers);
    }
  };

  return (
    <Dialog open={open}>
      <DialogContent
        className="max-w-lg border-border bg-card sm:max-w-xl [&>button]:hidden"
        onPointerDownOutside={(e) => e.preventDefault()}
        onEscapeKeyDown={(e) => e.preventDefault()}
      >
        <DialogTitle className="sr-only">Onboarding</DialogTitle>

        {/* Progress indicator */}
        <div className="mb-6 flex items-center gap-2">
          <div className={`h-1.5 flex-1 rounded-full ${step >= 1 ? "bg-[hsl(270,80%,55%)]" : "bg-muted"}`} />
          <div className={`h-1.5 flex-1 rounded-full ${step >= 2 ? "bg-[hsl(270,80%,55%)]" : "bg-muted"}`} />
        </div>

        {step === 1 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-black tracking-tight">Who are you?</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Select the option that best describes your situation.
              </p>
            </div>

            <div className="grid gap-3">
              {personaOptions.map((p) => {
                const active = selectedPersona === p.id;
                return (
                  <button
                    key={p.id}
                    onClick={() => setSelectedPersona(p.id)}
                    className={`flex items-center gap-4 rounded-lg border p-4 text-left transition-all ${
                      active
                        ? "border-primary bg-primary/10 shadow-md shadow-primary/10"
                        : "border-border hover:border-primary/40 hover:bg-muted/50"
                    }`}
                  >
                    <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-lg ${active ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                      <p.icon className="h-5 w-5" />
                    </div>
                    <div>
                      <p className="font-semibold">{p.label}</p>
                      <p className="text-xs text-muted-foreground">{p.description}</p>
                    </div>
                  </button>
                );
              })}
            </div>

            <button
              disabled={!selectedPersona}
              onClick={() => setStep(2)}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg bg-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-white transition-all hover:bg-[hsl(270,80%,60%)] disabled:opacity-40 disabled:cursor-not-allowed"
            >
              Continue
              <ArrowRight className="h-4 w-4" />
            </button>
          </div>
        )}

        {step === 2 && (
          <div className="space-y-6">
            <div>
              <h2 className="text-2xl font-black tracking-tight">What are your constraints?</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Check any that apply — we'll filter out roles that don't fit.
              </p>
            </div>

            <div className="grid gap-3">
              {barrierOptions.map((b) => (
                <label
                  key={b.id}
                  className={`flex cursor-pointer items-center gap-4 rounded-lg border p-4 transition-all ${
                    selectedBarriers.includes(b.id)
                      ? "border-primary bg-primary/10"
                      : "border-border hover:border-primary/40 hover:bg-muted/50"
                  }`}
                >
                  <Checkbox
                    checked={selectedBarriers.includes(b.id)}
                    onCheckedChange={() => toggleBarrier(b.id)}
                  />
                  <div>
                    <p className="font-semibold">{b.label}</p>
                    <p className="text-xs text-muted-foreground">{b.description}</p>
                  </div>
                </label>
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setStep(1)}
                className="inline-flex items-center gap-2 rounded-lg border border-border px-4 py-3 text-sm font-semibold transition-all hover:bg-muted/50"
              >
                <ArrowLeft className="h-4 w-4" />
                Back
              </button>
              <button
                onClick={handleComplete}
                className="inline-flex flex-1 items-center justify-center gap-2 rounded-lg bg-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-white transition-all hover:bg-[hsl(270,80%,60%)]"
              >
                View My Dashboard
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
};

export default OnboardingModal;

import { useRef, useEffect } from "react";
import { Link, useLocation } from "react-router-dom";
import { motion, useInView } from "framer-motion";
import Footer from "@/components/Footer";
import { ArrowRight, BarChart3, Users, Briefcase, Sparkles, TrendingUp, Shield, ChevronDown } from "lucide-react";
import heroNeetYouth from "@/assets/hero-neet-youth.jpg";
import heroRecruiter from "@/assets/hero-recruiter.jpg";
import heroUnemployed from "@/assets/hero-unemployed.jpg";

const stats = [
  { label: "Active Postings", value: "1,247", accent: true },
  { label: "Skills Coverage", value: "94.2%", accent: true },
  { label: "Retention Rate", value: "88.5%", accent: false },
  { label: "Active Gaps", value: "12 Critical", accent: true },
];

interface PersonaSectionProps {
  badge: string;
  title: string;
  titleAccent: string;
  description: string;
  image: string;
  ctaPrimary: string;
  ctaSecondary: string;
  features: { icon: React.ElementType; text: string }[];
  reverse?: boolean;
}

const PersonaSection = ({
  badge,
  title,
  titleAccent,
  description,
  image,
  ctaPrimary,
  ctaSecondary,
  features,
  reverse,
}: PersonaSectionProps) => {
  const ref = useRef(null);
  const isInView = useInView(ref, { once: true, margin: "-100px" });

  return (
    <section ref={ref} className="relative min-h-[100svh] overflow-hidden">
      {/* Background image */}
      <div className="absolute inset-0">
        <img src={image} alt="" className="h-full w-full object-cover" />
        <div className="absolute inset-0 bg-gradient-to-b from-[hsl(270,40%,8%)/0.95] via-[hsl(270,40%,8%)/0.80] to-[hsl(270,40%,8%)/0.60] md:bg-gradient-to-r md:from-[hsl(270,40%,8%)/0.92] md:via-[hsl(270,40%,8%)/0.75] md:to-[hsl(270,40%,8%)/0.4]" />
      </div>

      <div className={`relative z-10 mx-auto flex min-h-[100svh] max-w-7xl items-end px-4 pb-12 pt-20 sm:items-center sm:px-6 sm:py-24 lg:px-8 ${reverse ? "md:flex-row-reverse" : ""}`}>
        <motion.div
          initial={{ opacity: 0, y: 60 }}
          animate={isInView ? { opacity: 1, y: 0 } : {}}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="max-w-2xl"
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-[hsl(270,80%,60%)]/20 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-[hsl(270,80%,70%)] sm:px-4 sm:py-1.5 sm:text-xs">
            <Sparkles className="h-3 w-3" />
            {badge}
          </span>

          <h2 className="mt-4 text-3xl font-black leading-[1.05] tracking-tight text-foreground drop-shadow-[0_4px_24px_hsl(270,40%,8%)] sm:mt-6 sm:text-5xl md:text-7xl">
            {title}
            <br />
            <span className="italic text-[hsl(270,80%,65%)]">
              {titleAccent}
            </span>
          </h2>

          <p className="mt-4 max-w-lg text-sm leading-relaxed text-[hsl(270,10%,65%)] sm:mt-6 sm:text-lg">
            {description}
          </p>

          <div className="mt-6 flex flex-col gap-3 sm:mt-8 sm:flex-row sm:gap-4">
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center gap-2 rounded-full bg-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-foreground shadow-lg shadow-[hsl(270,80%,55%)]/25 transition-all hover:bg-[hsl(270,80%,60%)] hover:shadow-xl hover:shadow-[hsl(270,80%,55%)]/30 sm:px-7 sm:py-3.5"
            >
              {ctaPrimary}
              <ArrowRight className="h-4 w-4" />
            </Link>
            <button className="inline-flex items-center justify-center gap-2 rounded-full border border-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-foreground transition-all hover:bg-[hsl(270,80%,55%)]/10 sm:px-7 sm:py-3.5">
              {ctaSecondary}
            </button>
          </div>

          <div className="mt-6 flex flex-wrap gap-4 sm:mt-10 sm:gap-6">
            {features.map((f, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: 0.3 + i * 0.1 }}
                className="flex items-center gap-2 text-xs text-[hsl(270,10%,55%)] sm:text-sm"
              >
                <f.icon className="h-4 w-4 text-[hsl(270,80%,65%)]" />
                <span className="text-foreground">{f.text}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};

const Home = () => {
  const location = useLocation();

  useEffect(() => {
    if (location.hash) {
      const el = document.querySelector(location.hash);
      if (el) {
        setTimeout(() => el.scrollIntoView({ behavior: "smooth" }), 100);
      }
    }
  }, [location.hash]);

  return (
    <div className="min-h-screen bg-[hsl(270,40%,6%)]">
      {/* Fixed nav */}
      <nav className="fixed top-0 z-50 w-full border-b border-[hsl(270,20%,15%)] bg-[hsl(270,40%,6%)]/80 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3 sm:px-6 sm:py-4 lg:px-8">
          <div className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[hsl(270,80%,65%)] sm:h-6 sm:w-6" />
            <span className="text-base font-black tracking-tight text-foreground sm:text-lg">PULSE</span>
          </div>
          <div className="hidden items-center gap-8 md:flex">
            <a href="#neet-youth" className="text-base font-medium text-[hsl(270,10%,55%)] transition-colors hover:text-foreground">Youth</a>
            <a href="#recruiter" className="text-base font-medium text-[hsl(270,10%,55%)] transition-colors hover:text-foreground">Recruiters</a>
            <a href="#unemployed" className="text-base font-medium text-[hsl(270,10%,55%)] transition-colors hover:text-foreground">Career Restart</a>
          </div>
          <Link
            to="/dashboard"
            className="rounded-full bg-[hsl(270,80%,55%)] px-4 py-1.5 text-xs font-bold text-foreground transition-all hover:bg-[hsl(270,80%,60%)] sm:px-5 sm:py-2 sm:text-sm"
          >
            Get Started
          </Link>
        </div>
      </nav>

      {/* Hero landing */}
      <section className="relative flex min-h-[100svh] flex-col items-center justify-center overflow-hidden px-4 pt-16 sm:px-6 sm:pt-20">
        {/* Gradient orb bg */}
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-1/3 h-[300px] w-[300px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[hsl(270,80%,40%)]/15 blur-[80px] sm:h-[600px] sm:w-[600px] sm:blur-[120px]" />
          <div className="absolute right-1/4 top-2/3 h-[200px] w-[200px] rounded-full bg-[hsl(200,90%,50%)]/10 blur-[60px] sm:h-[400px] sm:w-[400px] sm:blur-[100px]" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: "easeOut" }}
          className="relative z-10 max-w-4xl text-center"
        >
          <span className="inline-flex items-center gap-2 rounded-full bg-[hsl(270,80%,60%)]/15 px-3 py-1 text-[10px] font-bold uppercase tracking-widest text-[hsl(270,80%,70%)] sm:px-4 sm:py-1.5 sm:text-xs">
            <Sparkles className="h-3 w-3" />
            Next-Gen Workforce Intelligence
          </span>

          <h1 className="mt-6 text-4xl font-black leading-[1.05] tracking-tight text-foreground sm:mt-8 sm:text-6xl md:text-8xl">
            Workforce
            <br />
            <span className="italic text-[hsl(270,80%,65%)]">
              Pulse.
            </span>
          </h1>

          <p className="mx-auto mt-4 max-w-xl text-sm leading-relaxed text-[hsl(270,10%,55%)] sm:mt-6 sm:text-lg">
            Sophisticated, data-driven insights into your global workforce performance and skills evolution. Built for the modern enterprise.
          </p>

          <div className="mt-8 flex flex-wrap items-center justify-center gap-4 sm:mt-10">
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-2 rounded-full bg-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-foreground shadow-lg shadow-[hsl(270,80%,55%)]/25 transition-all hover:bg-[hsl(270,80%,60%)] hover:shadow-xl sm:px-8 sm:py-4"
            >
              Launch Dashboard
              <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-6 z-10 sm:bottom-10"
        >
          <ChevronDown className="h-6 w-6 animate-bounce text-[hsl(270,10%,40%)]" />
        </motion.div>
      </section>

      {/* Stats bar */}
      <div className="border-y border-[hsl(270,20%,12%)] bg-[hsl(270,40%,6%)]">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-px md:grid-cols-4">
          {stats.map((stat) => (
            <div key={stat.label} className="px-4 py-5 text-center sm:px-6 sm:py-8 md:px-8">
              <p className="text-[9px] font-bold uppercase tracking-[0.15em] text-[hsl(270,10%,45%)] sm:text-[10px] sm:tracking-[0.2em]">
                {stat.label}
              </p>
              <p className={`mt-1 text-xl font-black tracking-tight sm:mt-2 sm:text-3xl ${stat.accent ? "text-[hsl(270,80%,65%)]" : "text-foreground"}`}>
                {stat.value}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Persona sections */}
      <div id="neet-youth">
        <PersonaSection
          badge="New Opportunities"
          title="Opportunities for"
          titleAccent="NEET Youth."
          description="Unlock your potential with earn-while-you-learn roles and apprenticeships tailored for your future. No experience needed — just ambition."
          image={heroNeetYouth}
          ctaPrimary="Explore Roles"
          ctaSecondary="Learn More"
          features={[
            { icon: Briefcase, text: "Paid Apprenticeships" },
            { icon: Shield, text: "Mentorship Programs" },
            { icon: TrendingUp, text: "Career Pathways" },
          ]}
        />
      </div>

      <div id="recruiter">
        <PersonaSection
          badge="For Employers"
          title="Hire Smarter with"
          titleAccent="Workforce Pulse."
          description="Access real-time talent supply data, skill gap analytics, and pipeline insights to fill critical roles faster across Montgomery."
          image={heroRecruiter}
          ctaPrimary="View Talent Pool"
          ctaSecondary="Request Demo"
          features={[
            { icon: Users, text: "124,800 Active Talent" },
            { icon: BarChart3, text: "Real-time Analytics" },
            { icon: TrendingUp, text: "+12% YoY Growth" },
          ]}
          reverse
        />
      </div>

      <div id="unemployed">
        <PersonaSection
          badge="Career Restart"
          title="Your Next Chapter"
          titleAccent="Starts Here."
          description="Purpose-built pathways for career returners. Wrap-around support including transit, coaching, and flexible schedules — because everyone deserves a second chance."
          image={heroUnemployed}
          ctaPrimary="Find Your Path"
          ctaSecondary="Support Options"
          features={[
            { icon: Shield, text: "Transit Support" },
            { icon: Users, text: "Career Coaching" },
            { icon: Briefcase, text: "No Experience Required" },
          ]}
        />
      </div>

      {/* Footer CTA */}
      <section className="relative overflow-hidden border-t border-[hsl(270,20%,12%)] py-16 sm:py-32">
        <div className="pointer-events-none absolute inset-0">
          <div className="absolute left-1/2 top-1/2 h-[300px] w-[300px] -translate-x-1/2 -translate-y-1/2 rounded-full bg-[hsl(270,80%,40%)]/10 blur-[80px] sm:h-[500px] sm:w-[500px] sm:blur-[120px]" />
        </div>
        <div className="relative z-10 mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="text-2xl font-black tracking-tight text-foreground sm:text-4xl md:text-5xl">
            Ready to transform your{" "}
            <span className="text-[hsl(270,80%,65%)]">
              workforce strategy
            </span>
            ?
          </h2>
          <p className="mx-auto mt-3 max-w-lg text-sm text-[hsl(270,10%,55%)] sm:mt-4 sm:text-lg">
            Join Montgomery's leading organizations using Workforce Pulse to drive smarter hiring and training decisions.
          </p>
          <Link
            to="/dashboard"
            className="mt-6 inline-flex items-center gap-2 rounded-full bg-[hsl(270,80%,55%)] px-6 py-3 text-sm font-bold text-foreground shadow-lg shadow-[hsl(270,80%,55%)]/25 transition-all hover:bg-[hsl(270,80%,60%)] hover:shadow-xl sm:mt-8 sm:px-8 sm:py-4"
          >
            Launch Dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>
        </div>
      </section>

      <Footer />
    </div>
  );
};

export default Home;

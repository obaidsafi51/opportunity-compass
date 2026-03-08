import { Link } from "react-router-dom";
import { BarChart3 } from "lucide-react";

const marqueeText = "STEP INTO THE PULSE ✦ STEP INTO THE PULSE ✦ STEP INTO THE PULSE ✦ STEP INTO THE PULSE ✦ STEP INTO THE PULSE ✦ STEP INTO THE PULSE ✦ ";


const navLinks = [
  { label: "Youth", to: "/#neet-youth" },
  { label: "Recruiters", to: "/#recruiter" },
  { label: "Career Restart", to: "/#unemployed" },
];

const Footer = () => (
  <footer className="border-t border-[hsl(270,20%,12%)] bg-[hsl(270,40%,6%)]">
    {/* Marquee ticker */}
    <div className="overflow-hidden border-b border-[hsl(270,20%,12%)] py-3">
      <div className="animate-marquee flex whitespace-nowrap">
        <span className="mx-4 text-sm font-bold uppercase tracking-[0.15em] text-[hsl(270,10%,30%)]">
          {marqueeText}
        </span>
        <span className="mx-4 text-sm font-bold uppercase tracking-[0.15em] text-[hsl(270,10%,30%)]">
          {marqueeText}
        </span>
      </div>
    </div>

    {/* Main footer content */}
    <div className="mx-auto max-w-7xl px-6 py-16 lg:px-8">
      <div className="grid grid-cols-1 gap-12">
        {/* Large nav links */}
        <div className="flex flex-col gap-2">
          {navLinks.map((link) => (
            <Link
              key={link.label}
              to={link.to}
              className="text-5xl font-black uppercase tracking-tight text-foreground transition-colors hover:text-[hsl(270,80%,65%)] md:text-6xl lg:text-7xl"
            >
              {link.label}
            </Link>
          ))}
        </div>
      </div>
    </div>

    {/* Bottom bar */}
    <div className="border-t border-[hsl(270,20%,12%)]">
      <div className="mx-auto grid max-w-7xl grid-cols-1 gap-4 px-6 py-6 md:grid-cols-3 lg:px-8">
        {/* Logo + year */}
        <div className="flex items-end gap-4">
          <Link to="/" className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5 text-[hsl(270,80%,65%)]" />
            <span className="text-sm font-black tracking-tight text-foreground">PULSE</span>
          </Link>
          <span className="text-[10px] font-medium uppercase tracking-wider text-[hsl(270,10%,30%)]">
            2026
          </span>
        </div>

        {/* Location */}
        <div className="text-xs leading-relaxed text-[hsl(270,10%,40%)]">
          <p className="font-semibold uppercase tracking-wider text-[hsl(270,10%,50%)]">Montgomery, AL</p>
          <p>Workforce Intelligence Division</p>
        </div>

        {/* Legal + contact */}
        <div className="flex flex-col items-start gap-1 md:items-end">
          <a href="mailto:info@workforcepulse.gov" className="text-xs text-[hsl(270,10%,40%)] transition-colors hover:text-foreground">
            info@workforcepulse.gov
          </a>
          <div className="flex gap-3 text-[10px] uppercase tracking-wider text-[hsl(270,10%,30%)]">
            <a href="#" className="transition-colors hover:text-foreground">Privacy Policy</a>
            <span>/</span>
            <a href="#" className="transition-colors hover:text-foreground">Terms of Use</a>
          </div>
        </div>
      </div>
    </div>
  </footer>
);

export default Footer;

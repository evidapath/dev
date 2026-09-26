import { Link } from "@tanstack/react-router";
import { EvidaPathLogo } from "./brand/EvidaPathLogo";
import { ShieldCheck, ArrowRight } from "lucide-react";
import { Button } from "./ui/button";

export function Footer() {
  return (
    <footer className="border-t border-border bg-card text-foreground">
      {/* Top Banner: single trust statement */}
      <div className="bg-secondary/50 border-b border-border/60 py-6 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-center md:text-left">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center shrink-0">
              <ShieldCheck className="w-5 h-5 text-primary" />
            </div>
            <div>
              <p className="font-display font-semibold text-sm text-foreground">
                Evidence before opinion. Transparent education intelligence.
              </p>
              <p className="text-xs text-muted-foreground mt-0.5">
                EvidaPath is being built to distinguish verified facts, institutional information,
                estimates, and analytical interpretation.
              </p>
            </div>
          </div>
          <Link to="/find-my-path" className="shrink-0">
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm flex items-center gap-1.5">
              Find My Path <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 lg:py-16">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 lg:gap-12">
          {/* Brand Col */}
          <div className="lg:col-span-1 space-y-4">
            <EvidaPathLogo height={36} />
            <p className="text-sm text-muted-foreground leading-relaxed max-w-sm">
              Know where you stand. See where you can go. Pathways, not wishful thinking.
            </p>
            <p className="text-xs text-muted-foreground italic font-serif">
              "Better decisions. Brighter futures."
            </p>
          </div>

          {/* Explore */}
          <div>
            <h4 className="font-display font-semibold text-sm text-foreground mb-3">Explore</h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link
                  to="/find-my-path"
                  className="hover:text-primary transition-colors font-medium text-foreground"
                >
                  Find My Path
                </Link>
              </li>
              <li>
                <Link to="/universities" className="hover:text-primary transition-colors">
                  Universities
                </Link>
              </li>
              <li>
                <Link to="/scholarships" className="hover:text-primary transition-colors">
                  Scholarships
                </Link>
              </li>
              <li>
                <Link to="/intelligence" className="hover:text-primary transition-colors">
                  Intelligence
                </Link>
              </li>
            </ul>
          </div>

          {/* How it works */}
          <div>
            <h4 className="font-display font-semibold text-sm text-foreground mb-3">
              How it works
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                <Link to="/intelligence" className="hover:text-primary transition-colors">
                  The EvidaPath Decision Model
                </Link>
              </li>
              <li>
                <Link to="/academic-readiness" className="hover:text-primary transition-colors">
                  Academic Readiness
                </Link>
              </li>
              <li>
                <Link to="/sign-in" className="hover:text-primary transition-colors">
                  Sign In
                </Link>
              </li>
            </ul>
          </div>

          {/* Trust */}
          <div>
            <h4 className="font-display font-semibold text-sm text-foreground mb-3">
              Trust & Standards
            </h4>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="text-xs text-muted-foreground">
                No outcome certainty claims. Never sponsored rankings. Independent analytical
                intelligence.
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Disclaimers */}
        <div className="mt-12 pt-8 border-t border-border flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-muted-foreground">
          <p>
            © {new Date().getFullYear()} EvidaPath Intelligence. All rights reserved. An emerging
            decision-intelligence platform whose live datasets are currently being built and
            verified.
          </p>
          <div className="flex flex-wrap items-center gap-6">
            <span className="hover:text-foreground cursor-pointer">Privacy & Data Security</span>
            <span className="hover:text-foreground cursor-pointer">Terms</span>
          </div>
        </div>
      </div>
    </footer>
  );
}

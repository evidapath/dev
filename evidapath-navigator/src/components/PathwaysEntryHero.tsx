import { useState } from "react";
import { Link } from "@tanstack/react-router";
import {
  ArrowRight,
  Compass,
  BarChart3,
  Search,
  GraduationCap,
  DollarSign,
  BookOpen,
  Layers,
  CheckCircle2,
} from "lucide-react";
import { Button } from "./ui/button";
import { UNIVERSITIES_DATA } from "../lib/mock-data";

export function PathwaysEntryHero() {
  const [activeTab, setActiveTab] = useState<"explore" | "analyze">("explore");
  const [selectedInterest, setSelectedInterest] = useState<string>("Computer Science");
  const [selectedTargetUniv, setSelectedTargetUniv] = useState<string>("uoft-canada");

  return (
    <div className="w-full max-w-5xl mx-auto mt-8">
      {/* Tab toggle */}
      <div className="flex border-b border-border bg-card rounded-t-2xl shadow-xs overflow-hidden">
        <button
          onClick={() => setActiveTab("explore")}
          className={`flex-1 py-4 px-6 text-left transition-all border-b-2 flex items-center gap-3 ${
            activeTab === "explore"
              ? "border-primary bg-background text-foreground font-semibold"
              : "border-transparent bg-secondary/40 text-muted-foreground hover:bg-secondary/60"
          }`}
        >
          <div
            className={`w-8 h-8 rounded-lg flex items-center justify-center ${activeTab === "explore" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}
          >
            <Compass className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-display font-bold">I’m exploring my options</div>
            <div className="text-xs text-muted-foreground font-normal">
              Discover universities matching my profile and budget
            </div>
          </div>
        </button>

        <button
          onClick={() => setActiveTab("analyze")}
          className={`flex-1 py-4 px-6 text-left transition-all border-b-2 flex items-center gap-3 ${
            activeTab === "analyze"
              ? "border-primary bg-background text-foreground font-semibold"
              : "border-transparent bg-secondary/40 text-muted-foreground hover:bg-secondary/60"
          }`}
        >
          <div
            className={`w-8 h-8 rounded-lg flex items-center justify-center ${activeTab === "analyze" ? "bg-primary/10 text-primary" : "bg-muted text-muted-foreground"}`}
          >
            <BarChart3 className="w-4 h-4" />
          </div>
          <div>
            <div className="text-sm font-display font-bold">
              I already have a university in mind
            </div>
            <div className="text-xs text-muted-foreground font-normal">
              Analyze evidence, identify gaps & controllable levers
            </div>
          </div>
        </button>
      </div>

      {/* Tab content panel */}
      <div className="bg-card border-x border-b border-border rounded-b-2xl p-6 sm:p-8 shadow-sm">
        {activeTab === "explore" ? (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Academic Focus
                </label>
                <select
                  value={selectedInterest}
                  onChange={(e) => setSelectedInterest(e.target.value)}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  <option value="Computer Science">Computer Science & AI</option>
                  <option value="Economics">Economics, Finance & Management</option>
                  <option value="Engineering">Mechanical & Aerospace Engineering</option>
                  <option value="Life Sciences">Life Sciences & Pre-Med</option>
                  <option value="Law">Law & Global Governance</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Curriculum / Predicted Grade
                </label>
                <select className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary">
                  <option>IB Diploma (38-42 points)</option>
                  <option>A-Levels (A*AA to AAA)</option>
                  <option>A-Levels (AAB to ABB)</option>
                  <option>US High School / AP (GPA 3.8+)</option>
                  <option>CBSE / National Board (92%+)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Target Annual Budget Range
                </label>
                <select className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary">
                  <option>Under $25,000 / yr (European Public)</option>
                  <option>$25,000 - $45,000 / yr (Value Global)</option>
                  <option>$45,000 - $65,000 / yr (UK / Canada Tier-1)</option>
                  <option>Flexible / Seeking Merit Aid</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <CheckCircle2 className="w-4 h-4 text-primary" />
                <span>Answer a few questions and see realistic pathways</span>
              </div>

              <Link to="/find-my-path">
                <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-5 h-10 rounded-lg flex items-center gap-2">
                  <span>Find My Path</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              <div className="sm:col-span-2">
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Select Target University to Evaluate
                </label>
                <select
                  value={selectedTargetUniv}
                  onChange={(e) => setSelectedTargetUniv(e.target.value)}
                  className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary"
                >
                  {UNIVERSITIES_DATA.map((u) => (
                    <option key={u.id} value={u.id}>
                      {u.flag} {u.name} ({u.city}, {u.country})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold uppercase text-muted-foreground mb-1.5">
                  Your Current Grade Standing
                </label>
                <select className="w-full h-10 px-3 rounded-lg border border-input bg-background text-sm text-foreground focus:outline-hidden focus:ring-2 focus:ring-primary">
                  <option>At or slightly above posted threshold</option>
                  <option>One grade band below minimum</option>
                  <option>Prerequisites pending / In progress</option>
                </select>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-4 pt-4 border-t border-border">
              <div className="flex items-center gap-2 text-xs text-muted-foreground">
                <span className="inline-block w-2 h-2 rounded-full bg-bronze" />
                <span>See where you stand and which gaps you can still change</span>
              </div>

              <Link to="/find-my-path">
                <Button className="w-full sm:w-auto bg-primary hover:bg-primary/90 text-primary-foreground font-semibold px-5 h-10 rounded-lg flex items-center gap-2">
                  <span>Find My Path</span>
                  <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

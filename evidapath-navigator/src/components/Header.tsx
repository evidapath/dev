import { Link, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { EvidaPathLogo } from "./brand/EvidaPathLogo";
import { Button } from "./ui/button";
import { useAuth } from "./AuthContext";
import {
  Menu,
  X,
  ArrowRight,
  Compass,
  GraduationCap,
  BookOpen,
  ShieldCheck,
  LayoutDashboard,
  ClipboardList,
  Vault,
  PiggyBank,
  Settings,
  LogIn,
  LogOut,
  ChevronDown,
  UserCircle,
} from "lucide-react";

export function Header() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [exploreOpen, setExploreOpen] = useState(false);
  const [memberOpen, setMemberOpen] = useState(false);
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  // PUBLIC nav — simple, understandable in under 5 seconds.
  const exploreItems = [
    { label: "Universities", href: "/universities", icon: GraduationCap },
    { label: "Scholarships", href: "/scholarships", icon: BookOpen },
    { label: "Intelligence", href: "/intelligence", icon: ShieldCheck },
  ];

  // LOGGED-IN nav — product workflows grouped under clear categories.
  const memberItems = [
    { label: "My Path", href: "/dashboard", icon: LayoutDashboard },
    { label: "Explore", href: "/universities", icon: Compass },
    { label: "Applications", href: "/applications", icon: ClipboardList },
    { label: "Offers", href: "/offer-vault", icon: Vault },
    { label: "Funding", href: "/fund", icon: PiggyBank },
    { label: "Account", href: "/account", icon: Settings },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border/80 bg-background/95 backdrop-blur-md transition-all">
      <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center group transition-opacity hover:opacity-90">
          <EvidaPathLogo height={34} />
        </Link>

        {/* Desktop Nav */}
        <nav className="hidden lg:flex items-center gap-1 xl:gap-2">
          {user ? (
            // Logged-in: grouped product nav
            <>
              {memberItems.slice(0, 5).map((item) => (
                <Link
                  key={item.href}
                  to={item.href}
                  activeProps={{
                    className: "text-foreground font-semibold bg-secondary/80",
                  }}
                  inactiveProps={{
                    className: "text-muted-foreground hover:text-foreground hover:bg-secondary/40",
                  }}
                  className="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
                >
                  {item.label}
                </Link>
              ))}
            </>
          ) : (
            // Logged-out: simple public nav
            <>
              <Link
                to="/universities"
                activeProps={{ className: "text-foreground font-semibold bg-secondary/80" }}
                inactiveProps={{
                  className: "text-muted-foreground hover:text-foreground hover:bg-secondary/40",
                }}
                className="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                Explore
              </Link>
              <Link
                to="/intelligence"
                activeProps={{ className: "text-foreground font-semibold bg-secondary/80" }}
                inactiveProps={{
                  className: "text-muted-foreground hover:text-foreground hover:bg-secondary/40",
                }}
                className="px-3 py-1.5 rounded-md text-sm font-medium transition-colors"
              >
                How It Works
              </Link>
            </>
          )}
        </nav>

        {/* Right Actions */}
        <div className="hidden sm:flex items-center gap-3">
          {user ? (
            <div className="flex items-center gap-3">
              <Link
                to="/dashboard"
                className="flex items-center gap-1.5 text-sm font-medium text-foreground hover:text-primary transition-colors px-2 py-1"
              >
                <UserCircle className="w-4 h-4 text-primary" />
                <span className="max-w-[140px] truncate">{user.email ?? "My EvidaPath"}</span>
              </Link>
              <Link
                to="/account"
                className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-1"
                title="Account & data"
              >
                <Settings className="w-4 h-4" />
              </Link>
              <button
                onClick={async () => {
                  await signOut();
                  navigate({ to: "/" });
                }}
                className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-1"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden md:inline">Sign Out</span>
              </button>
            </div>
          ) : (
            <Link
              to="/sign-in"
              className="flex items-center gap-1.5 text-sm font-medium text-muted-foreground hover:text-foreground transition-colors px-2 py-1"
            >
              <LogIn className="w-4 h-4" />
              <span>Sign In</span>
            </Link>
          )}
          <Link to="/find-my-path">
            <Button className="bg-primary hover:bg-primary/90 text-primary-foreground font-semibold text-sm px-4 h-9.5 rounded-lg shadow-sm transition-all flex items-center gap-1.5">
              <span>Find My Path</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </Button>
          </Link>
        </div>

        {/* Mobile menu trigger */}
        <div className="flex sm:hidden">
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="p-2 rounded-md text-foreground hover:bg-secondary transition-colors"
            aria-label="Toggle navigation menu"
          >
            {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden border-b border-border bg-card px-4 pt-3 pb-5 shadow-lg animate-in fade-in-20">
          <div className="flex flex-col space-y-1">
            {(user ? memberItems : exploreItems).map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  to={item.href}
                  onClick={() => setMobileMenuOpen(false)}
                  className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium text-foreground hover:bg-secondary transition-colors"
                >
                  <Icon className="w-4 h-4 text-muted-foreground" />
                  <span>{item.label}</span>
                </Link>
              );
            })}
            {!user && (
              <Link
                to="/intelligence"
                onClick={() => setMobileMenuOpen(false)}
                className="flex items-center gap-2.5 px-3 py-2 rounded-md text-sm font-medium text-foreground hover:bg-secondary transition-colors"
              >
                <ShieldCheck className="w-4 h-4 text-muted-foreground" />
                <span>How It Works</span>
              </Link>
            )}
          </div>

          <div className="mt-4 pt-4 border-t border-border flex flex-col gap-2">
            <Link to="/find-my-path" onClick={() => setMobileMenuOpen(false)} className="w-full">
              <Button className="w-full bg-primary hover:bg-primary/90 text-primary-foreground font-semibold h-10">
                Find My Path
              </Button>
            </Link>
            {user ? (
              <>
                <Link
                  to="/account"
                  onClick={() => setMobileMenuOpen(false)}
                  className="w-full flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground font-medium"
                >
                  <Settings className="w-4 h-4" />
                  Account &amp; Data
                </Link>
                <button
                  onClick={async () => {
                    setMobileMenuOpen(false);
                    await signOut();
                    navigate({ to: "/" });
                  }}
                  className="w-full flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground font-medium"
                >
                  <LogOut className="w-4 h-4" />
                  Sign Out
                </button>
              </>
            ) : (
              <Link
                to="/sign-in"
                onClick={() => setMobileMenuOpen(false)}
                className="w-full flex items-center justify-center gap-2 py-2 text-sm text-muted-foreground font-medium"
              >
                <LogIn className="w-4 h-4" />
                Sign In
              </Link>
            )}
          </div>
        </div>
      )}
    </header>
  );
}

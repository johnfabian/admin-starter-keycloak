import {
  ArrowRight,
  BarChart3,
  Bot,
  Database,
  LayoutDashboard,
  Mail,
  MessageSquare,
  Palette,
  Shield,
  Sparkles,
  Star,
  Users,
  Zap,
  type LucideIcon,
} from "lucide-react";
import { Link } from "react-router";

import { ThemeToggle } from "~/components/layout/theme-toggle";
import { Button } from "~/components/ui/button";
import { PublicLayout } from "~/layouts/public-layout";
import { appInfo, appRoutes } from "~/lib/app-settings.shared";
import { isAppPath } from "~/lib/string-helper.shared";
import type { CurrentUser } from "~/models/current-user";

interface Feature {
  icon: LucideIcon;
  title: string;
  description: string;
}

const coreFeatures: Feature[] = [
  {
    icon: Shield,
    title: "Secure Authentication",
    description: "Keycloak-backed sessions and role-based route protection.",
  },
  {
    icon: Palette,
    title: "Beautiful Themes",
    description: "Accent themes with direct light and dark mode switching.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description: "Built on React Router 7, React 19, Vite, and Tailwind CSS.",
  },
  {
    icon: Users,
    title: "User Management",
    description: "A clean foundation for users, groups, permissions, and apps.",
  },
];

const aiFeatures: Feature[] = [
  {
    icon: Bot,
    title: "AI Agents",
    description: "Plan future workflows around autonomous admin assistance.",
  },
  {
    icon: MessageSquare,
    title: "AI Chatbots",
    description: "Add conversational help for support, onboarding, and operations.",
  },
  {
    icon: BarChart3,
    title: "Smart Analytics",
    description: "Surface trends, anomalies, and admin activity insights.",
  },
  {
    icon: Database,
    title: "Knowledge Base",
    description: "Keep internal data ready for retrieval and automation.",
  },
];

const productLinks = [
  { label: "Features", href: "#features" },
  { label: "Security", href: "#security" },
  { label: "AI", href: "#ai" },
];

const companyLinks = [
  { label: "Dashboard", href: appRoutes.usersDashboard },
  { label: "Apps", href: appRoutes.appsDashboard },
  { label: "Account", href: appRoutes.authAccount },
];

const legalLinks = [
  { label: "Privacy", href: "#privacy" },
  { label: "Terms", href: "#terms" },
  { label: "Contact", href: "mailto:hello@example.com" },
];

const socialLinks = [
  { icon: Star, href: "https://github.com", label: "GitHub" },
  { icon: MessageSquare, href: "https://twitter.com", label: "Twitter" },
  { icon: Users, href: "https://linkedin.com", label: "LinkedIn" },
  { icon: Mail, href: "mailto:hello@example.com", label: "Email" },
];

export function SplashPage({ user }: { user: CurrentUser | null }) {
  return (
    <PublicLayout user={user} background="white" showHeader={false}>
      <div className="flex min-h-screen flex-col bg-background text-foreground">
        <SplashHeader />
        <main className="flex-1">
          <SplashHero user={user} />
          <SplashFeatures />
        </main>
        <SplashFooter />
      </div>
    </PublicLayout>
  );
}

function SplashHeader() {
  return (
    <header className="w-full border-b bg-background">
      <div className="flex h-16 items-center justify-between px-6 md:px-10 lg:px-16">
        <Link
          to={appRoutes.home}
          className="flex items-center gap-2.5 font-semibold text-foreground transition-colors hover:text-primary"
        >
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <LayoutDashboard className="h-5 w-5" aria-hidden="true" />
          </span>
          <span className="text-lg font-bold tracking-tight">{appInfo.name}</span>
        </Link>
        <nav className="flex items-center gap-2 sm:gap-4" aria-label="Header navigation">
          <ThemeToggle />
        </nav>
      </div>
    </header>
  );
}

function SplashHero({ user }: { user: CurrentUser | null }) {
  return (
    <section className="relative w-full overflow-hidden" aria-labelledby="hero-heading">
      <div
        className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_right,var(--primary)_0%,transparent_35%,transparent_100%)] opacity-5"
        aria-hidden="true"
      />

      <div className="relative z-10 grid min-h-[calc(100vh-4rem)] items-center gap-8 px-6 py-12 md:grid-cols-2 md:px-10 md:py-16 lg:gap-16 lg:px-16">
        <div className="flex flex-col justify-center">
          <div className="mb-6 inline-flex w-fit items-center gap-2 rounded-full border bg-background/80 px-3 py-1 text-sm backdrop-blur">
            <Sparkles className="h-3.5 w-3.5 text-primary" aria-hidden="true" />
            <span className="text-muted-foreground">Modern Admin Dashboard</span>
          </div>

          <h1
            id="hero-heading"
            className="text-4xl font-bold tracking-tight text-foreground sm:text-5xl lg:text-6xl"
          >
            Build better{" "}
            <span className="bg-[linear-gradient(to_right,var(--primary),color-mix(in_oklch,var(--primary)_60%,transparent))] bg-clip-text text-transparent">
              admin panels
            </span>{" "}
            faster
          </h1>

          <p className="mt-6 max-w-lg text-lg text-muted-foreground">
            A production-ready starter with Keycloak authentication, theming, and the shell you need
            to ship your admin dashboard quickly.
          </p>

          <div className="mt-8 flex flex-wrap items-center gap-4">
            <Button asChild className="h-10 gap-2 px-6">
              <a href={user ? appRoutes.usersDashboard : appRoutes.authRegister}>
                Get Started
                <ArrowRight className="h-4 w-4" aria-hidden="true" />
              </a>
            </Button>
            <Button variant="outline" asChild className="h-10 px-6">
              <a href={user ? appRoutes.usersDashboard : appRoutes.authLoginWithPrompt}>
                {user ? "Open Dashboard" : "Sign In"}
              </a>
            </Button>
          </div>

          <div className="mt-12 flex gap-8 border-t pt-8">
            <HeroStat value="100%" label="Type Safe" />
            <HeroStat value="7" label="Color Themes" />
            <HeroStat value="Dark" label="Mode Ready" />
          </div>
        </div>

        <div className="relative hidden md:block">
          <div
            className="absolute -inset-4 rounded-2xl bg-[linear-gradient(to_right,var(--primary),transparent)] opacity-20 blur-2xl"
            aria-hidden="true"
          />
          <div className="relative overflow-hidden rounded-xl border bg-background/50 shadow-2xl backdrop-blur">
            <img
              src="/images/splashpage/dashboard-preview.png"
              alt="Dashboard analytics preview showing charts and data visualization"
              className="w-full object-cover"
            />
            <div
              className="absolute inset-0 bg-[linear-gradient(to_right,var(--background),transparent,transparent)] opacity-80"
              aria-hidden="true"
            />
          </div>
        </div>
      </div>
    </section>
  );
}

function HeroStat({ value, label }: { value: string; label: string }) {
  return (
    <div>
      <div className="text-2xl font-bold text-foreground">{value}</div>
      <div className="text-sm text-muted-foreground">{label}</div>
    </div>
  );
}

function SplashFeatures() {
  return (
    <>
      <section
        id="features"
        aria-labelledby="features-heading"
        className="w-full border-t bg-muted/30 py-16 md:py-24"
      >
        <div className="px-6 md:px-10 lg:px-16">
          <SectionHeader
            icon={Sparkles}
            badge="Everything You Need"
            heading="Built for Modern Teams"
            description="A complete foundation for building secure, beautiful admin dashboards with enterprise-grade features out of the box."
            id="features-heading"
          />

          <FeatureRow
            image="/images/splashpage/code-environment.png"
            imageAlt="Clean code on a modern development environment"
            heading="Secure by Default"
            description="Enterprise-grade authentication with Keycloak, role-based access control, and server-checked routes. Built with security practices from the ground up."
            features={coreFeatures.slice(0, 2)}
          />

          <FeatureRow
            image="/images/splashpage/abstract-gradient.png"
            imageAlt="Abstract colorful gradient representing beautiful themes"
            heading="Beautiful & Lightning Fast"
            description="Themeable UI with direct dark mode support, powered by React Router 7 and React 19. Optimized for a focused admin workflow."
            features={coreFeatures.slice(2, 4)}
            reverse
          />
        </div>
      </section>

      <section id="ai" aria-labelledby="ai-features-heading" className="w-full py-16 md:py-24">
        <div className="px-6 md:px-10 lg:px-16">
          <SectionHeader
            icon={Bot}
            badge="AI-Powered"
            heading="Supercharge with AI"
            description="Add intelligent capabilities to your admin panel with an AI-ready architecture. Build chatbots, deploy agents, and unlock smart automation."
            id="ai-features-heading"
          />

          <FeatureRow
            image="/images/splashpage/ai-chatbot.png"
            imageAlt="AI chatbot interface with conversation bubbles"
            heading="Conversational AI at Your Fingertips"
            description="Deploy intelligent chatbots for support, internal help desks, and user onboarding flows."
            features={aiFeatures.slice(0, 2)}
          />

          <FeatureRow
            image="/images/splashpage/data-analytics.png"
            imageAlt="Data analytics dashboard with charts and graphs"
            heading="Autonomous Agents That Work For You"
            description="Build AI agents that can analyze data, generate reports, and take actions on your behalf."
            features={aiFeatures.slice(2, 4)}
            reverse
          />
        </div>
      </section>
    </>
  );
}

function SectionHeader({
  icon: Icon,
  badge,
  heading,
  description,
  id,
}: {
  icon: LucideIcon;
  badge: string;
  heading: string;
  description: string;
  id: string;
}) {
  return (
    <div className="mb-16 text-center">
      <div className="mb-4 inline-flex items-center gap-2 rounded-full border bg-primary/5 px-4 py-1.5 text-sm font-medium text-primary">
        <Icon className="h-4 w-4" aria-hidden="true" />
        {badge}
      </div>
      <h2 id={id} className="text-3xl font-bold tracking-tight text-foreground md:text-4xl">
        {heading}
      </h2>
      <p className="mx-auto mt-4 max-w-2xl text-lg text-muted-foreground">{description}</p>
    </div>
  );
}

function FeatureRow({
  image,
  imageAlt,
  heading,
  description,
  features,
  reverse = false,
}: {
  image: string;
  imageAlt: string;
  heading: string;
  description: string;
  features: Feature[];
  reverse?: boolean;
}) {
  const imageContent = (
    <div className={reverse ? "relative order-1 lg:order-2" : "relative"}>
      <div
        className="absolute -inset-4 rounded-2xl bg-[linear-gradient(to_right,var(--primary),transparent)] opacity-20 blur-2xl"
        aria-hidden="true"
      />
      <div className="relative overflow-hidden rounded-xl border bg-background/50 shadow-2xl">
        <img src={image} alt={imageAlt} className="w-full object-cover" />
      </div>
    </div>
  );

  const textContent = (
    <div className={reverse ? "order-2 space-y-6 lg:order-1" : "space-y-6"}>
      <h3 className="text-2xl font-bold text-foreground">{heading}</h3>
      <p className="text-lg text-muted-foreground">{description}</p>
      <div className="grid gap-4 sm:grid-cols-2">
        {features.map((feature) => (
          <FeatureCardCompact key={feature.title} feature={feature} />
        ))}
      </div>
    </div>
  );

  return (
    <div className="mb-20 grid items-center gap-12 last:mb-0 lg:grid-cols-2">
      {reverse ? (
        <>
          {textContent}
          {imageContent}
        </>
      ) : (
        <>
          {imageContent}
          {textContent}
        </>
      )}
    </div>
  );
}

function FeatureCardCompact({ feature }: { feature: Feature }) {
  const Icon = feature.icon;

  return (
    <div className="flex gap-4 rounded-lg border bg-muted/50 p-4">
      <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-primary/10">
        <Icon className="h-5 w-5 text-primary" aria-hidden="true" />
      </div>
      <div>
        <h4 className="font-medium text-foreground">{feature.title}</h4>
        <p className="mt-1 text-xs text-muted-foreground">{feature.description}</p>
      </div>
    </div>
  );
}

function SplashFooter() {
  return (
    <footer className="bg-muted/30">
      <div className="px-6 py-10 md:px-10 md:py-12 lg:px-16">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-5">
          <div className="lg:col-span-2">
            <Link
              to={appRoutes.home}
              className="mb-4 flex items-center gap-2.5 font-semibold text-foreground"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
                <LayoutDashboard className="h-5 w-5" aria-hidden="true" />
              </span>
              <span className="text-lg font-bold tracking-tight">{appInfo.name}</span>
            </Link>
            <p className="mb-6 max-w-sm text-sm leading-relaxed text-muted-foreground">
              Build beautiful, secure admin dashboards with AI-ready architecture. Everything you
              need to ship fast.
            </p>
            <div className="flex gap-3">
              {socialLinks.map((social) => (
                <a
                  key={social.label}
                  href={social.href}
                  className="flex h-9 w-9 items-center justify-center rounded-lg border bg-background text-muted-foreground transition-colors hover:border-primary/50 hover:bg-primary/10 hover:text-primary"
                  aria-label={social.label}
                >
                  <social.icon className="h-4 w-4" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>

          <FooterColumn title="Product" links={productLinks} />
          <FooterColumn title="Company" links={companyLinks} />
          <FooterColumn title="Legal" links={legalLinks} />
        </div>

        <div className="mt-10 text-center md:text-left">
          <p className="text-sm text-muted-foreground">
            &copy; {new Date().getFullYear()} {appInfo.name}. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
}

function FooterColumn({
  title,
  links,
}: {
  title: string;
  links: { label: string; href: string }[];
}) {
  return (
    <div>
      <h3 className="mb-4 text-sm font-semibold text-foreground">{title}</h3>
      <ul className="space-y-3">
        {links.map((link) => (
          <li key={link.label}>
            {isAppPath(link.href) ? (
              <Link
                to={link.href}
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </Link>
            ) : (
              <a
                href={link.href}
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                {link.label}
              </a>
            )}
          </li>
        ))}
      </ul>
    </div>
  );
}

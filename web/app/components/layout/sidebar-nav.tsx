import { Link } from "react-router";

import type { SidebarNavSection } from "~/components/layout/sidebar-nav-items";
import { isPathActive } from "~/lib/string-helper.shared";
import { cn } from "~/lib/tw.shared";

interface SidebarNavProps {
  collapsed: boolean;
  onNavigate: () => void;
  pathname: string;
  sections: SidebarNavSection[];
}

export function SidebarNav({ collapsed, onNavigate, pathname, sections }: SidebarNavProps) {
  return (
    <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-4" aria-label="Main navigation">
      {sections.map((section) => (
        <div key={section.label}>
          <p
            className={cn(
              "h-6 overflow-hidden px-2 pb-2 text-xs font-medium uppercase text-sidebar-foreground/60 opacity-100 transition-[height,padding,opacity] duration-200 ease-linear",
              collapsed && "md:h-0 md:pb-0 md:opacity-0"
            )}
          >
            {section.label}
          </p>
          <ul className="space-y-1" aria-label={section.label}>
            {section.items.map((item) => {
              const Icon = item.icon;
              const active = isPathActive(pathname, item.href, item.exact);

              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    onClick={onNavigate}
                    aria-current={active ? "page" : undefined}
                    title={collapsed ? item.label : undefined}
                    className={cn(
                      "flex h-9 items-center gap-2 rounded-md px-2 text-sm outline-none transition-[background-color,color,padding] duration-200 ease-linear hover:bg-sidebar-accent hover:text-sidebar-accent-foreground focus-visible:ring-2 focus-visible:ring-sidebar-ring",
                      active && "bg-sidebar-accent font-medium text-sidebar-accent-foreground",
                      collapsed && "md:justify-center md:gap-0"
                    )}
                  >
                    <Icon className="size-4 shrink-0" aria-hidden="true" />
                    <span
                      aria-hidden={collapsed}
                      className={cn(
                        "max-w-44 truncate opacity-100 transition-[max-width,opacity] duration-200 ease-linear",
                        collapsed && "md:max-w-0 md:opacity-0"
                      )}
                    >
                      {item.label}
                    </span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}

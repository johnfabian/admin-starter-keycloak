import {
  Home,
  LayoutDashboard,
  ListTodo,
  Settings,
  Shield,
  UserRound,
  type LucideIcon,
} from "lucide-react";

import { appInfo, appRoutes } from "~/lib/app-settings.shared";

export interface SidebarNavItem {
  exact?: boolean;
  href: string;
  icon: LucideIcon;
  label: string;
}

export interface SidebarNavSection {
  adminOnly?: boolean;
  items: SidebarNavItem[];
  label: string;
}

export const sidebarNavSections: SidebarNavSection[] = [
  {
    adminOnly: true,
    label: "Admin",
    items: [
      {
        exact: true,
        href: appRoutes.adminsDashboard,
        icon: Shield,
        label: appInfo.pageTitles.adminsDashboard,
      },
    ],
  },
  {
    label: "User",
    items: [
      {
        exact: true,
        href: appRoutes.usersDashboard,
        icon: Home,
        label: appInfo.pageTitles.usersDashboard,
      },
      {
        href: appRoutes.profile,
        icon: UserRound,
        label: appInfo.pageTitles.profile,
      },
      {
        href: appRoutes.settings,
        icon: Settings,
        label: appInfo.pageTitles.settings,
      },
    ],
  },
  {
    label: "Apps",
    items: [
      {
        exact: true,
        href: appRoutes.appsDashboard,
        icon: LayoutDashboard,
        label: appInfo.pageTitles.appsDashboard,
      },
      {
        href: appRoutes.todos,
        icon: ListTodo,
        label: appInfo.pageTitles.todos,
      },
    ],
  },
];

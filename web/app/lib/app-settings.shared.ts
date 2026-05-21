export const appSettings = {
  app: {
    name: "Admin Starter",
    title: "Admin Starter Keycloak",
    description: "A Keycloak-powered admin starter for users, groups, permissions, and apps.",
    pageTitles: {
      usersDashboard: "User Dashboard",
      adminsDashboard: "Admin Dashboard",
      forbidden: "Forbidden",
    },
  },
  auth: {
    roles: {
      admins: "Admins",
      users: "Users",
    },
  },
  routes: {
    paths: {
      home: "/",
      users: "/users",
      usersDashboard: "/users/dashboard",
      admins: "/admins",
      adminsDashboard: "/admins/dashboard",
      forbidden: "/forbidden",
      authLogin: "/auth/login",
      authLoginWithPrompt: "/auth/login?prompt=login",
      authRegister: "/auth/register",
      authCallback: "/auth/callback",
      authAccount: "/auth/account",
      authLogout: "/auth/logout",
    },
    patterns: {
      users: "users",
      usersDashboard: "users/dashboard",
      admins: "admins",
      adminsDashboard: "admins/dashboard",
      forbidden: "forbidden",
      authLogin: "auth/login",
      authRegister: "auth/register",
      authCallback: "auth/callback",
      authAccount: "auth/account",
      authLogout: "auth/logout",
    },
    modules: {
      splash: "routes/splash.tsx",
      users: "routes/users.tsx",
      usersDashboard: "routes/users-dashboard.tsx",
      admins: "routes/admins.tsx",
      adminsDashboard: "routes/admins-dashboard.tsx",
      forbidden: "routes/forbidden.tsx",
      authLogin: "routes/auth-login.tsx",
      authRegister: "routes/auth-register.tsx",
      authCallback: "routes/auth-callback.tsx",
      authAccount: "routes/auth-account.tsx",
      authLogout: "routes/auth-logout.tsx",
    },
  },
  ui: {
    mobileBreakpoint: 768,
    theme: {
      storageKeys: {
        mode: "color-mode",
        theme: "color-theme",
      },
      storageEvent: "admin-starter-theme-storage",
      systemDarkModeQuery: "(prefers-color-scheme: dark)",
      defaultMode: "dark",
      defaultTheme: "teal",
      modes: [
        { value: "light", label: "Light" },
        { value: "dark", label: "Dark" },
        { value: "system", label: "System" },
      ],
      themes: [
        { value: "teal", label: "Teal", colorClass: "bg-teal-500" },
        { value: "blue", label: "Blue", colorClass: "bg-blue-500" },
        { value: "green", label: "Green", colorClass: "bg-green-500" },
        { value: "purple", label: "Purple", colorClass: "bg-purple-500" },
        { value: "orange", label: "Orange", colorClass: "bg-orange-500" },
        { value: "red", label: "Red", colorClass: "bg-red-500" },
        { value: "pink", label: "Pink", colorClass: "bg-pink-500" },
      ],
    },
  },
} as const;

export const appInfo = appSettings.app;
export const appRoles = appSettings.auth.roles;
export const appRoutes = appSettings.routes.paths;
export const appRoutePatterns = appSettings.routes.patterns;
export const appRouteModules = appSettings.routes.modules;
export const appUi = appSettings.ui;
export const appTheme = appSettings.ui.theme;

export type ColorMode = (typeof appTheme.modes)[number]["value"];
export type ColorTheme = (typeof appTheme.themes)[number]["value"];

export const appAccess = {
  adminRoutes: [appRoles.admins],
  userRoutes: [appRoles.users, appRoles.admins],
} as const;

export const appAccessAreas = {
  adminRoutes: "adminRoutes",
  userRoutes: "userRoutes",
} as const satisfies Record<keyof typeof appAccess, keyof typeof appAccess>;

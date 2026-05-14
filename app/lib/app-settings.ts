export const appSettings = {
  app: {
    name: "Admin Starter",
    title: "Admin Starter Keycloak",
    description: "A Keycloak-powered admin starter for users, groups, permissions, and apps.",
    pageTitles: {
      usersDashboard: "User Dashboard",
      adminsDashboard: "Admins",
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
      authLogout: "auth/logout",
    },
    modules: {
      home: "routes/home.tsx",
      users: "routes/users.tsx",
      usersDashboard: "routes/users-dashboard.tsx",
      admins: "routes/admins.tsx",
      adminsDashboard: "routes/admins-dashboard.tsx",
      forbidden: "routes/forbidden.tsx",
      authLogin: "routes/auth-login.tsx",
      authRegister: "routes/auth-register.tsx",
      authCallback: "routes/auth-callback.tsx",
      authLogout: "routes/auth-logout.tsx",
    },
  },
} as const;

export const appInfo = appSettings.app;
export const appRoles = appSettings.auth.roles;
export const appRoutes = appSettings.routes.paths;
export const appRoutePatterns = appSettings.routes.patterns;
export const appRouteModules = appSettings.routes.modules;

export const appAccess = {
  adminRoutes: [appRoles.admins],
  userRoutes: [appRoles.users, appRoles.admins],
} as const;

export const appAccessAreas = {
  adminRoutes: "adminRoutes",
  userRoutes: "userRoutes",
} as const satisfies Record<keyof typeof appAccess, keyof typeof appAccess>;

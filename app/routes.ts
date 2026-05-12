import { type RouteConfig, index, route } from "@react-router/dev/routes";

export default [
  index("routes/home.tsx"),
  route("users", "routes/users.tsx"),
  route("users/dashboard", "routes/users-dashboard.tsx"),
  route("admins", "routes/admins.tsx"),
  route("admins/dashboard", "routes/admins-dashboard.tsx"),
  route("forbidden", "routes/forbidden.tsx"),
  route("auth/login", "routes/auth-login.tsx"),
  route("auth/register", "routes/auth-register.tsx"),
  route("auth/callback", "routes/auth-callback.tsx"),
  route("auth/logout", "routes/auth-logout.tsx"),
] satisfies RouteConfig;

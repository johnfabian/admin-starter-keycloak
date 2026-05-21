import { type RouteConfig, index, route } from "@react-router/dev/routes";

import { appRouteModules, appRoutePatterns } from "./lib/app-settings";

export default [
  index(appRouteModules.splash),
  route(appRoutePatterns.users, appRouteModules.users),
  route(appRoutePatterns.usersDashboard, appRouteModules.usersDashboard),
  route(appRoutePatterns.admins, appRouteModules.admins),
  route(appRoutePatterns.adminsDashboard, appRouteModules.adminsDashboard),
  route(appRoutePatterns.forbidden, appRouteModules.forbidden),
  route(appRoutePatterns.authLogin, appRouteModules.authLogin),
  route(appRoutePatterns.authRegister, appRouteModules.authRegister),
  route(appRoutePatterns.authCallback, appRouteModules.authCallback),
  route(appRoutePatterns.authAccount, appRouteModules.authAccount),
  route(appRoutePatterns.authLogout, appRouteModules.authLogout),
] satisfies RouteConfig;

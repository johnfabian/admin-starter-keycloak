import { type RouteConfig, index, route } from "@react-router/dev/routes";

import { appRouteModules, appRoutePatterns } from "./lib/app-settings.shared";

export default [
  index(appRouteModules.splash),
  route(appRoutePatterns.users, appRouteModules.users),
  route(appRoutePatterns.usersDashboard, appRouteModules.usersDashboard),
  route(appRoutePatterns.admins, appRouteModules.admins),
  route(appRoutePatterns.adminsDashboard, appRouteModules.adminsDashboard),
  route(appRoutePatterns.profile, appRouteModules.profile),
  route(appRoutePatterns.settings, appRouteModules.settings),
  route(appRoutePatterns.apps, appRouteModules.apps),
  route(appRoutePatterns.appsDashboard, appRouteModules.appsDashboard),
  route(appRoutePatterns.todos, appRouteModules.todos),
  route(appRoutePatterns.forbidden, appRouteModules.forbidden),
  route(appRoutePatterns.authLogin, appRouteModules.authLogin),
  route(appRoutePatterns.authRegister, appRouteModules.authRegister),
  route(appRoutePatterns.authCallback, appRouteModules.authCallback),
  route(appRoutePatterns.authAccount, appRouteModules.authAccount),
  route(appRoutePatterns.authLogout, appRouteModules.authLogout),
  route(appRoutePatterns.chromeDevtools, appRouteModules.chromeDevtools),
] satisfies RouteConfig;

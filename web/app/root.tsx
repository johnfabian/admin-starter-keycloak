import {
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
  useRouteLoaderData,
} from "react-router";

import { ErrorPage } from "./components/error-page";
import { appTheme } from "./lib/app-settings.shared";
import { getCookieValue } from "./lib/cookie.shared";
import { getValidColorMode, getValidColorTheme } from "./lib/theme.shared";
import type { Route } from "./+types/root";
import { ThemeProvider } from "./providers/theme-provider";
import "./app.css";

export const links: Route.LinksFunction = () => [
  { rel: "icon", href: "/favicon.ico", sizes: "any" },
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
];

export function loader({ request }: Route.LoaderArgs) {
  const cookieHeader = request.headers.get("Cookie");
  const colorMode = getValidColorMode(getCookieValue(cookieHeader, appTheme.cookieKeys.mode));
  const colorTheme = getValidColorTheme(getCookieValue(cookieHeader, appTheme.cookieKeys.theme));
  const isDark = colorMode === "dark";

  return {
    theme: {
      colorMode,
      colorTheme,
      colorScheme: isDark ? "dark" : "light",
      htmlClassName: isDark ? "dark" : undefined,
    },
  };
}

function BaseLayout({
  children,
  theme,
}: {
  children: React.ReactNode;
  theme: Awaited<ReturnType<typeof loader>>["theme"];
}) {
  return (
    <html
      lang="en"
      className={theme.htmlClassName}
      data-theme={theme.colorTheme}
      style={{ colorScheme: theme.colorScheme }}
      suppressHydrationWarning
    >
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
      </head>
      <body>
        <ThemeProvider
          initialColorMode={theme.colorMode}
          initialColorTheme={theme.colorTheme}
        >
          {children}
        </ThemeProvider>
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

export function Layout({ children }: { children: React.ReactNode }) {
  const loaderData = useRouteLoaderData<typeof loader>("root");
  const theme = loaderData?.theme ?? {
    colorMode: appTheme.defaultMode,
    colorTheme: appTheme.defaultTheme,
    colorScheme: "dark",
    htmlClassName: "dark",
  };

  return <BaseLayout theme={theme}>{children}</BaseLayout>;
}

export default function App() {
  return <Outlet />;
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  return <ErrorPage error={error} />;
}

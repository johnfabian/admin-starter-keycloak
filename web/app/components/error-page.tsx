import { ArrowLeft, Home, LogIn, RefreshCw } from "lucide-react";
import { isRouteErrorResponse, Link, useNavigate } from "react-router";

import { Button } from "~/components/ui/button";
import { appInfo, appRoutes } from "~/lib/app-settings.shared";

interface ErrorView {
  actionHref: string;
  actionLabel: string;
  description: string;
  status: number;
  title: string;
}

const ERROR_PAGE_CONFIG = {
  defaultStatus: 500,
  status: {
    notFound: 404,
    unauthorized: 401,
    forbidden: 403,
    methodNotAllowed: 405,
    badGateway: 502,
    unavailable: 503,
  },
  views: {
    notFound: {
      actionHref: appRoutes.home,
      actionLabel: "Go back",
      description: "The page you requested could not be found.",
      status: 404,
      title: "Page not found",
    },
    unauthorized: {
      actionHref: appRoutes.authLoginWithPrompt,
      actionLabel: "Sign in",
      description: "Your session is missing or has expired. Sign in to continue.",
      status: 401,
      title: "Authentication required",
    },
    forbidden: {
      actionHref: appRoutes.forbidden,
      actionLabel: "View details",
      description: "Your account does not have access to this area.",
      status: 403,
      title: "Access denied",
    },
    methodNotAllowed: {
      actionHref: appRoutes.home,
      actionLabel: "Go home",
      description: "This action cannot be completed from the current request.",
      status: 405,
      title: "Action not allowed",
    },
    badGateway: {
      actionHref: appRoutes.authLoginWithPrompt,
      actionLabel: "Try signing in again",
      description: "The authentication service returned an unexpected response.",
      status: 502,
      title: "Authentication could not be completed",
    },
    unavailable: {
      actionHref: appRoutes.authLoginWithPrompt,
      actionLabel: "Retry sign in",
      description: "The authentication service is temporarily unavailable.",
      status: 503,
      title: "Service unavailable",
    },
    default: {
      actionHref: appRoutes.home,
      actionLabel: "Go home",
      description: "Something went wrong. Please try again.",
      status: 500,
      title: "Unexpected error",
    },
  },
} as const;

export function buildRouteErrorView(error: unknown): ErrorView {
  if (!isRouteErrorResponse(error)) {
    return ERROR_PAGE_CONFIG.views.default;
  }

  return buildRouteErrorViewFromStatus(error.status);
}

export function buildRouteErrorViewFromStatus(status: number): ErrorView {
  switch (status) {
    case ERROR_PAGE_CONFIG.status.notFound:
      return ERROR_PAGE_CONFIG.views.notFound;
    case ERROR_PAGE_CONFIG.status.unauthorized:
      return ERROR_PAGE_CONFIG.views.unauthorized;
    case ERROR_PAGE_CONFIG.status.forbidden:
      return ERROR_PAGE_CONFIG.views.forbidden;
    case ERROR_PAGE_CONFIG.status.methodNotAllowed:
      return ERROR_PAGE_CONFIG.views.methodNotAllowed;
    case ERROR_PAGE_CONFIG.status.badGateway:
      return ERROR_PAGE_CONFIG.views.badGateway;
    case ERROR_PAGE_CONFIG.status.unavailable:
      return ERROR_PAGE_CONFIG.views.unavailable;
    default:
      return {
        ...ERROR_PAGE_CONFIG.views.default,
        status: status || ERROR_PAGE_CONFIG.defaultStatus,
      };
  }
}

export function ErrorPage({
  error,
  heading = appInfo.name,
  status,
}: {
  error?: unknown;
  heading?: string;
  status?: number;
}) {
  const navigate = useNavigate();
  const view =
    typeof status === "number" ? buildRouteErrorViewFromStatus(status) : buildRouteErrorView(error);
  const Icon = view.status === ERROR_PAGE_CONFIG.status.unavailable ? RefreshCw : Home;
  const isLoginAction = view.actionHref.startsWith(appRoutes.authLogin);
  const isNotFound = view.status === ERROR_PAGE_CONFIG.status.notFound;
  const showHomeAction = isNotFound || view.actionHref !== appRoutes.home;

  const handleBack = () => {
    if (window.history.length > 1) {
      navigate(-1);
      return;
    }

    navigate(appRoutes.home);
  };

  return (
    <main className="flex min-h-screen items-center justify-center bg-muted/30 px-4 py-10 text-foreground">
      <section className="w-full max-w-xl rounded-xl border bg-card p-8 shadow-sm">
        <p className="text-sm font-medium uppercase text-muted-foreground">{heading}</p>
        <div className="mt-5 flex size-12 items-center justify-center rounded-xl bg-primary text-primary-foreground">
          <Icon className="size-5" aria-hidden="true" />
        </div>
        <p className="mt-6 text-sm font-medium text-muted-foreground">Error {view.status}</p>
        <h1 className="mt-2 text-3xl font-semibold tracking-tight">{view.title}</h1>
        <p className="mt-3 text-sm leading-6 text-muted-foreground">{view.description}</p>
        <div className="mt-6 flex flex-wrap gap-3">
          {isNotFound ? (
            <Button type="button" onClick={handleBack}>
              <ArrowLeft className="size-4" aria-hidden="true" />
              {view.actionLabel}
            </Button>
          ) : (
            <Button asChild>
              <Link to={view.actionHref}>
                {isLoginAction ? (
                  <LogIn className="size-4" aria-hidden="true" />
                ) : (
                  <Home className="size-4" aria-hidden="true" />
                )}
                {view.actionLabel}
              </Link>
            </Button>
          )}
          {showHomeAction ? (
            <Button asChild variant="outline">
              <Link to={appRoutes.home}>Home</Link>
            </Button>
          ) : null}
        </div>
      </section>
    </main>
  );
}

export function RouteErrorBoundary({ error }: { error: unknown }) {
  return <ErrorPage error={error} />;
}

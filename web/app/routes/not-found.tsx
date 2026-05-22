import { data } from "react-router";

import { ErrorPage } from "~/components/error-page";

const NOT_FOUND_STATUS = 404;

export function loader() {
  return data(null, { status: NOT_FOUND_STATUS });
}

export default function NotFound() {
  return <ErrorPage status={NOT_FOUND_STATUS} />;
}

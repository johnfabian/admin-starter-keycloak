export const errorPreviewStatuses = [
  { label: "401", status: 401 },
  { label: "403", status: 403 },
  { label: "405", status: 405 },
  { label: "500", status: 500 },
  { label: "502", status: 502 },
  { label: "503", status: 503 },
] as const;

export type ErrorPreviewStatus = (typeof errorPreviewStatuses)[number]["status"];

export function isErrorPreviewStatus(status: number): status is ErrorPreviewStatus {
  return errorPreviewStatuses.some((preview) => preview.status === status);
}

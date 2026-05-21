import postgres from "postgres";

import { getAuthConfig } from "~/lib/server/auth-config.server";

let databaseClient: postgres.Sql | undefined;

function createDatabaseClient() {
  return postgres(getAuthConfig().databaseUrl, {
    transform: {
      column: postgres.toCamel,
    },
  });
}

export function getDatabase() {
  databaseClient ??= createDatabaseClient();

  return databaseClient;
}

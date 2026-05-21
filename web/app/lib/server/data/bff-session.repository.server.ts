import { getDatabase } from "~/lib/server/data/database.server";
import type { CurrentUser } from "~/models/current-user";

export interface BffSessionRecord {
  id: string;
  userData: CurrentUser;
  tokenPayload: string;
  lastSeenAt: Date;
}

interface CreateBffSessionRecord {
  id: string;
  userId: string;
  userData: CurrentUser;
  tokenPayload: string;
  accessTokenExpiresAt: string;
  refreshTokenExpiresAt: string | null;
}

interface UpdateBffSessionRecord {
  id: string;
  userData: CurrentUser;
  tokenPayload: string;
  accessTokenExpiresAt: string;
  refreshTokenExpiresAt: string | null;
}

function toUserJson(user: CurrentUser) {
  return {
    id: user.id,
    firstName: user.firstName,
    lastName: user.lastName,
    name: user.name,
    email: user.email,
    image: user.image,
    roles: user.roles,
  };
}

export async function insertBffSessionRecord(record: CreateBffSessionRecord) {
  const sql = getDatabase();

  await sql`
    INSERT INTO web_bff_sessions (
      id,
      user_id,
      user_data,
      token_payload,
      access_token_expires_at,
      refresh_token_expires_at
    )
    VALUES (
      ${record.id},
      ${record.userId},
      ${sql.json(toUserJson(record.userData))},
      ${record.tokenPayload},
      ${record.accessTokenExpiresAt},
      ${record.refreshTokenExpiresAt}
    )
  `;
}

export async function findBffSessionRecordById(sessionId: string) {
  const sql = getDatabase();
  const result = await sql<BffSessionRecord[]>`
    SELECT id, user_data, token_payload, last_seen_at
    FROM web_bff_sessions
    WHERE id = ${sessionId}
  `;

  return result[0] ?? null;
}

export async function touchBffSessionRecord(sessionId: string) {
  const sql = getDatabase();

  await sql`
    UPDATE web_bff_sessions
    SET last_seen_at = now()
    WHERE id = ${sessionId}
  `;
}

export async function updateBffSessionRecord(record: UpdateBffSessionRecord) {
  const sql = getDatabase();

  await sql`
    UPDATE web_bff_sessions
    SET
      user_data = ${sql.json(toUserJson(record.userData))},
      token_payload = ${record.tokenPayload},
      access_token_expires_at = ${record.accessTokenExpiresAt},
      refresh_token_expires_at = ${record.refreshTokenExpiresAt},
      updated_at = now(),
      last_seen_at = now()
    WHERE id = ${record.id}
  `;
}

export async function deleteBffSessionRecord(sessionId: string) {
  const sql = getDatabase();

  await sql`
    DELETE FROM web_bff_sessions
    WHERE id = ${sessionId}
  `;
}

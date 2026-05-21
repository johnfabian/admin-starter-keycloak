import crypto from "node:crypto";

import { getAuthConfig } from "~/lib/server/auth-config.server";
import {
  deleteBffSessionRecord,
  findBffSessionRecordById,
  insertBffSessionRecord,
  touchBffSessionRecord,
  updateBffSessionRecord,
  type BffSessionRecord,
} from "~/lib/server/data/bff-session.repository.server";
import { decryptTokenPayload, encryptTokenPayload } from "~/lib/server/token-crypto.server";
import type { CurrentUser } from "~/models/current-user";

export interface BffTokenSet {
  accessToken: string;
  refreshToken: string;
  idToken: string;
  tokenType: string;
  scope: string;
  accessTokenExpiresAt: string;
  refreshTokenExpiresAt: string | null;
}

export interface BffSession {
  id: string;
  user: CurrentUser;
  tokens: BffTokenSet;
}

function isExpired(value: string | null) {
  return Boolean(value && new Date(value).getTime() <= Date.now());
}

function shouldTouchSession(lastSeenAt: Date) {
  const { sessionLastSeenUpdateSeconds } = getAuthConfig();
  return Date.now() - lastSeenAt.getTime() >= sessionLastSeenUpdateSeconds * 1000;
}

function readSessionRecord(record: BffSessionRecord): BffSession {
  return {
    id: record.id,
    user: record.userData,
    tokens: decryptTokenPayload<BffTokenSet>(record.tokenPayload),
  };
}

export async function createBffSession(user: CurrentUser, tokens: BffTokenSet) {
  const id = crypto.randomUUID();
  const tokenPayload = encryptTokenPayload(tokens);

  await insertBffSessionRecord({
    id,
    userId: user.id,
    userData: user,
    tokenPayload,
    accessTokenExpiresAt: tokens.accessTokenExpiresAt,
    refreshTokenExpiresAt: tokens.refreshTokenExpiresAt,
  });

  return id;
}

export async function getBffSession(sessionId: string) {
  const record = await findBffSessionRecordById(sessionId);

  if (!record) return null;

  const session = readSessionRecord(record);

  if (isExpired(session.tokens.refreshTokenExpiresAt)) {
    await deleteBffSession(sessionId);
    return null;
  }

  // Avoid turning every authenticated page load into a database write.
  if (shouldTouchSession(record.lastSeenAt)) {
    await touchBffSessionRecord(sessionId);
  }

  return session;
}

export async function updateBffSession(session: BffSession) {
  await updateBffSessionRecord({
    id: session.id,
    userData: session.user,
    tokenPayload: encryptTokenPayload(session.tokens),
    accessTokenExpiresAt: session.tokens.accessTokenExpiresAt,
    refreshTokenExpiresAt: session.tokens.refreshTokenExpiresAt,
  });
}

export async function deleteBffSession(sessionId: string) {
  await deleteBffSessionRecord(sessionId);
}

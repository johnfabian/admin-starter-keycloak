import crypto from "node:crypto";

import { toBase64Url } from "~/lib/string-helper.shared";

const PKCE_CONFIG = {
  codeChallengeMethod: "S256",
  codeVerifierHashAlgorithm: "sha256",
  randomTokenBytes: 32,
  tokenEncoding: "base64",
} as const;

export const pkceCodeChallengeMethod = PKCE_CONFIG.codeChallengeMethod;

export function createRandomToken() {
  return toBase64Url(
    crypto.randomBytes(PKCE_CONFIG.randomTokenBytes).toString(PKCE_CONFIG.tokenEncoding)
  );
}

export function createCodeChallenge(codeVerifier: string) {
  const challenge = crypto
    .createHash(PKCE_CONFIG.codeVerifierHashAlgorithm)
    .update(codeVerifier)
    .digest(PKCE_CONFIG.tokenEncoding);

  return toBase64Url(challenge);
}

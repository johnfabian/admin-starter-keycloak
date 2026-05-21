import crypto from "node:crypto";

import { getAuthConfig } from "~/lib/server/auth-config.server";

const TOKEN_CRYPTO_CONFIG = {
  algorithm: "aes-256-gcm",
  digestAlgorithm: "sha256",
  encryptedPayloadSeparator: ".",
  encoding: "utf8",
  encryptedPayloadEncoding: "base64url",
  initializationVectorBytes: 12,
  invalidPayloadMessage: "Token payload is not in the expected encrypted format.",
} as const;

function getEncryptionKey() {
  return crypto
    .createHash(TOKEN_CRYPTO_CONFIG.digestAlgorithm)
    .update(getAuthConfig().tokenEncryptionKey, TOKEN_CRYPTO_CONFIG.encoding)
    .digest();
}

export function encryptTokenPayload(value: unknown) {
  const iv = crypto.randomBytes(TOKEN_CRYPTO_CONFIG.initializationVectorBytes);
  const cipher = crypto.createCipheriv(TOKEN_CRYPTO_CONFIG.algorithm, getEncryptionKey(), iv);
  const plaintext = JSON.stringify(value);
  const encrypted = Buffer.concat([
    cipher.update(plaintext, TOKEN_CRYPTO_CONFIG.encoding),
    cipher.final(),
  ]);
  const tag = cipher.getAuthTag();

  return [iv, tag, encrypted]
    .map((part) => part.toString(TOKEN_CRYPTO_CONFIG.encryptedPayloadEncoding))
    .join(TOKEN_CRYPTO_CONFIG.encryptedPayloadSeparator);
}

export function decryptTokenPayload<T>(value: string): T {
  const [ivValue, tagValue, encryptedValue] = value.split(
    TOKEN_CRYPTO_CONFIG.encryptedPayloadSeparator
  );

  if (!ivValue || !tagValue || !encryptedValue) {
    throw new Error(TOKEN_CRYPTO_CONFIG.invalidPayloadMessage);
  }

  const decipher = crypto.createDecipheriv(
    TOKEN_CRYPTO_CONFIG.algorithm,
    getEncryptionKey(),
    Buffer.from(ivValue, TOKEN_CRYPTO_CONFIG.encryptedPayloadEncoding)
  );

  decipher.setAuthTag(Buffer.from(tagValue, TOKEN_CRYPTO_CONFIG.encryptedPayloadEncoding));

  const decrypted = Buffer.concat([
    decipher.update(Buffer.from(encryptedValue, TOKEN_CRYPTO_CONFIG.encryptedPayloadEncoding)),
    decipher.final(),
  ]);

  return JSON.parse(decrypted.toString(TOKEN_CRYPTO_CONFIG.encoding)) as T;
}

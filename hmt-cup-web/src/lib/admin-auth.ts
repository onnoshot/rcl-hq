import { createHash } from "crypto";

export const ADMIN_COOKIE = "hmtcup_admin";

export function expectedSessionToken() {
  const password = process.env.ADMIN_PASSWORD ?? "";
  const secret = process.env.ADMIN_SESSION_SECRET ?? "";
  return createHash("sha256").update(`${password}::${secret}`).digest("hex");
}

export function checkPassword(input: string) {
  return input.length > 0 && input === (process.env.ADMIN_PASSWORD ?? "");
}

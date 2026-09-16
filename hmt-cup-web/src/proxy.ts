import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { ADMIN_COOKIE, expectedSessionToken } from "@/lib/admin-auth";

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  if (pathname === "/admin/login" || pathname === "/api/admin/login") {
    return NextResponse.next();
  }

  const isProtected =
    pathname.startsWith("/admin") ||
    (pathname.startsWith("/api/admin") && pathname !== "/api/admin/login");

  if (!isProtected) return NextResponse.next();

  const token = request.cookies.get(ADMIN_COOKIE)?.value;
  if (token && token === expectedSessionToken()) {
    return NextResponse.next();
  }

  if (pathname.startsWith("/api/")) {
    return NextResponse.json({ error: "unauthorized" }, { status: 401 });
  }

  const loginUrl = new URL("/admin/login", request.url);
  return NextResponse.redirect(loginUrl);
}

export const config = {
  matcher: ["/admin/:path*", "/api/admin/:path*"],
};

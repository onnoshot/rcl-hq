"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { TAB_ITEMS } from "./nav-items";

export function BottomTabBar() {
  const pathname = usePathname();

  if (pathname.startsWith("/admin")) return null;

  return (
    <nav className="pb-safe fixed inset-x-0 bottom-0 z-[100] border-t border-white/10 bg-ink/85 backdrop-blur-xl lg:hidden">
      <div className="mx-auto flex max-w-md items-stretch justify-between px-2 pt-2">
        {TAB_ITEMS.map((item) => {
          const active =
            item.href === "/" ? pathname === "/" : pathname.startsWith(item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className="flex flex-1 flex-col items-center gap-1 rounded-2xl px-1 py-1.5 text-white/50 transition-colors active:bg-white/5"
            >
              <span className={active ? "text-red-bright" : ""}>
                {item.icon(active)}
              </span>
              <span
                className={`text-[10px] font-medium tracking-tight ${
                  active ? "text-white" : "text-white/45"
                }`}
              >
                {item.label}
              </span>
              {active && (
                <span className="absolute -mt-[26px] h-1 w-1 rounded-full bg-red-bright" />
              )}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}

export type NavItem = {
  href: string;
  label: string;
  icon: (active: boolean) => React.ReactNode;
};

const strokeIcon = (d: string, active: boolean, extra?: React.ReactNode) => (
  <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
    <path
      d={d}
      stroke={active ? "#E82020" : "currentColor"}
      strokeWidth={active ? 2.1 : 1.7}
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    {extra}
  </svg>
);

export const TAB_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Ana Sayfa",
    icon: (active) =>
      strokeIcon("M4 11.5 12 5l8 6.5M6 10v9h5v-5h2v5h5v-9", active),
  },
  {
    href: "/turnuva",
    label: "Turnuva",
    icon: (active) =>
      strokeIcon(
        "M8 21h8M12 17v4M6 4h12v3a6 6 0 0 1-12 0V4ZM4 5h2v2a3 3 0 0 1-2-2Zm16 0h-2v2a3 3 0 0 0 2-2Z",
        active
      ),
  },
  {
    href: "/galeri",
    label: "Galeri",
    icon: (active) =>
      strokeIcon(
        "M4 5h16v14H4V5Zm2 11 4-5 3 3.5 2-2.5L20 15",
        active,
        <circle cx="8.5" cy="9" r="1.3" fill={active ? "#E82020" : "currentColor"} />
      ),
  },
  {
    href: "/lig",
    label: "Lig",
    icon: (active) =>
      strokeIcon("M5 19V11M12 19V5M19 19v-6", active),
  },
  {
    href: "/iletisim",
    label: "İletişim",
    icon: (active) =>
      strokeIcon(
        "M4 6h16v12H4V6Zm0 0 8 7 8-7",
        active
      ),
  },
];

export const NAV_LINKS: NavItem[] = [
  { href: "/turnuva", label: "Turnuva", icon: () => null },
  { href: "/galeri", label: "Galeri", icon: () => null },
  { href: "/scout", label: "Scout", icon: () => null },
  { href: "/gelisim", label: "Gelişim", icon: () => null },
  { href: "/lig", label: "Lig", icon: () => null },
  { href: "/iletisim", label: "İletişim", icon: () => null },
];

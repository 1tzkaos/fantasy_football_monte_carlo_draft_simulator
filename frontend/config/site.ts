export type SiteConfig = typeof siteConfig;

export const siteConfig = {
  name: "Next.js + NextUI",
  description: "Make beautiful websites regardless of your design experience.",
  navItems: [
    {
      label: "Home",
      href: "/",
    },
    {
      label: "Setup",
      href: "/setup",
    },
    {
      label: "Draft",
      href: "/draft",
    },
  ],
  navMenuItems: [
    {
      label: "Setup",
      href: "/setup",
    },
    {
      label: "Draft",
      href: "/draft",
    },
  ],
  links: {
    github:
      "https://github.com/joewlos/fantasy_football_monte_carlo_draft_simulator",
  },
};

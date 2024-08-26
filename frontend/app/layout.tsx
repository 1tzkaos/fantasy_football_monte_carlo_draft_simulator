import "@/styles/globals.css";
import { Metadata, Viewport } from "next";
import { Link } from "@nextui-org/link";
import clsx from "clsx";

import { Providers } from "./providers";

import { siteConfig } from "@/config/site";
import { fontSans } from "@/config/fonts";
import { Navbar } from "@/components/navbar";

export const metadata: Metadata = {
  title: {
    default: siteConfig.name,
    template: `%s - ${siteConfig.name}`,
  },
  description: siteConfig.description,
  icons: {
    icon: "/favicon.ico",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "white" },
    { media: "(prefers-color-scheme: dark)", color: "black" },
  ],
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html suppressHydrationWarning lang="en">
      <head />
      <body
        className={clsx(
          "min-h-screen font-sans antialiased",
          fontSans.variable,
        )}
      >
        <Providers themeProps={{ attribute: "class", defaultTheme: "dark" }}>
          <div className="relative flex flex-col h-screen">
            {/* Background image */}
            <div
              className="
                absolute w-screen h-screen 
                bg-cover bg-no-repeat bg-right bg-scroll 
                opacity-100 z-1 hide-on-light
              "
              style={{
                backgroundImage: "url('/football_dark.png')",
              }}
            />
            <div
              className="
                absolute w-screen h-screen 
                bg-cover bg-no-repeat bg-right bg-scroll 
                opacity-50 z-1 hide-on-dark
              "
              style={{
                backgroundImage: "url('/football_light.png')",
              }}
            />
            {/* Content */}
            <Navbar />
            <main className="container relative mx-auto max-w-7xl pt-16 px-6 flex-grow z-2">
              {children}
            </main>
            <footer
              className="
                w-full relative z-2 
                flex flex-col items-center justify-center px-6 py-3
              "
            >
              <p className="text-default-600 text-current">By Joe Wlos</p>
              <p className="text-default-600 text-current">
                Powered by{" "}
                <Link
                  isExternal
                  className="text-primary"
                  href="https://nextui-docs-v2.vercel.app?utm_source=next-app-template"
                  title="nextui.org homepage"
                >
                  NextUI
                </Link>{" "}
                and{" "}
                <Link
                  isExternal
                  className="text-primary"
                  href="https://art049.github.io/odmantic/"
                  title="odmantic homepage"
                >
                  ODMantic
                </Link>
              </p>
            </footer>
          </div>
        </Providers>
      </body>
    </html>
  );
}

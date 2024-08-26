import { Link } from "@nextui-org/link";
import { Snippet } from "@nextui-org/snippet";
import { Code } from "@nextui-org/code";
import { button as buttonStyles } from "@nextui-org/theme";

import { siteConfig } from "@/config/site";
import { title, subtitle } from "@/components/primitives";
import { GithubIcon } from "@/components/icons";

export default function Home() {
  return (
    <section className="flex flex-col items-center justify-center gap-8 py-8 md:py-10">
      <div className="inline-block max-w-lg text-center justify-center">
        <h1 className={title()}>Make&nbsp;</h1>
        <h1 className={title({ color: "green" })}>statistically sound&nbsp;</h1>
        <br className="hidden md:inline" />
        <h1 className={title()}>picks for every position.</h1>
        <h2 className={subtitle({ class: "mb-0" })}>
          Harness the power of (kind of sort of) artificial intelligence to
          draft players for your fantasy football team.
        </h2>
      </div>

      <div className="flex">
        <Link
          isExternal
          className={buttonStyles({ variant: "bordered", radius: "full" })}
          href={siteConfig.links.github}
        >
          <GithubIcon size={20} />
          GitHub
        </Link>
      </div>

      <div>
        <Snippet hideCopyButton hideSymbol variant="bordered">
          <span>
            Get started by{" "}
            <Link href="/setup">
              <Code color="primary">setting up</Code>
            </Link>{" "}
            a draft
          </span>
        </Snippet>
      </div>
    </section>
  );
}

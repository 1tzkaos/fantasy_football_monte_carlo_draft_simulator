import Link from "next/link";

import { title, subtitle } from "@/components/primitives";

export default function NotFound() {
  return (
    <section className="flex flex-col items-center justify-center gap-8 py-8 md:py-10">
      <div className="inline-block max-w-lg text-center justify-center">
        <h1 className={title()}>{`False start.`}</h1>
        <h2 className={subtitle()}>
          404. That page does not exist. Try again, or{" "}
          <Link className={"text-lg lg:text-xl text-primary"} href="/">
            go home
          </Link>
          .
        </h2>
      </div>
    </section>
  );
}

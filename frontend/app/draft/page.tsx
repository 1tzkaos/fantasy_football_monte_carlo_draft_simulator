"use client";

import { createContext, useState } from "react";
import { button as buttonStyles } from "@nextui-org/theme";
import { Link } from "@nextui-org/link";
import clsx from "clsx";

import { fontMono } from "@/config/fonts";
import { PlayIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";
import { DraftSettings } from "@/types";

interface DraftContextType {
  draftSettings: DraftSettings[];
}

const DraftContext = createContext<DraftContextType>({
  draftSettings: [],
});

export default function DraftPage() {
  const [draftSettings, setDraftSettings] = useState<DraftSettings[]>([
    {
      id: "#", // Replace with actual ID from API
      name: "Example Draft",
      created: "2024-09-01",
    },
  ]);

  return (
    <section className="flex flex-col items-center justify-center gap-8 py-8 md:py-10">
      <div className="inline-block max-w-lg text-center justify-center">
        <h1 className={title()}>{`Enter your draft room.`}</h1>
        <h2 className={subtitle()}>
          {`
          Choose one of your previously uploaded settings to train a logistic regression
         and run a round-by-round Monte Carlo simulation of your league's draft.
        `}
        </h2>
      </div>

      {/* Iterate through the available settings and display them as a clickable btn */}
      <div className="flex flex-col gap-4 w-full">
        <DraftContext.Provider value={{ draftSettings }}>
          {draftSettings.map((draftSetting) => (
            <Link
              key={draftSetting.id}
              className={
                buttonStyles({
                  size: "lg",
                  variant: "bordered",
                  fullWidth: true,
                  radius: "full",
                }) +
                " flex flex-row gap-1 p-12 justify-start items-center w-full"
              }
              href={`/draft/${draftSetting.id}`}
            >
              <div className="text-left">
                <p className="text-xl">{draftSetting.name}</p>
                <p className={clsx("font-mono", fontMono.variable)}>
                  {draftSetting.created}
                </p>
              </div>
              <div className="flex-grow flex justify-end text-primary">
                <PlayIcon />
              </div>
            </Link>
          ))}
        </DraftContext.Provider>
      </div>
    </section>
  );
}

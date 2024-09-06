"use client";

import { createContext } from "react";
import { button as buttonStyles } from "@nextui-org/theme";
import { Button } from "@nextui-org/button";
import { Code } from "@nextui-org/code";
import { Link } from "@nextui-org/link";
import { Spinner } from "@nextui-org/spinner";
import clsx from "clsx";

import {
  useCreateDraftMutation,
  useGetLeaguesQuery,
} from "@/api/services/league";
import { fontMono } from "@/config/fonts";
import { PlayIcon } from "@/components/icons";
import { title, subtitle } from "@/components/primitives";
import { LeagueSimple } from "@/types";

interface DraftContextType {
  leagues: LeagueSimple[];
  handleCreateDraft: (id: string) => void;
  isLoading: boolean;
}

const DraftContext = createContext<DraftContextType>({
  leagues: [],
  handleCreateDraft: () => {},
  isLoading: true,
});

export default function DraftPage() {
  const { data: leagues = [], isLoading } = useGetLeaguesQuery("");
  const [createDraft] = useCreateDraftMutation();

  // Create a draft for the selected league and navigate to that page when successful
  const handleCreateDraft = async (id: string) => {
    const newDraft = await createDraft({ id }).unwrap();

    window.location.href = `/draft-room/${newDraft.id}`;
  };

  return (
    <section className="flex flex-col items-center justify-center gap-8">
      <div className="inline-block max-w-lg text-center justify-center">
        <h1 className={title()}>{`Enter your draft room.`}</h1>
        <h2 className={subtitle()}>
          Choose one of your{" "}
          <Link className={"text-lg lg:text-xl"} href="/setup">
            previously configured settings
          </Link>{" "}
          to train a logistic regression and run a round-by-round Monte Carlo
          simulation of your {`league's`} draft.
        </h2>
      </div>

      {/* Iterate through the available settings and display them as a clickable btn */}
      <div className="flex flex-col gap-4 w-full items-center">
        <DraftContext.Provider
          value={{ leagues, handleCreateDraft, isLoading }}
        >
          {leagues.map((league) => (
            <Button
              key={league.id}
              className={
                buttonStyles({
                  size: "lg",
                  variant: "bordered",
                }) +
                " flex flex-row gap-1 p-12 justify-start items-center w-11/12"
              }
              onClick={() => handleCreateDraft(league.id)}
            >
              <div className="w-3/4 md:w-fit text-left">
                <p className="text-xl text-wrap">{league.name}</p>
                <p className={clsx("font-mono", fontMono.variable)}>
                  {new Date(league.created).toLocaleDateString()}
                </p>
              </div>
              <div className="w-1/4 md:flex-grow flex justify-end items-center text-primary">
                <PlayIcon />
              </div>
            </Button>
          ))}

          {/* If there are no drafts, give an error that there are none available */}
          {leagues.length === 0 && !isLoading ? (
            <Code color="danger">No draft settings found.</Code>
          ) : null}

          {/* If the draft is loading, show the spinner */}
          {isLoading && (
            <div className="flex items-center">
              <Spinner size="sm" />
              <span className="ml-2">Loading</span>
            </div>
          )}
        </DraftContext.Provider>
      </div>
    </section>
  );
}

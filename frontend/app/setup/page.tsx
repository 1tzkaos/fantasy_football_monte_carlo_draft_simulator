"use client";

import { createContext, useCallback, useEffect, useState } from "react";
import { Button } from "@nextui-org/button";
import { Code } from "@nextui-org/code";
import { Input } from "@nextui-org/input";
import { Link } from "@nextui-org/link";
import { Progress } from "@nextui-org/progress";
import { Spinner } from "@nextui-org/spinner";
import { useTheme } from "next-themes";

import {
  useCreateLeagueMutation,
  useAddHistoricalDraftsMutation,
  useAddHistoricalPlayersMutation,
  useAddPlayersMutation,
} from "@/api/services/league";
import { title, subtitle } from "@/components/primitives";
import { LeagueSimple } from "@/types";

interface SetupContextType {
  theme: string | undefined;
  progressStep: number;
  isValidationError: boolean;
  isCreationError: boolean;
  isCreated: boolean;
  setLeagueName: (name: string) => void;
  setTeamsFile: (file: File) => void;
  setHistoricalDraftFile: (file: File) => void;
  setPlayersFile: (file: File) => void;
  setHistoricalPlayersFile: (file: File) => void;
}

const SetupContext = createContext<SetupContextType>({
  theme: undefined,
  progressStep: 0,
  isValidationError: false,
  isCreationError: false,
  isCreated: false,
  setLeagueName: () => {},
  setTeamsFile: () => {},
  setHistoricalDraftFile: () => {},
  setPlayersFile: () => {},
  setHistoricalPlayersFile: () => {},
});

export default function SetupPage() {
  const { theme } = useTheme();
  const [progressStep, setProgressStep] = useState<number>(0);
  const [isValidationError, setIsValidationError] = useState<boolean>(false);
  const [isCreationError, setIsCreationError] = useState<boolean>(false);
  const [isCreated, setIsCreated] = useState<boolean>(false);

  // Mutations for creating a new league
  const [createLeague] = useCreateLeagueMutation();
  const [addHistoricalDrafts] = useAddHistoricalDraftsMutation();
  const [addHistoricalPlayers] = useAddHistoricalPlayersMutation();
  const [addPlayers] = useAddPlayersMutation();

  // State to store the inputted name and files
  const [leagueName, setLeagueName] = useState<string | null>(null);
  const [teamsFile, setTeamsFile] = useState<File | null>(null);
  const [historicalDraftFile, setHistoricalDraftFile] = useState<File | null>(
    null,
  );
  const [playersFile, setPlayersFile] = useState<File | null>(null);
  const [historicalPlayersFile, setHistoricalPlayersFile] =
    useState<File | null>(null);

  // Validate for each step that the required fields are filled
  const validateStep = () => {
    switch (progressStep) {
      case 0:
        return leagueName !== null && leagueName !== "";
      case 1:
        return teamsFile !== null;
      case 2:
        return historicalDraftFile !== null;
      case 3:
        return playersFile !== null;
      case 4:
        return historicalPlayersFile !== null;
      default:
        return false;
    }
  };

  // Handle next button click
  const handleNext = useCallback(() => {
    if (validateStep()) {
      setProgressStep(progressStep + 1);
      setIsValidationError(false);
    } else {
      setIsValidationError(true);
    }
  }, [progressStep, validateStep]);

  // Async leauge creation
  const handleCreateLeague = useCallback(async () => {
    const newLeague: LeagueSimple = await createLeague({
      name: leagueName as string,
      teams: teamsFile as File,
    })
      .unwrap()
      .catch(() => {
        setIsCreationError(true);

        return {} as LeagueSimple;
      });

    await addHistoricalDrafts({
      id: newLeague.id,
      drafts: historicalDraftFile as File,
    }).catch(() => {
      setIsCreationError(true);
    });
    await addHistoricalPlayers({
      id: newLeague.id,
      players: historicalPlayersFile as File,
    }).catch(() => {
      setIsCreationError(true);
    });
    await addPlayers({
      id: newLeague.id,
      players: playersFile as File,
    }).catch(() => {
      setIsCreationError(true);
    });
    setIsCreated(true);
  }, [
    createLeague,
    leagueName,
    teamsFile,
    historicalDraftFile,
    historicalPlayersFile,
    playersFile,
  ]);

  // When on the last step, create the league
  useEffect(() => {
    if (progressStep === 5) {
      handleCreateLeague();
    }
  }, [progressStep, handleCreateLeague]);

  // Return the form
  return (
    <section className="flex flex-col items-center justify-center gap-8">
      <div className="max-w-lg text-center">
        <h1 className={title()}>{`Configure settings for a new draft.`}</h1>
        <h2 className={subtitle()}>
          Upload your {`league's`} teams and draft order, player projections,
          and historical draft data. Once your settings are configured,
          {`you'll`} be ready to{" "}
          <Link className={"text-lg lg:text-xl"} href="/draft">
            enter your draft room
          </Link>
          .
        </h2>
      </div>
      <SetupContext.Provider
        value={{
          theme,
          progressStep,
          isValidationError,
          isCreationError,
          isCreated,
          setLeagueName,
          setTeamsFile,
          setHistoricalDraftFile,
          setPlayersFile,
          setHistoricalPlayersFile,
        }}
      >
        {/* Progress bar with color and text for status updates */}
        <Progress
          color={isCreationError ? "danger" : "primary"}
          label={
            isCreationError ? (
              "Error"
            ) : isCreated ? (
              "Success"
            ) : progressStep < 5 ? (
              `Step ${progressStep + 1} of 5`
            ) : (
              <span className="flex items-center">
                <Spinner size="sm" />
                <span className="ml-2">Creating</span>
              </span>
            )
          }
          size="lg"
          value={progressStep * 20}
        />

        {/* Step 1 */}
        {progressStep === 0 && (
          <div className="flex flex-col gap-4 w-full items-center">
            <Input
              className="rounded-full"
              id="league-name"
              label="League Name"
              size="lg"
              variant={theme === "light" ? "faded" : "flat"}
              onChange={(e) => setLeagueName(e.target.value)}
            />
            <p className="text-left w-full">
              Make sure to name your league something unique and memorable.
            </p>
          </div>
        )}

        {/* Step 2 */}
        {progressStep === 1 && (
          <div className="flex flex-col gap-4 w-full items-center">
            <Input
              id="teams-csv"
              label="Teams CSV"
              size="lg"
              type="file"
              variant={theme === "light" ? "faded" : "flat"}
              onChange={(e) => {
                if (!e.target.files) {
                  return;
                } else setTeamsFile(e.target.files[0]);
              }}
            />
            <p className="text-left">
              This CSV file lists the teams in your league and their draft
              order. To see a template of this file, please{" "}
              <Link href="/teams.csv">click here</Link>.
            </p>
          </div>
        )}

        {/* Step 3 */}
        {progressStep === 2 && (
          <div className="flex flex-col gap-4 w-full items-center">
            <Input
              id="historical-drafts-csv"
              label="Historical Drafts CSV"
              size="lg"
              type="file"
              variant={theme === "light" ? "faded" : "flat"}
              onChange={(e) => {
                if (!e.target.files) {
                  return;
                } else setHistoricalDraftFile(e.target.files[0]);
              }}
            />
            <p className="text-left">
              This CSV file records the round-by-round outcomes of previous
              drafts for your league. To see a template of this file, please{" "}
              <Link href="/historical_drafts.csv">click here</Link>.
            </p>
          </div>
        )}

        {/* Step 4 */}
        {progressStep === 3 && (
          <div className="flex flex-col gap-4 w-full items-center">
            <Input
              id="players-csv"
              label="Players CSV"
              size="lg"
              type="file"
              variant={theme === "light" ? "faded" : "flat"}
              onChange={(e) => {
                if (!e.target.files) {
                  return;
                } else setPlayersFile(e.target.files[0]);
              }}
            />
            <p className="text-left">
              This CSV file lists current players and their projected fantasy
              football points. To see a template of this file, please{" "}
              <Link href="/players.csv">click here</Link>.
            </p>
          </div>
        )}

        {/* Step 5 */}
        {progressStep === 4 && (
          <div className="flex flex-col gap-4 w-full items-center">
            <Input
              id="historical-players-csv"
              label="Historical Players CSV"
              size="lg"
              type="file"
              variant={theme === "light" ? "faded" : "flat"}
              onChange={(e) => {
                if (!e.target.files) {
                  return;
                } else setHistoricalPlayersFile(e.target.files[0]);
              }}
            />
            <p className="text-left">
              This CSV file compares {`players'`} projected and actual fantasy
              football points in previous seasons. To see a template of this
              file, please{" "}
              <Link href="/historical_players.csv">click here</Link>.
            </p>
          </div>
        )}

        {/* Creation errors require the user to restart the process */}
        {isCreationError ? (
          <Code color="danger">
            There was an error creating your league. Please try again.
          </Code>
        ) : isCreated ? (
          <>
            <Code color="primary">Your league has been created!</Code>
            <p className="text-left">
              Next step? Visit the <Link href="/draft">draft page</Link>.
            </p>
          </>
        ) : null}

        {/* Next step button */}
        {progressStep < 5 && (
          <div className="flex w-full justify-between">
            <Button size="lg" variant="bordered" onClick={() => handleNext()}>
              Next
            </Button>
            {/* Validation error */}
            {isValidationError && (
              <Code color="danger">Please complete this field.</Code>
            )}
          </div>
        )}
      </SetupContext.Provider>
    </section>
  );
}

"use client";

import { createContext } from "react";
import { button as buttonStyles } from "@nextui-org/theme";
import { Button } from "@nextui-org/button";
import { useTheme } from "next-themes";

import { useGetDraftQuery, useDraftPlayerMutation } from "@/api/services/draft";
import { title, subtitle } from "@/components/primitives";
import { Draft, League, Players } from "@/types";

const positions = ["qb", "rb", "wr", "te", "dst", "k"];

type Position = (typeof positions)[number];
type PositionColorMap = {
  [key in Position]:
    | "primary"
    | "success"
    | "warning"
    | "danger"
    | "secondary"
    | "default";
};

const positionColors: PositionColorMap = {
  qb: "danger",
  rb: "success",
  wr: "primary",
  te: "warning",
  dst: "default",
  k: "secondary",
};

const emptyLeague: League = {
  id: "",
  name: "",
  created: "",
  teams: [],
  players: {
    qb: [],
    rb: [],
    wr: [],
    te: [],
    dst: [],
    k: [],
  },
  current_draft_turn: 0,
};

type DraftIdContextType = {
  draft: Draft;
  theme: string | undefined;
};

const DraftIdContext = createContext<DraftIdContextType>({
  draft: { league: emptyLeague, id: "", created: "" },
  theme: undefined,
});

export default function DraftIdPage({ params }: { params: { id: string } }) {
  const { theme } = useTheme();
  const {
    data: draft = {
      league: emptyLeague,
      id: "",
      created: "",
    },
  } = useGetDraftQuery(params.id);
  const [draftPlayer] = useDraftPlayerMutation();

  // Draft a player with a POST request to '/draft/:id/pick'
  const handleDraftPlayer = async (name: string) => {
    await draftPlayer({ id: draft.id, name });
  };

  return (
    <section className="flex flex-col items-center justify-center gap-8">
      <DraftIdContext.Provider
        value={{
          draft,
          theme,
        }}
      >
        <div className="inline-block text-center justify-center">
          <h1 className={title()}>
            Run{" "}
            <span className={title({ color: "green" })}>
              {`${draft.league.name}'s`}
            </span>{" "}
            draft.
          </h1>
          <h2 className={subtitle()}>
            For each round, select the players chosen by you and your opponents.
            When {`it's`} your turn to pick, a Monte Carlo simulation will help
            you make the best choice.
          </h2>
        </div>

        {/* Use a flex box to display columns of the six positions */}
        <div className="text-center grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
          {positions.map((position) => (
            <div key={position} className="flex flex-col items-center gap-4">
              <h3 className={subtitle()}>{position.toLocaleUpperCase()}</h3>
              <ul className="flex flex-col gap-4 w-full">
                {draft.league.players[position as keyof Players].map(
                  (player, i) => {
                    if (player.drafted === false) {
                      return (
                        <li key={i}>
                          <Button
                            className={
                              buttonStyles({
                                size: "lg",
                                // fullWidth: true,
                                variant: "solid",
                                color:
                                  positionColors[
                                    position as keyof PositionColorMap
                                  ],
                              }) +
                              ` h-fit w-full flex flex-col gap-1 py-4 ${
                                theme === "dark"
                                  ? " text-white "
                                  : " text-black "
                              } `
                            }
                            onClick={() => handleDraftPlayer(player.name)}
                          >
                            <p className="font-bold">{player.name}</p>
                            <p>
                              {player.nfl_team} |{" "}
                              {player.position_tier.toLocaleUpperCase()}
                            </p>
                          </Button>
                        </li>
                      );
                    }
                  },
                )}
              </ul>
            </div>
          ))}
        </div>
      </DraftIdContext.Provider>
    </section>
  );
}

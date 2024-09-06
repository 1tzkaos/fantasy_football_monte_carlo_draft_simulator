import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type LeagueSimple = {
  id: string;
  name: string;
  created: string;
};

export type DraftSimple = {
  id: string;
  created: string;
};

export type Player = {
  name: string;
  position: string;
  nfl_team: string;
  drafted: boolean;
  position_tier: string;
};

export type Players = {
  qb: Player[];
  rb: Player[];
  wr: Player[];
  te: Player[];
  dst: Player[];
  k: Player[];
};

export type Team = {
  name: string;
  owner: string;
  simulator: boolean;
};

// Expand the LeagueSimple type to include the teams and players
export type League = LeagueSimple & {
  teams: Team[];
  players: Players;
  draft_order: number[];
  current_draft_turn: number;
};

// Expand the DraftSimple type to include the league
export type Draft = DraftSimple & {
  league: League;
};

export type MonteCarloResults = {
  qb: number;
  rb: number;
  wr: number;
  te: number;
  dst: number;
  k: number;
  iterations: number;
};

// Draft results are just an object of each team name with a number (score) as value
export type DraftResults = Record<string, number>;

import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type LeagueSimple = {
  id: string;
  name: string;
  created: string;
};

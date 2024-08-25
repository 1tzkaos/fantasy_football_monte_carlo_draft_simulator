import { SVGProps } from "react";

export type IconSvgProps = SVGProps<SVGSVGElement> & {
  size?: number;
};

export type DraftSettings = {
  id: string;
  name: string;
  created: string;
};

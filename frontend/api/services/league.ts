import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { baseQuery } from "@/api/services/base";
import { LeagueSimple } from "@/types";

// Operations for querying the list of available leagues
// and creating a new league
export const leagueApi = createApi({
  reducerPath: "leagueApi",
  baseQuery: fetchBaseQuery(baseQuery),
  endpoints: (builder) => ({
    getLeagues: builder.query<LeagueSimple[], string>({
      query: () => ``,
    }),
  }),
});

export const { useGetLeaguesQuery } = leagueApi;

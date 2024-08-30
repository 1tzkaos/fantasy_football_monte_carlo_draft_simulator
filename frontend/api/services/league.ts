import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { baseQuery } from "@/api/services/base";
import { DraftSimple, LeagueSimple } from "@/types";

// Url for all league operations
const leagueUrl = "/league";

// Operations for querying the list of available leagues
// and creating a new league
export const leagueApi = createApi({
  reducerPath: "leagueApi",
  baseQuery: fetchBaseQuery(baseQuery),
  endpoints: (builder) => ({
    getLeagues: builder.query<LeagueSimple[], string>({
      query: () => leagueUrl,
    }),

    // To create a draft for a league, we need to send a POST request to
    // '/league/:id/draft'
    createDraft: builder.mutation<DraftSimple, { id: string }>({
      query: ({ id }) => ({
        url: `${leagueUrl}/${id}/draft`,
        method: "POST",
      }),
    }),

    // To create a league, we need to send a POST request to '/league'
    // with all of the teams data, which is required
    createLeague: builder.mutation<LeagueSimple, { name: string; teams: File }>(
      {
        query: ({ name, teams }) => {
          var bodyFormData = new FormData();

          bodyFormData.append("contentType", teams.type);
          bodyFormData.append("file", teams);

          return {
            url: leagueUrl,
            method: "POST",
            params: {
              name,
            },
            body: bodyFormData,
          };
        },
      },
    ),

    // Players are added from a file POSTed to '/league/:id/player'
    addPlayers: builder.mutation<void, { id: string; players: File }>({
      query: ({ id, players }) => {
        var bodyFormData = new FormData();

        bodyFormData.append("contentType", players.type);
        bodyFormData.append("file", players);

        return {
          url: `${leagueUrl}/${id}/player`,
          method: "POST",
          body: bodyFormData,
        };
      },
    }),

    // Historical players are added from a file POSTed to '/league/:id/historical_player'
    addHistoricalPlayers: builder.mutation<
      void,
      {
        id: string;
        players: File;
      }
    >({
      query: ({ id, players }) => {
        var bodyFormData = new FormData();

        bodyFormData.append("contentType", players.type);
        bodyFormData.append("file", players);

        return {
          url: `${leagueUrl}/${id}/historical_player`,
          method: "POST",
          body: bodyFormData,
        };
      },
    }),

    // Historical drafts are added from a file POSTed to '/league/:id/historical_draft'
    addHistoricalDrafts: builder.mutation<
      void,
      {
        id: string;
        drafts: File;
      }
    >({
      query: ({ id, drafts }) => {
        var bodyFormData = new FormData();

        bodyFormData.append("contentType", drafts.type);
        bodyFormData.append("file", drafts);

        return {
          url: `${leagueUrl}/${id}/historical_draft`,
          method: "POST",
          body: bodyFormData,
        };
      },
    }),
  }),
});

export const {
  useGetLeaguesQuery,
  useCreateDraftMutation,
  useCreateLeagueMutation,
  useAddPlayersMutation,
  useAddHistoricalDraftsMutation,
  useAddHistoricalPlayersMutation,
} = leagueApi;

import { createApi, fetchBaseQuery } from "@reduxjs/toolkit/query/react";

import { baseQuery } from "@/api/services/base";
import { Draft, MonteCarloResults } from "@/types";

// Url for all draft operations
const draftUrl = "/draft";

// Operations for querying the data of a draft
export const draftApi = createApi({
  reducerPath: "draftApi",
  baseQuery: fetchBaseQuery(baseQuery),
  tagTypes: ["Draft", "MonteCarloResults"],
  endpoints: (builder) => ({
    getDraft: builder.query<Draft, string>({
      query: (id) => `${draftUrl}/${id}`,
      providesTags: ["Draft"],
    }),

    // Mutation for drafting a player with a POST request to '/draft/:id/pick'
    draftPlayer: builder.mutation<void, { id: string; name: string }>({
      query: ({ id, name }) => ({
        url: `${draftUrl}/${id}/pick`,
        method: "POST",
        params: {
          name,
        },
      }),
      invalidatesTags: ["Draft"],
    }),

    // Monte Carlo simulation for drafting players
    runMonteCarlo: builder.mutation<MonteCarloResults, { id: string }>({
      query: ({ id }) => ({
        url: `${draftUrl}/${id}/monte_carlo`,
        method: "POST",
      }),
      invalidatesTags: ["MonteCarloResults"],
    }),
  }),
});

export const {
  useGetDraftQuery,
  useDraftPlayerMutation,
  useRunMonteCarloMutation,
} = draftApi;

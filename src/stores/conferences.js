import { create } from "zustand";
import { devtools } from "zustand/middleware";
import conferencesService from "../services/ConferenceService";

const useConferenceStore = create(
   devtools((set) => ({
     conferenceSingle: null,
     conferences: [],
     isLoading: false,
     error: "",
     fetchConferences: async (filter="") => {
       try {
         set({ isLoading: true });
         const response = await conferencesService.fetchConferences(filter);
         set({ conferences: response});
       } catch (error) {
         set({ error: error.message });
       } finally {
         set({ isLoading: false });
       }
     },

     fetchConferenceSingle: async (id) => {
        try {
          set({ isLoading: true });
          const response = await conferencesService.fetchConferenceById(id);
          set({ conferenceSingle: response});
        } catch (error) {
          set({ error: error.message });
        } finally {
          set({ isLoading: false });
        }
     }
   //   setConferences: async (conferences) => {
   //     console.log(conferences);
   //     try {
   //       set({ isLoading: true });
   //       set({ conferences: conferences });
   //       // const response = await conferenceservice.setconferences(settings);
   //     } catch (error) {
   //       set({ error: error.message });
   //     } finally {
   //       set({ isLoading: false });
   //     }
   //   },
   }))
 );
 
 export default useConferenceStore;
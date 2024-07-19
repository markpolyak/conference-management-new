import { create } from "zustand";
import { devtools } from "zustand/middleware";
import applicationsService from "../services/ApplicationService";

const useApplicationStore = create(
   devtools((set) => ({
     applicationSingle: null,
     applications: [],
     isLoading: false,
     error: "",
     fetchApplications: async (id, email="123@mail.ru") => {
       try {
         set({ isLoading: true });
         const response = await applicationsService.fetchApplications(id, email);
         set({ applications: response});
       } catch (error) {
         set({ error: error.message });
       } finally {
         set({ isLoading: false });
       }
     },

          
    addApplication: async (application) => {
        try {
          set({ isLoading: true });
          // const response = await applicationsService.addApplication(application);
          set((state) => ({applications: [...state.applications, application]}))
        } catch (error) {
          set({ error: error.message });
        } finally {
          set({ isLoading: false });
        }
    },
     
    editApplication: async (application) => {
      try {
        set({ isLoading: true });
        const response = await applicationsService.editApplication(application);
        set({ applicationSingle: response});
      } catch (error) {
        set({ error: error.message });
      } finally {
        set({ isLoading: false });
      }
   },

    //  fetchApplicationSingle: async (id) => {
    //     try {
    //       set({ isLoading: true });
    //       const response = await applicationsService.fetchApplicationById(id);
    //       set({ applicationSingle: response});
    //     } catch (error) {
    //       set({ error: error.message });
    //     } finally {
    //       set({ isLoading: false });
    //     }
    //  },

     deleteApplication: (id) => {
        try {
          set((state) => ({applications: state.applications.filter((application) => application.id !== id)}))
        } catch (error) {
          set({ error: error.message });
        } finally {
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
 
 export default useApplicationStore;
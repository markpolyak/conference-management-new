import React, { useEffect } from 'react';
import classes from "./ConferenceIdPage.module.scss";
import Conference from '../../components/elements/Conference/Conference';
import { useParams } from 'react-router-dom';
import useConferenceStore from '../../stores/conferences';
import ApplicationPreviewList from '../../components/elements/ApplicationPreviewList/ApplicationPreviewList';
import useApplicationStore from '../../stores/applications';
import useAuthStore from '../../stores/auth';

export default function ConferenceIdPage() {
   const {fetchConferenceSingle } = useConferenceStore((state) => ({
      fetchConferenceSingle: state.fetchConferenceSingle,
    }));

    const {  applications, fetchApplications } = useApplicationStore((state) => ({
      fetchApplications: state.fetchApplications,
      applications: state.applications,
    }));

    const {  user } = useAuthStore((state) => ({
      user: state.user,
    }));

   const params = useParams();


   async function fetchAnimeById() {
      if (params.id !== "undefined" && params.id !== "null") {
         const id = Number(params.id);

         await fetchConferenceSingle(id);

         if (applications.length === 0 || ((fetchConferenceSingle.id !== id) && applications.length ===3)) {
            await fetchApplications(id, user.email);
         }
        
         // await fetch
      }
   };

   useEffect(() => {
      fetchAnimeById();
   }, [])

  return (
    <main className={classes.main}>
         <Conference/>
         <ApplicationPreviewList/>
    </main>
  )
}

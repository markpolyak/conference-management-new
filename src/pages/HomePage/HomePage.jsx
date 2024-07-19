import {useEffect} from 'react';
import classes from "./HomePage.module.scss";
import ConferenceList from '../../components/elements/ConferenceList/ConferenceList';
import useConferenceStore from '../../stores/conferences';

export default function HomePage() {
   const {fetchConferences } = useConferenceStore((state) => ({
      fetchConferences: state.fetchConferences,
    }));

    useEffect(() => {
      fetchConferences();
    }, [])

  return (
    <main className={classes.main}>
         <ConferenceList/>
    </main>
  )
}

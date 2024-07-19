import React from 'react';
import classes from "./ApplicationPage.module.scss";
import ApplicationForm from '../../components/elements/ApplicationForm/ApplicationForm';

export default function ApplicationPage() {
  return (
    <main className={classes.main}>
         <ApplicationForm/>
    </main>
  )
}

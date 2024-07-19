import React from 'react';
import classes from "./ApplicationEditPage.module.scss";
import ApplicationEditForm from '../../components/elements/ApplicationEditForm/ApplicationEditForm';

export default function ApplicationEditPage() {
  return (
    <main className={classes.main}>
         <ApplicationEditForm/>
    </main>
  )
}

import React from 'react';
import classes from "./ApplicationPreviewList.module.scss";
import ApplicationPreview from '../ApplicationPreview/ApplicationPreview';
import useApplicationStore from '../../../stores/applications';
import useAuthStore from '../../../stores/auth';

export default function ApplicationPreviewList() {
  const {applications } = useApplicationStore((state) => ({
    applications: state.applications,
  }));

  const {isAuth } = useAuthStore((state) => ({
    isAuth: state.isAuth,
  }));

  return (
    <div className={classes["app-list"]}>
      <div className='_wrapper'>
        <h2 className={classes["app-list__title"]}>Список ранее поданных заявок:</h2>
        <div className={classes["app-list__container"]}>
          {
            applications.length > 0 && isAuth
              ?
                applications.map((application, index) =>
                  <ApplicationPreview application={application} key={index}/>
                )
              :
                <h3 className={classes["app-list__empty"]}>Заявки отсутствуют!</h3>
          }
        </div>
      </div>
    </div>
  )
}

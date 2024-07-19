import React from 'react';
import classes from "./Conference.module.scss";
import useConferenceStore from '../../../stores/conferences';
import { useNavigate, useParams} from 'react-router-dom';
import { checkDateRange } from '../../../utils/utils';
import useAuthStore from '../../../stores/auth';

export default function Conference() {
   const {conferenceSingle } = useConferenceStore((state) => ({
      conferenceSingle: state.conferenceSingle,
    }));

    const {isAuth } = useAuthStore((state) => ({
      isAuth: state.isAuth,
    }));

    const params = useParams();

    const navigate = useNavigate();

    if (!conferenceSingle) return <></>

  return (
    <div className={classes.conference}>
         <div className='_wrapper'>
            <div className={classes.conference__container}>
               <div className={classes.body__bg}></div>
               <p className={classes.conference__title}>
               {conferenceSingle && conferenceSingle.name_rus}
               </p>
               <p className={classes.conference__title_short}>
               {conferenceSingle && conferenceSingle.name_rus_short}
               </p>

               <div className={classes.conference__info}>
                  <p className={classes.conference__organizer}>
                     <span>Организатор:</span> <span>{conferenceSingle && conferenceSingle.organized_by}</span>
                  </p>
                  <p className={classes.conference__organizer}>
                     <span>Дата начала регистрации:</span> <span>{conferenceSingle && conferenceSingle.registration_start_date}</span>
                  </p>
                  <p className={classes.conference__organizer}>
                     <span>Дата окончания регистрации:</span> <span>{conferenceSingle && conferenceSingle.registration_end_date}</span>
                  </p>
                  <p className={classes.conference__email}>
                     <span>Email:</span> <span>{conferenceSingle && conferenceSingle.email}</span>
                  </p>


                  <p className={classes.conference__organizer}>
                     <span>Дата начала подачи докладов:</span> <span>{conferenceSingle && conferenceSingle.submission_start_date}</span>
                  </p>
                  <p className={classes.conference__organizer}>
                     <span>Дата окончания подачи докладов:</span> <span>{conferenceSingle && conferenceSingle.submission_end_date}</span>
                  </p>


                

                  <p className={classes.conference__organizer}>
                     <span>Дата начала конференции:</span> <span>{conferenceSingle && conferenceSingle.registration_end_date}</span>
                  </p>
                  <p className={classes.conference__organizer}>
                     <span>Дата окончания конференции:</span> <span>{conferenceSingle && conferenceSingle.registration_end_date}</span>
                  </p>
                  <p className={classes.conference__url}>
                     <span>Сайт:</span> <span><a href={conferenceSingle && conferenceSingle.url}>{conferenceSingle && conferenceSingle.url}</a></span>
                  </p>

               </div>

               {
                  isAuth &&
                  <div>
                     {
                      checkDateRange(conferenceSingle.registration_start_date, conferenceSingle.registration_end_date)
                     ? <button className={classes.conference__btn} onClick={() => navigate(`/conference/${params.id}/application`)}>Подать заявку</button>
                     : <p className={classes.conference__alert}>Прием заявок на конференцию завершен</p>
                  }
                  </div>
               
               }
               
            </div>
         </div>
    </div>
  )
}

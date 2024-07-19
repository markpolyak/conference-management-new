import {useState} from 'react';
import classes from "./ApplicationPreview.module.scss";
import useApplicationStore from '../../../stores/applications';
import useConferenceStore from '../../../stores/conferences';
import { formatDateTime } from '../../../utils/utils';
import { MdModeEdit } from "react-icons/md";
import { MdDelete } from "react-icons/md";
import ModalWindow from '../../UI/ModalWindow/ModalWindow';
import ApplicationEditForm from '../ApplicationEditForm/ApplicationEditForm';
import { useNavigate, useParams } from 'react-router-dom';
import { checkDateRange } from '../../../utils/utils';


export default function ApplicationPreview({application}) {
   const {conferenceSingle } = useConferenceStore((state) => ({
      conferenceSingle: state.conferenceSingle,
    }));
    const {deleteApplication } = useApplicationStore((state) => ({
      deleteApplication: state.deleteApplication,
    }));

    const navigate = useNavigate();
    const params = useParams();

    const [modalVisible, setModalVisible] = useState(false);

    function showButton() {
      if (checkDateRange(conferenceSingle.registration_start_date, conferenceSingle.registration_end_date) || (checkDateRange(conferenceSingle.submission_start_date, conferenceSingle.submission_end_date))) {
         return true;
      }

      return false;
    }



  return (
    <article className={classes.application}>
      <div className={classes.application__header}>
         <h4 className={classes.application__title}>Заявка на конференцию: {conferenceSingle && conferenceSingle.name_rus_short}</h4>
      </div>
    
      <div className={classes.application__body}>
         <div className={classes.application__fio}>
            <div className={classes.application__name}>
               <span>Имя:</span> <span>{application && (application.name || "-")}</span>
            </div>
            <div className={classes.application__surname}>
               <span>Фамилия:</span> <span>{application && (application.surname || "-")}</span>
            </div>
            <div className={classes.application__patronymic}>
               <span>Отчество:</span> <span>{application && (application.patronymic || "-")}</span>
            </div>
         </div>
         <div className={classes.application__contacts}>
            <div className={classes.application__email}>
               <span>Email:</span> <span>{application && (application.email || "-")}</span>
            </div>
            <div className={classes.application__phone}>
               <span>Phone:</span> <span>{application && (application.phone || "-")}</span>
            </div>
         </div>
         <div className={classes.application__dates}>
            <div className={classes.application__submitted}>
                  <span>Дата подачи:</span> <span>{application && (formatDateTime(application.submitted_at) || "-")}</span>
            </div>
            <div className={classes.application__updated}>
                  <span>Дата редактирования:</span> <span>{application && (formatDateTime(application.updated_at) || "-")}</span>
            </div>
         </div>
      </div>
      <div className={classes.application__footer}>
         {showButton() && <button className={[classes.application__btn, classes.application__btn_blue].join(" ")} onClick={() => navigate(`/conference/${params.id}/applications/${application.id}`)}><MdModeEdit />Изменить</button>}
         <button className={[classes.application__btn, classes.application__btn_red].join(" ")} onClick={() => deleteApplication(application.id)}><MdDelete />Удалить</button>
      </div>
{/*    
      <ApplicationEditForm/> */}

    </article>
  )
}

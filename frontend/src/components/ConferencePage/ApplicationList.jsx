import React, { useContext, useEffect, useState } from 'react'
import Application from './Application'
import s from './Conference.module.css'
import { Button, Spin } from 'antd'
import { UserContext } from '../../App'
import { useParams } from 'react-router-dom'
import PostService from '../../API/PostService'
import AddApplic from './AddApplic'
import { checkDate } from '../../utils/checkDate'

const ApplicationList = ({conference}) => {

    const {authData} = useContext(UserContext);
    const {conference_id} = useParams();

    const [isOpen, setIsOpen] = useState(false);
    const [applications, setApplications] = useState([]);

    const [correctDate, setCorrectDate] = useState(false);

    const sendData = async () => {
        try {
            const response = await PostService.postApplication(conference_id, applicData);
        } catch (error) {
            console.log('НЕТ БЭКЭНДА')
        }
        finally {
            setApplications([...applications, {
                ...applicData, 
                id: applications.length+1,
                submitted_at: new Date(),
                updated_at: new Date()
            }]);
        }
    }

    const fetchApplications = async () => {
        const response = await PostService.getApplications(conference_id, {email:authData});

        setApplications(response);
    }

    const changeApplication = async (newApplication) => {
        try {
            const response = await PostService.patchApplication(conference_id, newApplication);
        } catch (error) {
            console.log('НЕТ БЕКЭНДА')
        }
        finally {
            setApplications([...applications.map(i => i.id === newApplication.id ? newApplication : i)]);
        }
    }

    const deleteApplication = async (application) => {
        try {
            const response = await PostService.deleteApplication(conference_id, application);
        } catch (error) {
            console.log('НЕТ БЭКЭНДА')
        }
        finally {
            setApplications([...applications.filter(i => i.id !== application.id ? i : null)]);
        }
    }

    const showModal = () => setIsOpen(true);

    useEffect(() => {
        fetchApplications();
        if (conference)
            setCorrectDate(checkDate(conference.registration_start_date, conference.registration_end_date))
    }, [conference_id, conference])

    const [applicData, setApplicData] = useState({
        title: "", 
        telegram_id: "", //
        discord_id: "", //
        email: "", 
        phone: "", //
        name: "", 
        surname: "", 
        patronymic: "", 
        university: "", 
        student_group: "", //
        applicant_role: "", 
        adviser: "", 
        coauthors: [] //
    })

    return (
        !conference
        ?<Spin/>
        :
        <>
            <div>
                <div className={s.titleBlock}>
                    <h2 className={s.title}>Заявки</h2>
                    {
                        correctDate
                        ?
                        <Button onClick={showModal}>Подать заявку</Button>
                        : <></>
                    }
                </div>
                <div className={s.applicationList}>

                    {
                        applications.length 
                        ? applications.map((item) => <Application key={item.id} conference={conference} application={item} changeApplication={changeApplication} deleteApplication={deleteApplication} correctDate={correctDate}/>)
                        : <h3>Заявок нет!</h3>
                    }
                </div>            
            </div>
            <AddApplic isOpen={isOpen} setIsOpen={setIsOpen} applicData={applicData} setApplicData={setApplicData} conference={conference} sendData={sendData}/>
        </>
    )
}

export default ApplicationList
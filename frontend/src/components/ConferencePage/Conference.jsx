import React, { useContext, useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import PostService from '../../API/PostService';
import s from './Conference.module.css'
import Header from '../Header/Header';
import ApplicationList from './ApplicationList';
import { UserContext } from '../../App';
import { Spin } from 'antd';

const Conference = () => {

    const {conference_id} = useParams();
    const [conference, setConference] = useState();
    const {authData} = useContext(UserContext);

    const fetchConferenceData = async () => {
        const response = await PostService.getConference(conference_id);

        setConference(response[0]);
    }

    useEffect(() => {
        fetchConferenceData();
    }, [conference_id])

    return (
        <>
            <Header/>
            {
                !conference
                ? <Spin/>
                :
                <div className={s.container}>
                    <div className={s.titleBlock}>
                        <h2 className={s.title}>{conference.name_rus}</h2>
                        <a href={conference.url} target='_blank' rel='noreferrer' className={s.urlBlock}>{conference.url}</a>
                    </div>
                    <h3>Информация</h3>
                    <div className={s.informBlock}>
                        <div className={s.informData}><span className={s.leftBlock}>Почта</span> <span>{conference.email}</span></div>
                        <div className={s.informData}><span className={s.leftBlock}>Организация</span> <span>{conference.organized_by}</span></div>
                    </div>
                    <h3>Даты</h3>
                    <div className={s.dateBlock}>
                        <div className={s.dateItem}>
                            <span>Конференция</span>
                            <span>Начало: {conference.conf_start_date}</span>
                            <span>Конец: {conference.conf_end_date}</span>                        
                        </div>
                        <div className={s.dateItem}>
                            <span>Приём заявок</span>
                            <span>Начало: {conference.registration_start_date}</span>
                            <span>Конец: {conference.registration_end_date}</span>
                        </div>
                        <div className={s.dateItem}>
                            <span>Приём докладов</span>
                            <span>Начало: {conference.submission_start_date}</span>
                            <span>Конец: {conference.submission_end_date}</span>
                        </div>
                    </div>
                </div>
            }

            {
                authData ?
                <div className={s.container}>
                    <ApplicationList conference={conference}/>
                </div>
                : <></>
            }
                 
        </>
    )
}

export default Conference
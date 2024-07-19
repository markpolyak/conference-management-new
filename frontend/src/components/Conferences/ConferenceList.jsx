import React, { useState, useEffect } from 'react'
import PostService from '../../API/PostService';
import ConferenceItem from './ConferenceItem';
import s from './Conferences.module.css';
import Header from '../Header/Header';
import { Select } from 'antd';

const ConferenceList = () => {
    
    const [conferences, setConferences] = useState([]);
    const [filter, setFilter] = useState('all');

    const fetchData = async () => {
        const response = await PostService.getConferences(filter);
        setConferences(response);
    }

    useEffect(() => {
        fetchData();
    }, [filter])

    return (
        <>
            <Header/>
            <div>
                <Select
                    defaultValue={'all'}
                    className={s.select}
                    onChange={value => setFilter(value)}
                    options={[
                        {value:'all', label:'Все'},
                        {value:'active', label:'Активные'},
                        {value:'past', label:'Прошедшие'},
                        {value:'future', label:'Будущие'},
                ]}/>
            </div>
            <div className={s.listContainer}>
                {conferences.map(item => <ConferenceItem className={s.conferenceItem} key={item.id} conference={item}/>)}
            </div>        
        </>

    )
}

export default ConferenceList
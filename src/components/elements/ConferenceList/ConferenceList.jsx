import React, { useEffect, useState } from 'react';
import classes from "./ConferenceList.module.scss";
import ConferenceCard from '../ConferenceCard/ConferenceCard';
import MyButton from '../../UI/MyButton/MyButton';
import useConferenceStore from '../../../stores/conferences';
import { useNavigate } from 'react-router-dom';

export default function ConferenceList() {
   const { conferences, fetchConferences} = useConferenceStore((state) => ({
      conferences: state.conferences,
      fetchConferences: state.fetchConferences,
    }));

    const [currentIndex, setCurrentIndex] = useState(1);

    const navigate = useNavigate();

    const buttons = [
      {value: "Все", filter: "all"},
      {value: "Активные", filter: "active"},
      {value: "Прошлые", filter: "past"},
      {value: "Будущие", filter: "future"}
    ]

    function handleClick(index, filter) {
      setCurrentIndex(index);
      fetchConferences(filter)
    }

   //  useEffect(() => {
   //    setCurrentIndex(1);
   //  }, [])

   return (
      <div className={classes.conferences}>
            <div className='_wrapper'>
               <h2 className={classes.conferences__title}>Список Конференций</h2>
               <div className={classes.conferences__buttons}>
                  {buttons.map((button, index) =>
                      <MyButton value={button.value} isActive={index === currentIndex} onClick={e => handleClick(index, button.filter)} key={index}/>
                  )}
                  {/* <MyButton value="Все"/>
                  <MyButton value="Активные" isActive={true}/>
                  <MyButton value="Прошлые"/>
                  <MyButton value="Будущие"/> */}
               </div>
            
               <div className={classes.conferences__container}>
                  {conferences.map((conference, index) =>
                     <ConferenceCard conference={conference} key={index}/>
                  )}
               </div>
            </div>
      </div>
   )
}

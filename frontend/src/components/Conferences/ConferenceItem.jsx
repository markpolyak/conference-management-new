import React from 'react'
import s from './Conferences.module.css'
import { Link } from 'react-router-dom'

const ConferenceItem = ({conference, className}) => {
    return (
      <Link to={`/conference/${conference.id}`} className={className}>
        <h3>{conference.name_rus_short}</h3>
        <div className={s.dateBlock}>
          <span>Начало: {new Date(conference.conf_start_date).toLocaleString()}</span>
          <span>Конец: {new Date(conference.conf_end_date).toLocaleString()}</span>
        </div>
      </Link>
    )
}

export default ConferenceItem
import React, {useState} from 'react'
import s from './Conference.module.css'
import EditApplic from './EditApplic'
import { Button } from 'antd'


const Application = ({application, changeApplication, deleteApplication, correctDate, conference}) => {

    const [isOpen, setIsOpen] = useState(false);
    const showModal = () => setIsOpen(true);
    const deleteData = () => deleteApplication(application)

    const data = [
        {title: 'Автор', text: `${application.surname} ${application.name} ${application.patronymic}`},
        {title: 'Группа', text: application.student_group},
        {title: 'Роль', text: application.applicant_role},
        {title: 'Номер телефона', text: application.phone},
        {title: 'Почта',text:application.email},
        {title: 'Телеграм',text:application.telegram_id},
        {title: 'Дискорд',text:application.discord_id},
        {title: 'Консультант', text: application.adviser},
        {title: 'Соавторы', text: <div>{application.coauthors.map((i,idx) => <div key={`${application.id} ${idx}`}>{idx+1}) {i.surname} {i.name} {i.patronymic} {i.email}</div>)}</div>}
    ]

    return (
        <>
           <div className={s.applicationItem}>
                <div>
                    <div className={s.applicationTitle}>
                        <div>{application.title}</div>
                        {
                            correctDate
                            ?
                            <div className={s.editButtons}>
                                <Button size='small' onClick={showModal}>Изменить</Button>
                                <Button size='small' onClick={deleteData}>Удалить</Button>
                            </div>
                            :<>
                                <Button size='small' onClick={deleteData}>Удалить</Button>
                            </>                        
                        }
                    </div>
                    <div className={s.applicationItemBlock}><span className={s.applicationItemTitle}>Доклад</span>{application.file ? <a className={s.anchorFile} href={URL.createObjectURL(application.file)}>{application.file.name}</a> : '-'}</div>
                    {
                        data.map((item, idx) => <div key={`${application.id} ${idx}`} className={s.applicationItemBlock}><span className={s.applicationItemTitle}>{item.title}</span>{item.text ? item.text : '-'}</div>)
                    }                
                </div>
                <div className={s.applicationDateBlock}>
                    <div>Добавлена: {new Date(application.submitted_at).toLocaleString()}</div>
                    <div>Обновлена: {new Date(application.updated_at).toLocaleString()}</div>
                </div>
            </div>

            <EditApplic application={application} isOpen={isOpen} setIsOpen={setIsOpen} changeData={changeApplication} conference={conference}/>
        </>
    )
}

export default Application
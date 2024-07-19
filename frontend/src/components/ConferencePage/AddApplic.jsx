import React, { useEffect, useRef, useState } from 'react'
import { Button, Input, Modal } from 'antd'
import s from './Conference.module.css'
import { isApplicationCorrect } from '../../utils/ApplicationCheck'
import { checkDate } from '../../utils/checkDate'

const AddApplic = ({isOpen, setIsOpen, applicData, setApplicData, sendData, conference}) => {

    useEffect(() => {
        setIsCorrect(isApplicationCorrect(applicData))
    }, [applicData])

    const [isCorrect, setIsCorrect] = useState(false);
    const myRef = useRef(null);

    const handleChange = () => {
        myRef.current.click();
    }

    const fileChange = (e) => {
        setApplicData({...applicData, file: e.target.files[0]})
    }

    const onOk = () => {
        sendData();
        setIsOpen(false);
        setApplicData({
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
            coauthors: [],//
            file:null
        })
    }
    const onCancel = () => {
        setIsOpen(false);
        setApplicData({
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
            coauthors: [],//
            file: null
        })
    }

    const addCoauthorCount = () => {
        setApplicData({...applicData, coauthors: [...applicData.coauthors, {name:"", surname:"", patronymic:"", email:""}]});
    }

    const deleteCoauthor = () => {
        setApplicData({...applicData, coauthors: [...(applicData.coauthors.slice(0, applicData.coauthors.length-1))]})
    }

    return (
        <Modal
            open={isOpen}
            onOk={onOk}
            onCancel={onCancel}
            okText="Подать"
            cancelText="Отмена"
            title="Подать заявку"
            className={s.modal}
            footer={[
                <Button key='back' onClick={onCancel}>Отмена</Button>,
                <Button type='primary' key='enter' onClick={onOk} disabled={!isCorrect}>Подать</Button>
            ]}
        >
            <Input placeholder='Название заявки...*' value={applicData.title} onChange={(e) => setApplicData({...applicData, title: e.target.value})}></Input>

            {
                checkDate(conference.submission_start_date, conference.submission_end_date)
                ?
                <div>
                    <input className={s.filePicker} type='file' accept='.doc,.docx' ref={myRef} onChange={fileChange}/>
                    <Button onClick={handleChange}>Загрузить файл</Button>
                    {
                        applicData.file
                        ? <a className={s.uploadText} href={URL.createObjectURL(applicData.file)}>{applicData.file.name}</a>
                        : <span className={s.uploadText}>Загрузите файл</span>
                    }
                </div>
                :
                <></>  
            }


            <h2 className={s.formTitle}>Автор</h2>
            <Input placeholder='Имя...*' value={applicData.name} onChange={(e) => setApplicData({...applicData, name: e.target.value})}></Input>
            <Input placeholder='Фамилия...*' value={applicData.surname} onChange={(e) => setApplicData({...applicData, surname: e.target.value})}></Input>
            <Input placeholder='Отчество...*' value={applicData.patronymic} onChange={(e) => setApplicData({...applicData, patronymic: e.target.value})}></Input>
            <Input placeholder='Университет...*' value={applicData.university} onChange={(e) => setApplicData({...applicData, university: e.target.value})}></Input>
            <Input placeholder='Группа...' value={applicData.student_group} onChange={(e) => setApplicData({...applicData, student_group: e.target.value})}></Input>
            <Input placeholder='Роль...*' value={applicData.applicant_role} onChange={(e) => setApplicData({...applicData, applicant_role: e.target.value})}></Input>
            
            <h2 className={s.formTitle}>Связь</h2>
            <Input placeholder='Телеграм...' value={applicData.telegram_id} onChange={(e) => setApplicData({...applicData, telegram_id: e.target.value})}></Input>
            <Input placeholder='Дискорд...' value={applicData.discord_id} onChange={(e) => setApplicData({...applicData, discord_id: e.target.value})}></Input>
            <Input placeholder='Почта...*' value={applicData.email} onChange={(e) => setApplicData({...applicData, email: e.target.value})}></Input>
            <Input placeholder='Номер телефона...' value={applicData.phone} onChange={(e) => setApplicData({...applicData, phone: e.target.value})}></Input>

            <Input placeholder='Консультант*' value={applicData.adviser} onChange={(e) => setApplicData({...applicData, adviser: e.target.value})}></Input>

            <div className={s.coauthorsBlock}>
                <h2 className={s.formTitle}>Соавторы</h2>
                <div>
                    <Button className={s.button} onClick={() => addCoauthorCount()}>+</Button><span className={s.count}>{applicData.coauthors.length}</span><Button className={s.button} onClick={() => deleteCoauthor()}>-</Button>
                </div>
            </div>
            <div>
                {applicData.coauthors.map((i,idx) => <div className={s.coauthorInputs} key={idx}><span className={s.coauthorIndex}>{idx+1})</span>
                    <Input placeholder='Имя...' value={i.name} onChange={e => {
                        let temp = [...applicData.coauthors];
                        temp[idx].name = e.target.value;
                        setApplicData({...applicData, coauthors:[...temp]});
                    }}></Input>
                    <Input placeholder='Фамилия...' value={i.surname} onChange={e => {
                        let temp = [...applicData.coauthors];
                        temp[idx].surname = e.target.value;
                        setApplicData({...applicData, coauthors:[...temp]});
                    }}></Input>
                    <Input placeholder='Отчество...' value={i.patronymic} onChange={e => {
                        let temp = [...applicData.coauthors];
                        temp[idx].patronymic = e.target.value;
                        setApplicData({...applicData, coauthors:[...temp]});
                    }}></Input>
                    <Input placeholder='Почта...' value={i.email} onChange={e => {
                        let temp = [...applicData.coauthors];
                        temp[idx].email = e.target.value;
                        setApplicData({...applicData, coauthors:[...temp]});
                    }}></Input>
                </div>)}
            </div>

            <span className={s.text}>* - поля, обязательные для заполнения</span>
        </Modal>
    )
}

export default AddApplic
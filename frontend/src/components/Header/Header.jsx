import React, { useContext, useEffect, useState } from 'react'
import s from './Header.module.css'
import { Link } from 'react-router-dom'
import { Button, Input, Modal } from 'antd'
import { UserContext } from '../../App'
import { regEmail } from '../../utils/regulars'

const Header = () => {

  const [isOpen, setIsOpen] = useState(false);
  const [emailInput, setEmailInput] = useState('');
  const {authData, setAuthData} = useContext(UserContext);
  const [buttonText, setButtonText] = useState('Авторизация')

  const showModal = () => setIsOpen(true);

  const handleOk = () => {
    setIsOpen(false);
    localStorage.setItem('email', emailInput)
    setAuthData(emailInput);
  }

  const handleCancel = () => {
    setIsOpen(false);
    setEmailInput('');
  }

  const leaveAccount = () => {
    setAuthData('');
    setEmailInput('');
    localStorage.removeItem('email');
    setIsOpen(false);
  }

  useEffect(() => {
    if (localStorage.getItem('email')) {
      setAuthData(localStorage.getItem('email'))
      setButtonText(localStorage.getItem('email'))
    }
    else setButtonText('Авторизация');
  }, [authData])


    return (
      <>
        <header className={s.container}>
          <Link className={s.anchor} to={'/'}>
            <h1 className={s.title}>
              Менеджер конференций
            </h1>        
          </Link>

          <Button onClick={() => showModal()}>
            {buttonText}
          </Button>
        </header>

        <Modal 
          title={
            authData ? "Данные" : "Авторизация"
          }
          open={isOpen} 
          onOk={handleOk} 
          onCancel={handleCancel}
          footer={
            authData ?
            [
              <Button type='primary' key='leave' onClick={leaveAccount}>Выйти</Button>
            ]
            :
            [
              <Button key='back' onClick={handleCancel}>Отмена</Button>,
              <Button type='primary' key='enter' onClick={handleOk} disabled={!regEmail.test(emailInput)}>Войти</Button>
            ]
        }
          >
            {
              authData 
              ? <><h3>{authData} - ваша почта</h3></>
              : <Input type='email' placeholder='Введите почту...' value={emailInput} onChange={(e) => setEmailInput(e.target.value)}/>
            }
            
        </Modal>
      </>
    )
}

export default Header
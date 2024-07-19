import MyButton from "../../UI/MyButton/MyButton";
import classes from "./Header.module.scss";
import { useNavigate } from "react-router-dom";
import ModalWindow from "../../UI/ModalWindow/ModalWindow";
import DropZone from "../../UI/DropZone/DropZone";
import {useEffect, useState} from "react";
import LoginForm from "../LoginForm/LoginForm";
import toast, {Toaster} from "react-hot-toast"
import useAuthStore from "../../../stores/auth";
import { MdEmail } from "react-icons/md";

import cat_image from "../../../assets/кот.png";

export default function Header() {
  const navigate = useNavigate();
  const [modalVisible, setModalVisible] = useState(false);
  const [menuVisible, setMenuVisible] = useState(false);
  const {isAuth, user, logout } = useAuthStore((state) => ({
    isAuth: state.isAuth,
    user: state.user,
    logout: state.logout
  }));

  useEffect(() => {
    if (isAuth) toast.success('Успешная авторизация!');
  }, [isAuth])

  const handleLogoutClick = (e) => {
    setMenuVisible(false);
    e.stopPropagation();
    logout();
  };

  const handleDocumentClick = () => {
    setMenuVisible(false);
  };

  const handleProfileClick = (e) => {
    setMenuVisible(!menuVisible);
    e.stopPropagation();
    
  };

  useEffect(() => {
    document.addEventListener("click", handleDocumentClick);
    return () => document.removeEventListener("click", handleDocumentClick);
  }, []);

  return (
    <header className={classes.header}>
      <div className="_wrapper">
        <div className={classes.header__container}>
          <h1 className={classes.brand_name} onClick={() => navigate(`/`)}>Conference</h1>
          <ul className={classes.header__links}>
            <li className={classes.header__link} onClick={() => navigate(`/`)}>Конференции</li>
          </ul>
          <div className={classes.header__btn}>
              {
                isAuth 
                    ? <div className={classes.user}>
                        <p className={classes.user__name}>User</p>
                        <img src={cat_image} alt="Profile" onClick={handleProfileClick}/>
                        <div className={menuVisible ? [classes.user__menu, classes.active].join(" ") : classes.user__menu} onClick={e => e.stopPropagation()}>
                          <p>{user.email}</p>
                          <div className={classes.user__logout} onClick={handleLogoutClick}>
                            <button className={classes.user__btn}>Выйти</button>
                          </div>
                        </div>
                      </div>
                    : <MyButton value={"Войти"} color={"red"} onClick={() => setModalVisible(true)}/>
              }
          </div>
        </div>
        <ModalWindow title={"Выбор статьи"} visible={modalVisible} setVisible={setModalVisible} showHeader={false}>
            <LoginForm setVisible={setModalVisible}/>
        </ModalWindow>
        <Toaster/>
      </div>
    
    </header>
  )
}

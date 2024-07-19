import { getShortenedString } from "../../../utils/utils";
import classes from "./ConferenceCard.module.scss";
import { useState, useEffect } from 'react';
import { useNavigate } from "react-router-dom";
import { publicRoutes } from "../AppRouter/routes";

export default function ConferenceCard({conference}) {
   const [color, setColor] = useState(1);
   let colors = ["green", "red", "purple", "pink", "blue"]

   const navigate = useNavigate();

   function chooseColor() {
      const randomIndex = Math.floor(Math.random() * (colors.length - 1)); // генерируем случайный индекс в допустимом диапазоне
      const result = colors[randomIndex];
      setColor(result);
   }

   useEffect(() => {
      chooseColor()
   }, [])


  return (
   <div className="conference" onClick={() => navigate(`/conference/${conference.id}`)}>
      <div className={classes["conference__container"]}>
            <div className={classes["conference__body"]}>
               <div className={classes["body__link"]}>
                  <div className={[classes["body__bg"], classes[color]].join(" ")}></div>

                  <div className={classes.title__box}>
                     <div className={classes["body__title"]}>
                        {getShortenedString(conference.name_rus_short || "Без названия", 30)}
                     </div>
                     <div className={classes["body__title_en"]}>
                     {getShortenedString(conference.name_eng_short || "Без названия", 30)}
                     </div>
                  </div>
                  
                  <div className={classes.date}>
                     <div className={classes["body__date-box"]}>
                        Начало:
                        <span className={classes["body__date"]}>
                           {conference.conf_start_date}
                        </span>
                     </div>
                     <div className={classes["body__date-box"]}>
                        Завершение:
                        <span className={classes["body__date"]}>
                           {conference.conf_end_date}
                        </span>
                     </div>
                  </div>
               </div>
            </div>
      </div>
   </div>
  )
}

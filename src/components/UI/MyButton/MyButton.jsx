import React from 'react';
import classes from "./MyButton.module.scss";

export default function MyButton({value, color="red", isActive=false, ...props}) {
  return (
    <button className={isActive ? [classes.btn, classes.active].join(" ") : classes.btn} {...props}>
         {value}
    </button>
  )
}

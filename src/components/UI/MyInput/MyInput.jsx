import { forwardRef } from "react";
import classes from "./MyInput.module.scss";
import { FaStarOfLife } from "react-icons/fa";

const MyInput = forwardRef(({errors, label, ...props}, ref) => (
    <>
      <label className={classes.label}>
        <span className={props.required ? [classes.label__text, classes.active].join(" ") : classes.label__text}>{label}<FaStarOfLife/></span>
        <input {...props} ref={ref} className={classes.input} />
      </label>
      <div className={classes.error}>
        <span>{errors}</span>
      </div>
    </>
  ))


  export default MyInput;
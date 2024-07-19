import classes from "./ModalWindow.module.scss";
import { IoMdClose } from "react-icons/io";

const ModalWindow = ({title, children, visible, setVisible, showHeader=true}) => {
  const rootClasses = [classes["modal"]];
  if (visible) rootClasses.push(classes.active);

  // function handleKeyDown(e) {
  //   console.log(e.code);
  //   if (e.code === 'Escape') {
  //     setVisible(false)
  //   }
  // }
  
  return (
    <div className={rootClasses.join(" ")} onClick={() => setVisible(false)}>
         <div className={classes.content} onClick={e => e.stopPropagation()}>
            <div className={showHeader ? [classes.content__header, classes.active].join(" ") : classes.content__header}>
                    <h5 className={classes.content__title}>{title}</h5>
                    <div onClick={() => setVisible(false)}>
                      <IoMdClose />
                    </div>
            </div>
            {children}
        </div>
    </div>
  );
};

export default ModalWindow;
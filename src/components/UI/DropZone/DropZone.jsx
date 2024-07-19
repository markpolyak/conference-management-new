import { useCallback } from "react";
import { useDropzone } from "react-dropzone";
import toast, {Toaster} from "react-hot-toast";

import classes from "./DropZone.module.scss";

export default function DropZone({visible, setVisible, setFile}) {
  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach((file) => {
      // alert(JSON.stringify(file));
    });
    console.log(acceptedFiles);
    if (acceptedFiles.length > 0){
      setFile(acceptedFiles[0])
      setVisible(false);
    } else {
      toast.error('Тип файла не поддерживается!');
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive, open } = useDropzone({
    onDrop,
    noClick: true,
    multiple: false,
    accept: { "application/doc": [".doc", ".docx"] },
  });

  return (
    <div
      {...getRootProps()}
      className={
        isDragActive
          ? [classes.dropzone, classes.active].join(" ")
          : classes.dropzone
      }
    >
      <input {...getInputProps()} />
      <div className={classes.dropzone__box}>
        <p>Перетащите файл сюда</p>
        <p>или</p>
        <div className={classes.dropzone__btn} onClick={open} >
          Выбрать файл
        </div>
      </div>
      <Toaster/>
    </div>
  );
}
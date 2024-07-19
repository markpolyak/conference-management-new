import {useState, useEffect} from 'react';
import classes from "./ApplicationEditForm.module.scss";
import { useForm } from "react-hook-form";
import MyInput from '../../UI/MyInput/MyInput';
import {adviserValidation, nameValidation, surnameValidation, patronymicValidation, emailValidation, universityValidation, phoneValidation, publicationNameValidation } from '../../../utils/validations';
import { FaDownload } from "react-icons/fa6";
import toast, { Toaster } from 'react-hot-toast';
import { useNavigate, useParams } from 'react-router-dom';
import useApplicationStore from '../../../stores/applications';
import ModalWindow from '../../UI/ModalWindow/ModalWindow';
import DropZone from '../../UI/DropZone/DropZone';
import { FaPlus } from "react-icons/fa";
import { FaMinus } from "react-icons/fa6";
import useConferenceStore from '../../../stores/conferences';

export default function ApplicationEditForm() {
   const {applications } = useApplicationStore((state) => ({
      applications: state.applications,
    }));
    const {conferenceSingle } = useConferenceStore((state) => ({
      conferenceSingle: state.conferenceSingle,
    }));
   const [modalVisible, setModalVisible] = useState(false);
   const [file, setFile] = useState({});
   const navigate = useNavigate();
   const params = useParams();

  
   let app;
    console.log(applications)
   if (applications) app = applications.filter(application => application.id === Number(params.id)).at(0);

   const [coauthors, setCoauthors] = useState(app ? app.coauthors : []);

   const {
      register,
      handleSubmit,
      watch,
      reset,
      resetField,
      formState: { errors, isValid, isSubmitted, isSubmitting },
    } = useForm({ mode: "onTouched" });
    
    const watchFields = watch(["name", "surname", "email", "university", "group", "phone" ]);
    
    const onSubmit = (data) => {
      // if (!file.name) toast.error('Ошибка! Прикрепите файл!');
      // else 
      toast.success('Заявка отправлена!');
      if (params.id !== "undefined" && params.id !== "null") navigate(-1);
    };

    function handleAuthor(e, event="add") {
      e.stopPropagation();
      
      event === "add" ? setCoauthors([...coauthors, 1]) : setCoauthors(coauthors.slice(0, -1));
    }

   //  useEffect(() => {
   //    if (file.name) {
   //       toast.success('Статья успешно добавлена!');
   //    }
   //  }, [file.name])

   //  useEffect(() => {
   //    console.log(modalVisible)
   //    document.body.style.overflow = modalVisible ? 'hidden' : "scroll";
   //  }, [modalVisible])

   if (!app) {
      return <></>
   }

   return (
      <div className={classes.wrapper}>
            <div className={classes.body__bg}></div>
            <h2 className={classes.title}>Редактирование Заявки</h2>
            <form className={classes.form} onSubmit={handleSubmit(onSubmit)}>
               <div className={classes.form__fields}>
                  <MyInput
                     type="text"
                     placeholder="Иван"
                     defaultValue={app.name || ""}
                     {...register("name", nameValidation)}
                     label={"Имя"}
                     required
                     errors={errors.name && errors.name.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="Иванов"
                     defaultValue={app.surname || ""}
                     {...register("surname", surnameValidation)}
                     label={"Фамилия"}
                     required
                     errors={errors.surname && errors.surname.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="Иваныч"
                     defaultValue={app.patronymic || ""}
                     {...register("patronymic", patronymicValidation)}
                     label={"Отчество"}
                     required
                     errors={errors.patronymic && errors.patronymic.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="Email"
                     defaultValue={app.email || ""}
                     {...register("email", emailValidation)}
                     label={"Адрес Email"}
                     required
                     errors={errors.email && errors.email.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="ГУАП"
                     defaultValue={app.university || ""}
                     {...register("university", universityValidation)}
                     label={"Университет"}
                     required
                     errors={errors.university && errors.university.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="Группа"
                     defaultValue={app.student_group || ""}
                     {...register("student_group")}
                     label={"Группа"}
                     errors={errors.student_group && errors.student_group.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="+78005553535"
                     defaultValue={app.phone || ""}
                     {...register("phone", phoneValidation)}
                     label={"Номер телефона"}
                     errors={errors.phone && errors.phone.message}
                  />
                  <MyInput
                     type="text"
                     placeholder=""
                     defaultValue={app.title || ""}
                     {...register("title",publicationNameValidation)}
                     label={"Название публикации"}
                     required
                     errors={errors.title && errors.title.message}
                  />
                  <MyInput
                     type="text"
                     placeholder="Иван Иваныч"
                     defaultValue={app.adviser || ""}
                     {...register("adviser", adviserValidation)}
                     label={"Руководитель"}
                     required
                     errors={errors.adviser && errors.adviser.message}
                  />

                  <div className={classes.form__file}>
                     <div
                        className={classes["form__file-btn"]}
                        onClick={() => setModalVisible(true)}>
                        <FaDownload />
                        <span>Загрузить статью</span>
                     </div>

                     {file.name && file.size &&
                     <div className={classes["form__file-title"]}>
                        <span>{file.name || ""}</span>-<span>{(file.size / 1024 / 1024).toFixed(2)}MB</span>
                     </div>
                       }
                  </div>

                  <div className={classes.form__coauthors}>
                     <h3 className={classes["form__coauthors-title"]}>Соавторы статьи<FaPlus onClick={e => handleAuthor(e, "add")}/><FaMinus onClick={e => handleAuthor(e, "pop")}/></h3>
                     {coauthors.map((author, index) =>
                        <div className={classes.author} key={index}>
                           <MyInput
                              type="text"
                              placeholder="Иван"
                              defaultValue={app.coauthors[index].name || ""}
                              {...register(`authorName${index}`)}
                              label={"Имя"}
                              required
                              errors={errors.publicationName && errors.publicationName.message}
                           />
                           <MyInput
                              type="text"
                              placeholder="Иванов"
                              defaultValue={app.coauthors[index].surname || ""}
                              {...register(`authorSurname${index}`, surnameValidation)}
                              label={"Фамилия"}
                              required
                              errors={errors.publicationName && errors.publicationName.message}
                           />
                           <MyInput
                              type="text"
                              placeholder="Иваныч"
                              defaultValue={app.coauthors[index].patronymic || ""}
                              {...register(`authorPatronymic${index}`, patronymicValidation)}
                              label={"Отчество"}
                              required
                              errors={errors.publicationName && errors.publicationName.message}
                           />
                           <MyInput
                              type="text"
                              placeholder="example@gmail.com"
                              defaultValue={app.coauthors[index].email || ""}
                              {...register(`authorEmail${index}`, emailValidation)}
                              label={"Email"}
                              required
                              errors={errors.publicationName && errors.publicationName.message}
                           />
                        </div>
                     )
                  }
                  </div>
                
               </div>
               <button
                  type="submit"
                  className={classes.form__btn}
               >
                  Сохранить
               </button>
               <ModalWindow title={"Выбор статьи"} visible={modalVisible} setVisible={setModalVisible}>
                  <DropZone visible={modalVisible} setVisible={setModalVisible} setFile={setFile}/>
               </ModalWindow>
               <Toaster/>
            </form>
      </div>
   )
}

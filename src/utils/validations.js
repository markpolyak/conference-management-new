export const emailValidation = {
   minLength: {
     value: 9,
     message: "Минимум 9 символов",
   },
   maxLength: {
     value: 35,
     message: "Максимум 35 символов",
   },
   pattern: {
     value: /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/,
     message: "Email не соответствует формату",
   },
 };
 

 export const nameValidation = {
   minLength: {
     value: 2,
     message: "Минимум 2 символа",
   },
   maxLength: {
     value: 30,
     message: "Максимум 30 символов",
   },
   pattern: {
     value: /[А-Яа-я]{2,}$/,
     message: "Имя не соответствует формату",
   },
 };

 export const adviserValidation = {
  minLength: {
    value: 2,
    message: "Минимум 2 символа",
  },
  maxLength: {
    value: 30,
    message: "Максимум 30 символов",
  },
  pattern: {
    value: /[А-Яа-я.]{2,}$/,
    message: "Имя руководителя не соответствует формату",
  },
};

 
 export const surnameValidation = {
   minLength: {
     value: 2,
     message: "Минимум 1 символ",
   },
   maxLength: {
     value: 30,
     message: "Максимум 30 символов",
   },
   pattern: {
     value: /[А-Яа-я]{1,}$/,
     message: "Фамилия не соответствует формату",
   },
 };

 export const patronymicValidation = {
  minLength: {
    value: 1,
    message: "Минимум 1 символ",
  },
  maxLength: {
    value: 30,
    message: "Максимум 30 символов",
  },
  pattern: {
    value: /[А-Яа-я]{1,}$/,
    message: "Отчество не соответствует формату",
  },
};

 
 

 export const universityValidation = {
   minLength: {
     value: 2,
     message: "Минимум 1 символ",
   },
   maxLength: {
     value: 30,
     message: "Максимум 30 символов",
   },
   pattern: {
     value: /[А-яа-я]{2,}$/,
     message: "Название университета не соответствует формату",
   },
 };

 export const phoneValidation = {
   // minLength: {
   //   value: 2,
   //   message: "Минимум 1 символ",
   // },
   // maxLength: {
   //   value: 30,
   //   message: "Максимум 30 символов",
   // },
   pattern: {
     value: /^(\+7|8)?\s?\(?\d{3}\)?\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}$/,
     message: "Номер телефона не соответствует формату",
   },
 };

 export const publicationNameValidation = {
  minLength: {
    value: 3,
    message: "Минимум 3 символа",
  },
  maxLength: {
    value: 50,
    message: "Максимум 50 символов",
  },
  pattern: {
    value: /[А-Яа-я]{3,}$/,
    message: "Название публикации не соответствует формату",
  },
};

export const passwordValidation = {
  minLength: {
    value: 3,
    message: "Минимум 3 символа",
  },
  maxLength: {
    value: 50,
    message: "Максимум 50 символов",
  },
  // pattern: {
  //   value: /[1-9]{3,}$/,
  //   message: "Пароль не соответствует формату",
  // },
};


//  export const groupValidation = {
//    minLength: {
//      value: 2,
//      message: "Минимум 4 символа",
//    },
//    maxLength: {
//      value: 30,
//      message: "Максимум 4 символа",
//    },
//    pattern: {
//      value: /^(Z[1-8][0-47-9]\d{2}|[1-8][0-47-9]\d{2}[KM]|[1-8][0-47-9]\d{2})$/,
     
//      message: "Номер группы не соответствует формату",
//    },
//  };
 
//  export const passwordValidation = {
//    minLength: {
//      value: 8,
//      message: "Минимум 8 символов",
//    },
//    maxLength: {
//      value: 25,
//      message: "Максимум 25 символов",
//    },
//  };
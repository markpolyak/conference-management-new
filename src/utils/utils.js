export const getShortenedString = (value, maxLetters) => {
   if (!value) return "";
   return value.length > maxLetters ? value.slice(0, maxLetters) + "..." : value;
};

export function formatDateTime(input) {
   // Создаем объект даты из строки
  if (!input) return "";
   let date = new Date(input);

 
   // Получаем компоненты даты и времени
   let year = date.getFullYear();
   let month = String(date.getMonth() + 1).padStart(2, '0');
   let day = String(date.getDate()).padStart(2, '0');
   let hours = String(date.getHours()).padStart(2, '0');
   let minutes = String(date.getMinutes()).padStart(2, '0');
   let seconds = String(date.getSeconds()).padStart(2, '0');
 
   // Формируем строку в нужном формате
   return `${year}-${month}-${day} / ${hours}:${minutes}:${seconds}`;
 }
 
 export function checkDateRange(startDate, endDate) {
   // Получаем текущую дату
   const currentDate = new Date();

   // Преобразуем строки дат в объекты Date
   const start = new Date(startDate.split('.').reverse().join('-'));
   const end = new Date(endDate.split('.').reverse().join('-'));

   // Проверяем, находится ли текущая дата в заданном промежутке
   return currentDate >= start && currentDate <= end;
}

export function transformObject(input) {
   const coauthors = [];
   const result = {};
 
   // Сначала копируем все поля, кроме тех, что начинаются с author
   for (const [key, value] of Object.entries(input)) {
     if (!key.startsWith('author')) {
       result[key] = value;
     }
   }
 
   // Затем собираем авторов в массив
   let index = 0;
   while (input.hasOwnProperty(`authorName${index}`)) {
     const coauthor = {
       name: input[`authorName${index}`],
       surname: input[`authorSurname${index}`],
       patronymic: input[`authorPatronymic${index}`],
       email: input[`authorEmail${index}`],
     };
     coauthors.push(coauthor);
     index++;
   }
 
   // Добавляем массив coauthors в результат
   result.coauthors = coauthors;
 
   return result;
 }
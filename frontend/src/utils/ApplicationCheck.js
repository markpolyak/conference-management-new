import { regEmail } from "./regulars";

export const isApplicationCorrect = (application) => {
    if (application.title && 
        regEmail.test(application.email) && 
        application.name && 
        application.surname && 
        application.patronymic && 
        application.university && 
        application.applicant_role && 
        application.adviser &&
        checkCoauthors(application.coauthors)) return true
    else return false
}

export const checkCoauthors = (coauthors) => {
    for (const coauthor of coauthors) {
        if (!(coauthor.name && coauthor.surname && coauthor.patronymic && regEmail.test(coauthor.email))) return false;
    }
    return true
}
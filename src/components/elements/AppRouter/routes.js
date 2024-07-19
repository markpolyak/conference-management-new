import Conference from "../Conference/Conference";
import HomePage from "../../../pages/HomePage/HomePage";
import ConferenceIdPage from "../../../pages/ConferenceIdPage/ConferenceIdPage";
import ApplicationForm from "../ApplicationForm/ApplicationForm";
import ApplicationEditPage from "../../../pages/ApplicationEditPage/ApplicationEditPage";
import ApplicationPage from "../../../pages/ApplicationPage/ApplicationPage"

export const publicPaths = {
  HOMEPAGE: "/",
  CONFERENCE_ID: "/conference/:id",
  APPLICATION: "/conference/:id/application",
  APPLICATION_EDIT: "/conference/:id/applications/:id",
  ERROR: '/404',
}

export const publicRoutes = [
  { path: publicPaths.HOMEPAGE, element: <HomePage/> },
  { path: publicPaths.CONFERENCE_ID, element: <ConferenceIdPage/> },
  { path: publicPaths.APPLICATION, element: <ApplicationPage/> },
  { path: publicPaths.APPLICATION_EDIT, element: <ApplicationEditPage/> },
]
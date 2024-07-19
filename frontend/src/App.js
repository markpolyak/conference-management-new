import React, { useState } from 'react'
import { createBrowserRouter, Navigate, RouterProvider } from 'react-router-dom'
import ConferenceList from './components/Conferences/ConferenceList'
import Conference from './components/ConferencePage/Conference'

export const UserContext = React.createContext(null);

const App = () => {

    const [authData, setAuthData] = useState('');

    const router = createBrowserRouter([
        {
            path:"/",
            element: <Navigate replace to ="/conference"/>
        },
        {
            path:"/conference",
            element: <ConferenceList/>
        },
        {
            path:"/conference/:conference_id",
            element: <Conference/>
        }
    ])

  return (
    <>
        <UserContext.Provider value={{authData:authData, setAuthData:setAuthData}}>
            <RouterProvider router={router}/>
        </UserContext.Provider>
    </>
  )
}

export default App
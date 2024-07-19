import React from 'react';
import { Route, Routes, Navigate } from "react-router-dom";
import { publicRoutes } from './routes';

export default function AppRouter() {
  return (
    <div>
      <Routes>
         {publicRoutes.map(route =>
            <Route path={route.path} element={route.element} key={route.path}/>
        )}
         <Route path={"/*"} element={<Navigate to={"/404"} replace/>}/>
      </Routes>
    </div>
  )
}

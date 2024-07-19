import React from 'react';
import './App.css';
import ReactDOM from 'react-dom/client';
import Footer from './components/Footer/Footer';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <>
        <App/>
        <Footer/>
    </>
);
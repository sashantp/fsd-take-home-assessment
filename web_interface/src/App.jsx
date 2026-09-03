import { useState } from 'react'
import { BrowserRouter, Routes, Route } from "react-router-dom";
// import { Routes, Route } from "react-router-dom";
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'
import CrmEvents from "./components/CrmEvents";
import CalendarEvents from "./components/CalendarEvents";
import CrmReconciledEvents from "./components/CrmReconciledEvents";
import Layout from './Layout';


function App() {
  return (
    <BrowserRouter>
      <Layout>        
        <Routes>
          <Route path="/crm" element={<CrmEvents />} />
          <Route path="/calender" element={<CalendarEvents />} />
          <Route path="/crm/reconciled" element={<CrmReconciledEvents />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App

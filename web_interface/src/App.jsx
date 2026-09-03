import { useState } from 'react'
import { Routes, Route } from "react-router-dom";
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'
import CrmEvents from "./components/CrmEvents";
import CalendarEvents from "./components/CalendarEvents";


function App() {
  return (
    <Routes>
      <Route path="/crm" element={<CrmEvents />} />
      <Route path="/calendar" element={<CalendarEvents />} />
    </Routes>
  );
}

export default App

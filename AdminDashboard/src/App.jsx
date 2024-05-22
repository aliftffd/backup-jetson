import { useState } from 'react'
import './App.css'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './Header'
import Sidebar from './Sidebar'
import Home from './Home'
import History from './History'
function App() {
  const [openSidebarToggle, setOpenSidebarToggle] = useState(false)
  const OpenSidebar = () => {
    setOpenSidebarToggle(!openSidebarToggle)
  }
  return (
    <Router>
      <div className='grid-container'>
        <Header OpenSidebar={OpenSidebar} />
        <Sidebar openSidebarToggle={openSidebarToggle} OpenSidebar={OpenSidebar} />
        <Routes>
          <Route path="/" element={<Home />} />  {/* Rute untuk halaman utama */}
          <Route path="/History" element={<History />} />  {/* Rute untuk halaman History */}
        </Routes>
      </div>
    </Router>
  )
}
export default App

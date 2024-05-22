import React, { useState } from 'react'
import { Link } from 'react-router-dom';
import { MdOutlineSpeed, MdHistory, MdQuestionMark, MdTrain, MdLocationOn, MdClose } from 'react-icons/md'

function Sidebar({ openSidebarToggle, OpenSidebar }) {
    return (
        <aside id="Sidebar" className={openSidebarToggle ? "sidebar-responsive" : ""}>
            <div className='sidebar-title'>
                <div className='sidebar-brand'>
                    <MdTrain className='icon_header' /> ATP
                </div>
                <div className='icon close_icon' onClick={OpenSidebar}>
                    <MdClose />
                </div>
            </div>

            <ul className='sidebar-list'>
                <li className='sidebar-list-item'>
                    <Link to="/" className='active'>
                        <MdOutlineSpeed className='icon' /> Dashboard
                    </Link>
                </li>
                <li className='sidebar-list-item'>
                    <Link to="/History">
                        <MdHistory className='icon' /> History
                    </Link>
                </li>
            </ul>
        </aside>
    )
}

export default Sidebar
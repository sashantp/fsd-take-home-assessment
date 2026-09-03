import React from 'react';


const Layout = ({children}) => {

	return(
		<div className="app-container">
			<header>
				<nav className="navbar navbar-expand-lg navbar-dark bg-dark">
				  <div className="container-fluid">
				    <div className="collapse navbar-collapse" id="navbarSupportedContent">
				      <ul className="navbar-nav me-auto mb-2 mb-lg-0">
				        <li className="nav-item">
				          <a className="nav-link" href="/calender">Calendar Events</a>
				        </li>
				        <li className="nav-item">
				          <a className="nav-link" href="/crm">CRM Events</a>
				        </li>
				        <li className="nav-item">
				          <a className="nav-link" href="/crm/reconciled">CRM Events Reconciled</a>
				        </li>
				      </ul>
				    </div>
				  </div>
				</nav>
			</header>
			<main className="content-area">
				{children}
			</main>
			<footer>
			</footer>
		</div>
	);
};

export default Layout;
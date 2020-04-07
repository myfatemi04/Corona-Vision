import React from 'react';

function Navbar() {
    return (
        <nav className="navbar navbar-expand-lg custom-nav-color border-bottom navbar-dark sticky-top">
            <a className="navbar-brand lato" style={{fontSize: "2rem"}} href="/">Corona Vision</a>
            <button className="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbar-content" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
                <span className="navbar-toggler-icon"></span>
            </button>
            <div className="collapse navbar-collapse" id="navbar-content">
                <ul className="navbar-nav mr-auto">
                    <li className="nav-item">
                        <a className="nav-link" href="/">
                            Map
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="/charts">
                            Charts
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="/data">
                            Data
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="/whattodo">
                            How to help
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="/history">
                            History of spread
                        </a>
                    </li>
                    <li className="nav-item">
                        <a className="nav-link" href="/contact">
                            Contact us
                        </a>
                    </li>
                </ul>
            </div>
        </nav>
    );
}

export default Navbar;

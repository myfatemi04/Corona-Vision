import React from 'react';
import { BrowserRouter, Route, Switch } from 'react-router-dom';

import './Main.css';
import './Map.css';

import Navbar from './Nav.js';
import Styles from './Styles.js';
import CoronaMapContainer from './CoronaMap.js';

function Router() {
  return (
    <BrowserRouter>
      <div>
          <Switch>
            <Route path="/" component={Index} exact/>
          <Route component={Error}/>
          </Switch>
      </div> 
    </BrowserRouter>
  );
}

function Index() {
  return (<>
    <Styles/>
    <Navbar/>
    <CoronaMapContainer/>
  </>)
}

export default Index;

export {
  Router
};

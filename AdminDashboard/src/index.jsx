import React from 'react';
import ReactDOM from 'react-dom';
import 'normalize.css'; // Impor normalize.css
import './App.css'; // Impor app.css untuk styling keseluruhan
import App from './App';
import reportWebVitals from './reportWebVitals';

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById('root')
);

reportWebVitals();

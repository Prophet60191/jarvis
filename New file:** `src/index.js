import React from 'react';
import ReactDOM from 'react-dom';

function App() {
    return (
        <div>
            <h1>Weather Dashboard</h1>
            <input type="text" placeholder="Enter city name" />
            <button>Get Weather</button>
        </div>
    );
}

ReactDOM.render(<App />, document.getElementById('root'));

// entire file content ...
import React, { useState } from 'react';
import Button from './Button';

const App = () => {
  const [count, setCount] = useState(0);

  return (
    <div>
      <h1>Test Button App</h1>
      <p>Count: {count}</p>
      <Button onClick={() => setCount(count + 1)} />
    </div>
  );
};

export default App;

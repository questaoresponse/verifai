import { BrowserRouter as Router, Routes, Route } from 'react-router';
import Home from './Home'
import Insert from './Insert'
import './App.css'

function App() {

  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home/>} />
        <Route path="/insert" element={<Insert/>} />
      </Routes>
    </Router>
  )
}

export default App;
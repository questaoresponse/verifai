import { useEffect, useState } from 'react'
import Header from './Header'
import Home from './Home'
import Insert from './Insert'
import './App.css'

interface line{
  id: number,
  link:string,
  type: number,
  expect: number,
  result: number
}

function App() {
  const [ currentPage, setCurrentPage ] = useState("Home");

  return <>
    <Header currentPage={currentPage} setCurrentPage={setCurrentPage}></Header>
    <div id="page">
      { currentPage == "Home" ? <Home></Home> : <Insert setCurrentPage={setCurrentPage}></Insert> }
    </div>
  </>
}

export default App

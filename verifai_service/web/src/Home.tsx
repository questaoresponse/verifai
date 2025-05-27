import { useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import './Home.css'

interface line{
  id: number,
  link:string,
  type: number,
  expect: number,
  result: number
}

function Home() {
  const [ lines, setLines ] = useState<line[]>([]);

  useEffect(()=>{
    fetch("http://127.0.0.1:12345/list").then(response=>response.json()).then(response=>{
      setLines(response.data);
    })
  },[]);

  return (
    <div id="home">
        <div id='table'>
            <div id='head'>
                <div className="line-id">Id</div>
                <div className="line-link">Link</div>
                <div className="line-expect">Expectativa</div>
                <div className="line-type">Tipo</div>
                <div className="line-result">Resultado</div>
            </div>
            <div id="content">{lines.map((line)=>{
                return <div className='line'>
                    <div className="line-id">{line.id}</div>
                    <div className="line-link">{line.link}</div>
                    <div className="line-expect">{line.expect}</div>
                    <div className="line-type">{line.type}</div>
                    <div className="line-result">{line.result}</div>
                </div>
            })}</div>
        </div>
    </div>
  )
}

export default Home

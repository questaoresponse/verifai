import { useEffect, useState, type Dispatch, type SetStateAction } from 'react'
import './App.css'

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
    setLines([{id:1,link:"https://",type:0,expect:1,result:1}]);
  },[]);

  return (
    <div id="page">
        <div className='table'>
            <div className='head'>
                <div className="line-id">Id</div>
                <div className="line-link">Link</div>
                <div className="line-expect">Expectativa</div>
                <div className="line-type">Tipo</div>
                <div className="line-result">Resultado</div>
            </div>
            <div className="content">{lines.map((line)=>{
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

import { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from "react-router-dom";
import "./Insert.css";
import Header from './Header';

const SERVER = import.meta.env.DEV ? "http://127.0.0.1:12345" : "";

interface line {
  id: number,
  link:string,
  type: number,
  processedType: string,
  expect: number,
  result: string,
  response: string
}

function Insert(){
    const navigate = useNavigate();
    const location = useLocation();

    const refs = {
        link: useRef<HTMLInputElement>(null),
        type: useRef<HTMLSelectElement>(null),
        expect: useRef<HTMLSelectElement>(null)
    }
    const [ editLine, setEditLine ] = useState<line | null>(null);

    const verifyInsert = ()=>{
        const link = refs.link.current!.value;
        const type = refs.type.current!.value;
        const expect = refs.expect.current!.value;

        if (!(link.startsWith("https://www.instagram.com/p/") || link.startsWith("https://www.instagram.com/reel/") || link.startsWith("https://www.instagram.com/share/p/") || link.startsWith("https://wwww.instagram.com/share/reel/"))) return;

        fetch(SERVER + "/insert", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ link, type, expect })
        }).then(response=>response.json()).then(response=>{
            response.result=="true" && navigate("/");
        })
    }

    useEffect(()=>{
        if (location.pathname == "/edit"){
            fetch(SERVER + "/edit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({ type: "get" })
            }).then(response=>response.json()).then(response=>{
                response.result=="true" && navigate("/");
            });
        }
    },[]);

    return <>
        <Header></Header>
        <div id="insert" className='page'>
            <div id="form">
                <div className='group'>
                    <div className='label'>Link:</div>
                    <input ref={refs.link} id="link" className='group-input'></input>
                </div>
                <div className='group'>
                    <div className='label'>Tipo de conteúdo:</div>
                    <select className='insert-select group-input' defaultValue="1" ref={refs.type} id="type">
                        <option value="1">Esporte</option>
                        <option value="2">Cultura</option>
                        <option value="3">Ciência</option>
                        <option value="4">Política</option>
                        <option value="5">História</option>
                        <option value="6">Geografia</option>
                        <option value="0">Outro</option>
                    </select>
                </div>
                <div className='group'>
                    <div className='label'>Veracidade:</div>
                    <select className='insert-select group-input' defaultValue="1" ref={refs.expect} id="expect">
                        <option value="1">Verdadeiro</option>
                        <option value="0">Falso</option>
                    </select>
                </div>
                <div id="send" className='btn' onClick={verifyInsert}>Inserir</div>
            </div>
        </div>
    </>
}

export default Insert
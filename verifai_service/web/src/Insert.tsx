import { useRef, type Dispatch, type SetStateAction } from 'react'
import "./Insert.css"

function Insert({setCurrentPage}:{setCurrentPage: Dispatch<SetStateAction<string>>}){
    const refs = {
        link: useRef<HTMLInputElement>(null),
        type: useRef<HTMLSelectElement>(null),
        expect: useRef<HTMLSelectElement>(null)
    }

    const verifyInsert = ()=>{
        const link = refs.link.current!.value;
        const type = refs.type.current!.value;
        const expect = refs.expect.current!.value;

        if (!(link.startsWith("https://www.instagram.com/p/") || link.startsWith("https://www.instagram.com/reel/") || link.startsWith("https://www.instagram.com/share/p/") || link.startsWith("https://wwww.instagram.com/share/reel/"))) return;

        fetch("http://127.0.0.1:12345/insert", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ link, type, expect })
        }).then(response=>response.json()).then(response=>{
            response.result=="true" && setCurrentPage("Home");
        })
    }

    return <div id="insert">
        <input ref={refs.link} id="link"></input>
        <select defaultValue="1" ref={refs.type} id="type">
            <option value="1">Esporte</option>
            <option value="2">Cultura</option>
            <option value="3">Ciencia</option>
            <option value="4">Politica</option>
            <option value="5">História</option>
            <option value="6">Geografia</option>
            <option value="0">Outra</option>
        </select>
        <select defaultValue="1" ref={refs.expect} id="expect">
            <option value="1">Verdadeiro</option>
            <option value="0">Falso</option>
        </select>
        <div id="send" className='btn' onClick={verifyInsert}>Inserir</div>
    </div>
}

export default Insert
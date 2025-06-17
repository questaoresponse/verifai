import { useEffect, useState } from 'react'
import './Home.css'
import Header from './Header';
import { useNavigate } from 'react-router-dom';

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

function Home() {
    const navigate = useNavigate();

    const [ lines, setLines ] = useState<line[]>([]);
    const [ executeValue, setExecuteValue ] = useState("");
    const [ isValidExecuteValue, setIsValidExecuteValue ] = useState(true);
    const [ result, setResult ] = useState({ recall: 0, precision: 0, specificity: 0, accuracy: 0 });
    const [ response, _ ] = useState([false,""]);

    const transformData = (data: any) => {
        const types = [
            "Outro",
            "Esporte",
            "Cultura",
            "Ciência",
            "Política",
            "História",
            "Geografia"
        ];
        return data.map((line: any)=>{ return {...line, processedType: types[Number(line.type)], result: line.result == 2 ? "-" : String(line.result) } });
    };
    
    const onExecuteInput = (e: any) => {
            setExecuteValue(previousValue=>{
                const value: string = e.target.value;
                if (value == "" || /^\d+$/.test(value) || /^\d+-$/.test(value) || /^\d+-\d+$/.test(value)){
                    if (/^\d+-\d+$/.test(value)){
                        const parts = value.split("-");
                        const id_start = Number(parts[0]);
                        const id_end = Number(parts[1]);
                        
                        setIsValidExecuteValue(id_end >= id_start && id_end <= lines.length);
                    } else {
                        setIsValidExecuteValue(false);
                    }
                    return value;
                }

                setIsValidExecuteValue(false);

                return previousValue;
            });
    }

    const executeVerify = () => {
        if (!isValidExecuteValue) return;

        const parts = executeValue.split("-");
        const id_start = lines[Number(parts[0]) - 1].id;
        const id_end = lines[Number(parts[1]) - 1].id;

        setIsValidExecuteValue(false);

        fetch(SERVER + "/verify", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id_start,
                id_end
            })
        }).then(response=>response.json()).then(response=>{
            if (response.result == "true"){
                setExecuteValue(`1-${response.data.length}`);
                setLines(transformData(response.data));
            }
            if (/^\d+-\d+$/.test(executeValue)){
                const parts = executeValue.split("-");
                const id_start = Number(parts[0]);
                const id_end = Number(parts[1]);
                setIsValidExecuteValue(id_end >= id_start && id_end <= lines.length);
            } else {
                setIsValidExecuteValue(false);
            }
        });
    }

    const deleteLine = (id: number) => {
        fetch(SERVER + "/delete", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                id
            })
        }).then(response=>response.json()).then(response=>{
            if (response.result == "true"){
                setExecuteValue(`1-${response.data.length}`);
                setLines(transformData(response.data));
            }
        });
    }
    
    const switchResponse = (_: line) => {
        
    }

    const closeResponse = () => {
    }

    useEffect(()=>{
        fetch(SERVER + "/list").then(response=>response.json()).then(response=>{
            setExecuteValue(`1-${response.data.length}`);
            setLines(transformData(response.data));
        });
    },[]);

    useEffect(()=>{
        const getValue = (value: number) => isNaN(value) ? 0 : value;

        const VP = lines.filter(line=>line.expect == 1 && line.result == "1").length;
        const VN = lines.filter(line=>line.expect == 0 && line.result == "0").length;
        const FP = lines.filter(line=>line.expect == 0 && line.result == "1").length;
        const FN = lines.filter(line=>line.expect == 1 && line.result == "0").length;

        const recall = getValue(VP / (VP + FN));
        const precision = getValue(VP / (VP + FP));
        const specificity = getValue(VN / (VN + FP));
        const accuracy = getValue((VP + VN) / (VP + VN + FP + FN));

        setResult({ recall, precision, specificity, accuracy });

    },[lines]);

    const editLine = (line: line) => {
        navigate("/edit?id=" + line.id);
    }

    return <>
        <Header></Header>
        <div id="home" className='page'>
            <div id='table'>
                <div id='head'>
                    <div className="line-id">Id</div>
                    <div className="line-link">Link</div>
                    <div className="line-expect">Expectativa</div>
                    <div className="line-type">Tipo</div>
                    <div className="line-result">Resultado</div>
                    <div className='line-options'>Opções</div>
                </div>
                <div id="content">{lines.map((line, i: number)=>{
                    return <div className='line' key={String(i)}>
                        <div className="line-id">{i + 1}</div>
                        <a className="line-link" href={line.link}>
                            <div className='line-link-text'>{line.link}</div>
                        </a>
                        <div className="line-expect">{line.expect}</div>
                        <div className="line-type">{line.processedType}</div>
                        <div className="line-result">{line.result}</div>
                        <div className="line-options">
                            <div className='delete-option btn-option' onClick={()=>deleteLine(line.id)}>del</div>
                            <div className="edit-option btn-option" onClick={()=>editLine(line)}>edit</div>
                            <div className="complete-option btn-option" onClick={()=>switchResponse(line)}>comp</div>
                        </div>
                    </div>
                })}</div>
            </div>
            <div id="execute-div">
                <div className='execute-group'>
                    <div className='label'>Links para executar:</div>
                    <input value={executeValue} onInput={onExecuteInput}></input>
                </div>
                <div style={isValidExecuteValue ? { opacity: "1", cursor: "pointer" } : { opacity: "0.5", cursor: "initial" }} id="execute-btn" className='btn' onClick={executeVerify}>Executar</div>
            </div>
            <div id="result">
                <div id="result1">Sensibilidade: {result.recall}</div>
                <div id="result2">Precisão: {result.precision}</div>
                <div id="result3">Especificidade: {result.specificity}</div>
                <div id="result4">Acurácia: {result.accuracy}</div>
            </div>
            <div id="response-menu-a" style={{ display: response[0] ? "block" : "none" }}></div>
            <div style={{ display: response[0] ? "block" : "none" }} id="response-menu">
                <div id="response-x" onClick={closeResponse}></div>
                <div id="response"></div>
            </div>
        </div>
    </>
}

export default Home;

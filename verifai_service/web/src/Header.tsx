import type { Dispatch, SetStateAction } from "react"
import "./Header.css"
function Header({currentPage, setCurrentPage}:{ currentPage: string, setCurrentPage: Dispatch<SetStateAction<string>>}){
    return <div id="header">
            <div id="btn-header" className="btn" onClick={()=>setCurrentPage(currentPage=>currentPage=="Home" ? "Insert" : "Home")}>{currentPage=="Home" ? "Insert" : "Home"}</div> 
        </div>
}

export default Header
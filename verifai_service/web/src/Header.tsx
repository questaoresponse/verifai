import { useNavigate, useLocation } from "react-router-dom";
import "./Header.css"
function Header(){
    const navigate = useNavigate();
    const location = useLocation();

    return <div id="header">
        <div id="btn-header" className="btn" onClick={()=>navigate(location.pathname == "/" ? "/insert" : "/")}>{location.pathname == "/" ? "Insert" : "Home"}</div> 
    </div>
}

export default Header;
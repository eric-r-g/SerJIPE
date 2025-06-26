import './headerdiv.css';
import logo from '/JIPElogo.png';

function HeaderDiv(){

    return (
        <div id="header-div">
            <header id='header'>
                <div id='center-img'>
                    <img src={logo} alt="Logo SerJIPE" />
                </div>
            </header>
            <div id='controls'>
                <button>Listar dispositivos</button>
            </div>
        </div>
    )
}

export default HeaderDiv;
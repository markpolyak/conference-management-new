import "./styles/App.scss";
import Header from "./components/elements/Header/Header";
import AppRouter from "./components/elements/AppRouter/AppRouter";

function App() {

  return (
    <div className="App">
        <Header/>
        <AppRouter/>
        {/* <AppRouter/> */}
    </div>
  );
}

export default App;
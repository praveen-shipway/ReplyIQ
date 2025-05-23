import './App.css'
import ChatWindow from './components/ChatWindow'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap-icons/font/bootstrap-icons.css' 



function App() {

  return (
    <>
       <div className=" bg-light d-flex " style={{borderRadius:'15px', width:'400px'}}>
          <div className="w-100 border shadow  bg-white d-flex flex-column " 
          style={{ maxWidth: 400, height: '90vh',  borderRadius: '15px', // Rounded corners
                   boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)', // Soft shadow
                   overflow: 'hidden', // Clips inner corners
                   backgroundColor: '#fff', // Ensure background isn't transparent
                   display: 'flex',
                   flexDirection: 'column' }} >
            <ChatWindow />
          </div>
      </div>
    </>
  )
}

export default App

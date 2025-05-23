
export default function ChatHeader( ) {
  
  // const [open, setOpen] = useState(false)

  // const toggleDropdown = () => setOpen(!open)
  // const closeDropdown = () => setOpen(false)

  return (
    <>
   <div className="d-flex align-items-center justify-content-between border-bottom" style={{ padding: '5px' }}>
  <div className="d-flex align-items-center gap-2">
    <img
      src="src/assets/profile.avif"
      alt="React Logo"
      className="rounded-circle"
      width="40"
      height="40"
    />
    <div className="d-grid gap-0">
        <div className="fw-bold ">ReplyIQ</div>
    </div>
  </div>
{/* 
  <div className="dropdown">
    <i
      className="bi bi-three-dots-vertical"
      style={{ fontSize: '1.5rem', cursor: 'pointer' }}
      onClick={toggleDropdown}
      role="button"
      aria-expanded={open}
      aria-haspopup="true"
      aria-label="Toggle menu"
    />
    <ul
      className={`dropdown-menu dropdown-menu${open ? ' show' : ''}` }  
      style={{
          position: 'absolute',
    right: 0,
    top: '100%',
    border: '1px solid rgba(0, 0, 0, 0.1)', 
    boxShadow: '0px 4px 12px rgba(0, 0, 0, 0.15)',
    borderRadius: '8px',
    minWidth: '160px',
    zIndex: 1000,
        }}
      onClick={closeDropdown}
    >
      <li>  <button className="dropdown-item" type="button" onClick={onNewChat}>New chat</button></li>
      <li><button className="dropdown-item" type="button">Settings</button></li>
      <li><hr className="dropdown-divider" /></li>
      <li><button className="dropdown-item text-danger" type="button">Logout</button></li>
    </ul>
  </div> */}
</div>

    </>
  )
}

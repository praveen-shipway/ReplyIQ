import { useState } from 'react'


export default function ChatInput({ onSend }) {
  const [text, setText] = useState('')

  const handleSend = () => {
    if (text.trim() !== '') {
      onSend(text)
      setText('')
    }
  }

  return (
   <div className="p-2 d-flex align-items-center gap-2 input-area ">
      <input
        type="text"
        className="form-control rounded-pill"
        placeholder="Type your message..."
        value={text}
        onChange={(e) => setText(e.target.value)}
        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
      />
      <button className="btn btn-primary rounded-pill px-4 " onClick={handleSend}>
        Send
      </button>
    </div>
  )
}
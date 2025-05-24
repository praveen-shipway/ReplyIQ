import { useState , useEffect, useRef} from 'react'
import ChatHeader from './ChatHeader'
import MessageBubble from './MessageBubble'
import ChatInput from './ChatInput'
import axios from 'axios'
import QuickReplies from './QuickReplies'

export default function ChatWindow() {
  

  const [messages, setMessages] = useState([
    { from: 'bot', text: 'Hi! How can I help you today?' },
  ])

  const [isTyping, setIsTyping] = useState(false)

  const [hasUserSentMessage, setHasUserSentMessage] = useState(false);

  const messagesEndRef = useRef(null);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);


  const sendMessage = async (text) => {
    const userMessage = { from: 'user', text };
    if (!hasUserSentMessage) {
      setHasUserSentMessage(true);
    }
    setMessages((prev) => [...prev, userMessage]);
    setIsTyping(true);

  try {
      const res= await axios.post('http://localhost:8000/chat', {
          "user_id": "puneet05",
          "session_id": "session123",
          "message": text
        }, 
        {
          headers: {
              "Content-Type": "application/json", 
          }
        }
      );

      // console.log('res', res);

      setMessages((prev) => [...prev, { from: 'bot', text: res.data.reply }]);
    } catch (err) {
      setMessages((prev) => [...prev, { from: 'bot', text: 'Something went wrong!' }],err);
    }
  };

 const sendReaction = (msgIndex, emoji) => {
  setMessages((prevMessages) =>
    prevMessages.map((msg, idx) =>
      idx === msgIndex
        ? { ...msg, reactions: [emoji] }
        : msg
      )
    )
    
  }

  return (
    <>
      <div className="d-flex flex-column h-100  ">
        <ChatHeader isTyping={isTyping} />
        
        {/* Scrollable message list */}
        <div className="flex-grow-1 overflow-auto d-flex flex-column chat-scrollbar chat-window">
         {(() => {
            let botCount = 0;
            return messages.map((msg, idx) => {
              const botIndex = msg.from === 'bot' ? ++botCount : null;
              return (
                <MessageBubble
                  key={idx}
                  index={idx}
                  from={msg.from}
                  text={msg.text}
                  reactions={msg.reactions}
                  botIndex={botIndex}
                  onReact={(emoji) => sendReaction(idx, emoji)}
                />
              );
            });
          })()}
            <div ref={messagesEndRef} />
        </div>
          {/* Show QuickReplies only if user hasn't sent a message */}
        <div style={{ display: hasUserSentMessage ? 'none' : 'block' }}>
          {/* <QuickReplies onSend={sendMessage} /> */}
        </div>

        {/* <QuickReplies onSend={sendMessage} /> */}
        <ChatInput onSend={sendMessage} />
      </div>
    </>
  )
}

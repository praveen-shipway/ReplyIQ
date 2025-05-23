import '../App.css'
import { useState } from 'react'

export default function MessageBubble({ from, text, reactions = [], onReact , botIndex}) {
  const [showReactions, setShowReactions] = useState(false)
  const availableReactions = ['❤️', '😂', '👍', '😮', '😢']

const isBot = from === 'bot'

  return (
    <div
      className={`d-flex mb-2 ${from === 'user' ? 'justify-content-end' : 'justify-content-start'}`}
      onMouseEnter={() => isBot && setShowReactions(true)}
      onMouseLeave={() => isBot && setShowReactions(false)}
    >
      <div className="position-relative">
        <div
          className={`text-small ${
            from === 'user'
              ? 'user-bubble text-white border-radius-str-chat bg-secondary'
              : 'bot-bubble text-white border-radius-str-bot bg-primary'
          }`}
          style={{
            maxWidth: '65%',
            display: 'inline',
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            padding: '6px 12px',
            margin: '0px 3px',
          }}
        >
          {text}
        </div>

        {/* Show existing reactions below message */}
        {reactions.length > 0 && (
          <div className="mt-1 d-flex gap-1 justify-content-end">
            {reactions.map((r, i) => (
              <span key={i} style={{ fontSize: '14px' }}>
                {r}
              </span>
            ))}
          </div>
        )}

        {/* Reactions picker on hover */}
        {showReactions && from === 'bot' && botIndex >= 2 &&(
          <div
            className="position-absolute right-0  bg-none rounded shadow-sm d-flex p-1 gap-2"
            style={{ zIndex: 100, top:'13%', right:'-63%' }}
          >
            {availableReactions.map((emoji) => (
              <span
                key={emoji}
                style={{ cursor: 'pointer', fontSize: '14px' }}
                onClick={() => onReact(emoji)}
              >
                {emoji}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

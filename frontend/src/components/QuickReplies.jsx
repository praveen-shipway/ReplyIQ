export default function QuickReplies({ onSend }) {
  const suggestions = [
   'Track my order',
  'Reschedule my order',
  'Cancel my order',
  ]

  return (
    <div className="px-1 py-2 border-top d-flex flex-wrap gap-2">
      {suggestions.map((text, idx) => (
        <button
          key={idx}
          className="btn btn-outline-secondary btn-sm rounded-pill"
          onClick={() => onSend(text)}
        >
          {text}
        </button>
      ))}
    </div>
  )
}

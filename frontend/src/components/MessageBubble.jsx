import '../App.css'
import { ThumbsUp, ThumbsDown } from 'lucide-react'

export default function MessageBubble({ from, text,   }) {
  // const availableReactions = [
  //   { id: 1, icon: <ThumbsUp size={20} strokeWidth={1.5} /> },   // like = 1
  //   { id: 0, icon: <ThumbsDown size={20} strokeWidth={1.5} /> }, // dislike = 0
  // ];

  // const [hasReacted, setHasReacted] = useState(false);

  // const handleReact = (reactionId) => {
  //   let value;
  //   if (reactionId === 1) {
  //     value = 1;
  //   } else if (reactionId === 0) {
  //     value = -1;
  //   }

  //   console.log('Reaction value:', value);
  //   onReact(reactionId); // send id to parent
  //   setHasReacted(true);
  // };

  return (
    <div
      className={`d-flex mb-2 ${from === 'user' ? 'justify-content-end ms-5 mt-2' : 'justify-content-start me-5 mt-2'}`}
    >
      <div className="position-relative">
        <div
          className={`text-small ${
            from === 'user'
              ? 'user-bubble  border-radius-str-chat '
              : 'bot-bubble  border-radius-str-bot '
          }`}
          style={{
            maxWidth: '100%',
            whiteSpace: 'normal',
            wordWrap: 'anywhere',
            padding: '6px 12px',
            margin: '0px 3px',
          }}
        >
          {text}
        </div>

        {/* Reactions display */}
        {/* {reactions.length > 0 && (
          <div className="ms-1 mt-1 d-flex gap-2 justify-content-start">
            {reactions.map((reaction, i) => {
              const match = availableReactions.find(r => r.id === reaction);
              return (
                <span key={i} style={{ fontSize: '14px' }}>
                  {match?.icon}
                </span>
              );
            })}
          </div>
        )} */}

        {/* Reaction picker */}
        {/* {from === 'bot' && botIndex >= 2 && !hasReacted && (
          <div
            className="position-absolute right-0 bg-none rounded d-flex p-1 gap-3"
            style={{ zIndex: 100 }}
          >
            {availableReactions.map(({ id, icon }) => (
              <span
                key={id}
                style={{ cursor: 'pointer' }}
                onClick={() => handleReact(id)}
              >
                {icon}
              </span>
            ))}
          </div>
        )} */}
      </div>
    </div>
  );
}

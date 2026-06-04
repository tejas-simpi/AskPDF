import Markdown from 'react-markdown';
import './ChatMessage.css';

export default function ChatMessage({ role, content }) {
  const isUser = role === 'user';

  return (
    <div className={`chat-message ${isUser ? 'chat-message-user' : 'chat-message-assistant'}`}>
      <div className="chat-avatar">
        {isUser ? '👤' : '✨'}
      </div>
      <div className="chat-bubble">
        <div className="chat-bubble-content">
          {isUser ? (
            content
          ) : (
            <Markdown>{content}</Markdown>
          )}
        </div>
      </div>
    </div>
  );
}

import { useRef, useEffect } from 'react';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { TypingIndicator } from '../UI/LoadingSpinner';
import EmptyState from '../UI/EmptyState';
import './ChatWindow.css';

export default function ChatWindow({
  messages,
  onSend,
  loading,
  emptyIcon = '💬',
  emptyTitle = 'Start a Conversation',
  emptyDesc = 'Type a message below to begin chatting',
  placeholder = 'Type your message...',
}) {
  const scrollRef = useRef(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, loading]);

  return (
    <div className="chat-window">
      <div className="chat-messages" ref={scrollRef}>
        {messages.length === 0 ? (
          <EmptyState
            icon={emptyIcon}
            title={emptyTitle}
            description={emptyDesc}
          />
        ) : (
          <>
            {messages.map((msg, i) => (
              <ChatMessage key={i} role={msg.role} content={msg.content} />
            ))}
            {loading && (
              <div className="chat-message chat-message-assistant">
                <div className="chat-avatar">✨</div>
                <div className="chat-bubble">
                  <TypingIndicator />
                </div>
              </div>
            )}
          </>
        )}
      </div>
      <ChatInput onSend={onSend} disabled={loading} placeholder={placeholder} />
    </div>
  );
}

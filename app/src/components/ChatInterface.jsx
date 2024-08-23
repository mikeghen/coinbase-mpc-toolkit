import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ScrollArea } from "@/components/ui/scroll-area"
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const scrollAreaRef = useRef(null);
  const queryClient = useQueryClient();

  const sendMessage = async (message) => {
    const response = await axios.post('https://localhost:5000/query-agent', { message });
    return response.data;
  };

  const mutation = useMutation({
    mutationFn: sendMessage,
    onSuccess: (data) => {
      setMessages(prev => [...prev, { text: data, isUser: false }]);
      queryClient.invalidateQueries('messages');
    },
  });

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setMessages(prev => [...prev, { text: inputMessage, isUser: true }]);
      mutation.mutate(inputMessage);
      setInputMessage('');
    }
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  return (
    <div className="flex flex-col h-full bg-gray-200">
      <div className="flex-1 overflow-hidden p-4">
        <ScrollArea className="h-full pr-4" ref={scrollAreaRef}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.isUser ? 'text-right' : 'text-left'
              }`}
            >
              <div
                className={`inline-block p-3 rounded-2xl max-w-[70%] ${
                  message.isUser
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-black'
                }`}
              >
                {message.text}
              </div>
            </div>
          ))}
        </ScrollArea>
      </div>
      <div className="p-4 bg-gray-100 border-t border-gray-300">
        <div className="flex">
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="iMessage"
            className="flex-1 mr-2 rounded-full"
          />
          <Button onClick={handleSendMessage} className="rounded-full">Send</Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;
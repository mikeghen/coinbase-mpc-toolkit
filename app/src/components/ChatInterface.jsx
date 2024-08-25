import React, { useState, useEffect, useRef } from 'react';
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const ChatInterface = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [userId, setUserId] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef(null);
  const latestMessageRef = useRef(null);
  const queryClient = useQueryClient();

  const generateUserId = () => {
    const timestamp = Date.now().toString(36);
    const randomNum = Math.random().toString(36).substring(2, 10);
    return `${timestamp}-${randomNum}`;
  };

  useEffect(() => {
    const newUserId = generateUserId();
    const initialMessage = "Hello";
    setMessages(prev => [...prev, { text: initialMessage, isUser: true }]);
    mutation.mutate({
      message: initialMessage,
      user_id: newUserId,
    });

    setUserId(newUserId);
  }, []);

  const sendMessage = async (payload) => {
    const response = await axios.post(`${import.meta.env.VITE_API_BASE_URL}/query-agent`, payload);
    return response.data;
  };

  const mutation = useMutation({
    mutationFn: sendMessage,
    onMutate: () => {
      setTimeout(() => {
        setIsTyping(true);  // Show typing indicator after a brief delay
      }, 500); // 500ms delay before showing "Malice is typing..."
    },
    onSuccess: (data) => {
      setMessages(prev => [...prev, { text: data, isUser: false }]);
      setIsTyping(false);  // Hide typing indicator when mutation ends
      queryClient.invalidateQueries('messages');
    },
    onError: () => {
      setIsTyping(false);  // Hide typing indicator if there is an error
    }
  });

  const handleSendMessage = () => {
    if (inputMessage.trim()) {
      setMessages(prev => [...prev, { text: inputMessage, isUser: true }]);
      mutation.mutate({
        message: inputMessage,
        user_id: userId,
      });
      setInputMessage('');
    }
  };

  useEffect(() => {
    if (latestMessageRef.current) {
      latestMessageRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isTyping]);

  // Function to preprocess message by replacing double newlines with <br>
  const preprocessMessage = (message) => {
    return message.replace(/\n\n/g, '  \n');  // Replace \n\n with markdown line break
  };

  return (
    <div className="flex flex-col h-full bg-gray-200">
      <div className="bg-yellow-500 text-white p-4">
        This demonstration is for research purposes only. Only send <strong>Base Sepolia ETH</strong> to the wallet you are given.
      </div>
      <div className="flex-1 overflow-hidden p-4">
        <ScrollArea className="h-full pr-4 overflow-auto" ref={scrollAreaRef}>
          {messages.map((message, index) => (
            <div
              key={index}
              className={`mb-4 ${
                message.isUser ? 'text-right' : 'text-left'
              }`}
              ref={index === messages.length - 1 ? latestMessageRef : null}
            >
              <div
                className={`inline-block p-3 rounded-2xl max-w-[70%] ${
                  message.isUser
                    ? 'bg-blue-500 text-white'
                    : 'bg-white text-black'
                }`}
              >
                <ReactMarkdown>{preprocessMessage(message.text)}</ReactMarkdown>
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="mb-4 text-left" ref={latestMessageRef}>
              <div className="inline-block p-3 rounded-2xl max-w-[70%] bg-white text-black">
                <span className="typing-animation">Malice is typing...</span>
              </div>
            </div>
          )}
        </ScrollArea>
      </div>
      <div className="p-4 bg-gray-100 border-t border-gray-300">
        <div className="flex">
          <Input
            type="text"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
            placeholder="Type a message..."
            className="flex-1 mr-2 rounded-full"
          />
          <Button onClick={handleSendMessage} className="rounded-full">Send</Button>
        </div>
      </div>
    </div>
  );
};

export default ChatInterface;

import { useState, useEffect, useRef } from 'react';
import { Widget } from '../../../App';
import { ScrollArea } from '../../ui/scroll-area';
import { Input } from '../../ui/input';
import { Button } from '../../ui/button';

interface TerminalWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

const mockMessages = [
  'System initialized',
  'Connected to device',
  'Temperature: 25.3°C',
  'Voltage: 3.3V',
  'Data received: 0xAA 0xBB 0xCC',
  'Status: OK',
];

export default function TerminalWidget({ widget, theme, isConnected }: TerminalWidgetProps) {
  const [messages, setMessages] = useState<string[]>([]);
  const [input, setInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const newMsg = mockMessages[Math.floor(Math.random() * mockMessages.length)];
        setMessages(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${newMsg}`]);
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  useEffect(() => {
    if (widget.config.autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, widget.config.autoScroll]);

  const handleSend = () => {
    if (input.trim()) {
      setMessages(prev => [...prev, `> ${input}`]);
      setInput('');
    }
  };

  return (
    <div className="h-full flex flex-col p-3">
      <ScrollArea className="flex-1 mb-2">
        <div
          ref={scrollRef}
          className={`p-3 rounded ${
            theme === 'dark' ? 'bg-[#1A1A1A]' : 'bg-gray-50'
          }`}
          style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '12px' }}
        >
          {messages.map((msg, idx) => (
            <div key={idx} className="mb-1 text-green-400">
              {msg}
            </div>
          ))}
        </div>
      </ScrollArea>
      <div className="flex gap-2">
        <Input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type command..."
          className={`text-sm ${
            theme === 'dark' ? 'bg-[#1A1A1A] border-gray-700' : 'bg-gray-50 border-gray-300'
          }`}
          style={{ fontFamily: 'JetBrains Mono, monospace' }}
        />
        <Button 
          onClick={handleSend}
          size="sm"
          className="bg-[#0A84FF] hover:bg-[#0066CC] text-white"
        >
          Send
        </Button>
      </div>
    </div>
  );
}

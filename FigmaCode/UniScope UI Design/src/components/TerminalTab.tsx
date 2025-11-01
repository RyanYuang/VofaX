import { useState, useEffect, useRef } from 'react';
import { Trash2, Clock } from 'lucide-react';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Checkbox } from './ui/checkbox';
import { Label } from './ui/label';
import { ScrollArea } from './ui/scroll-area';

interface TerminalTabProps {
  theme: 'dark' | 'light';
  isConnected: boolean;
  setRxBytes: (bytes: number) => void;
  setTxBytes: (bytes: number) => void;
}

const mockRxData = [
  { time: '14:32:45.123', data: 'System initialized', hex: '53 79 73 74 65 6D 20 69 6E 69 74' },
  { time: '14:32:45.456', data: 'Temperature: 25.3°C', hex: '54 65 6D 70 3A 20 32 35 2E 33 C2 B0 43' },
  { time: '14:32:46.789', data: 'Sensor data: [1024, 2048, 512]', hex: 'AA BB 04 00 08 00 02 00' },
  { time: '14:32:47.012', data: 'Status: OK', hex: '53 74 61 74 75 73 3A 20 4F 4B' },
  { time: '14:32:48.345', data: 'Voltage: 3.3V', hex: '56 6F 6C 74 61 67 65 3A 20 33 2E 33 56' },
];

export default function TerminalTab({ theme, isConnected, setRxBytes, setTxBytes }: TerminalTabProps) {
  const [displayMode, setDisplayMode] = useState<'ascii' | 'hex'>('ascii');
  const [autoScroll, setAutoScroll] = useState(true);
  const [showTimestamp, setShowTimestamp] = useState(true);
  const [rxMessages, setRxMessages] = useState(mockRxData);
  const [txInput, setTxInput] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (autoScroll && scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [rxMessages, autoScroll]);

  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const newMessage = {
          time: new Date().toLocaleTimeString('en-US', { hour12: false, fractionalSecondDigits: 3 } as any),
          data: `Data packet ${Math.floor(Math.random() * 1000)}`,
          hex: Array.from({ length: 8 }, () => Math.floor(Math.random() * 256).toString(16).toUpperCase().padStart(2, '0')).join(' ')
        };
        setRxMessages(prev => [...prev, newMessage]);
        setRxBytes(prev => prev + Math.floor(Math.random() * 100));
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isConnected, setRxBytes]);

  const handleSend = () => {
    if (txInput.trim()) {
      setTxBytes(prev => prev + txInput.length);
      setTxInput('');
    }
  };

  const handleClear = () => {
    setRxMessages([]);
  };

  return (
    <div className="h-full flex flex-col p-4 gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Button
              variant={displayMode === 'ascii' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDisplayMode('ascii')}
              className={displayMode === 'ascii' ? 'bg-[#0078D4]' : ''}
            >
              ASCII
            </Button>
            <Button
              variant={displayMode === 'hex' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setDisplayMode('hex')}
              className={displayMode === 'hex' ? 'bg-[#0078D4]' : ''}
            >
              HEX
            </Button>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox 
              id="autoscroll" 
              checked={autoScroll}
              onCheckedChange={(checked) => setAutoScroll(checked as boolean)}
            />
            <Label htmlFor="autoscroll" className="text-sm cursor-pointer">Auto-scroll</Label>
          </div>

          <div className="flex items-center gap-2">
            <Checkbox 
              id="timestamp" 
              checked={showTimestamp}
              onCheckedChange={(checked) => setShowTimestamp(checked as boolean)}
            />
            <Label htmlFor="timestamp" className="text-sm cursor-pointer">
              <Clock className="w-3.5 h-3.5 inline mr-1" />
              Timestamp
            </Label>
          </div>
        </div>

        <Button
          variant="outline"
          size="sm"
          onClick={handleClear}
          className={theme === 'dark' ? 'border-gray-700 hover:bg-gray-700' : 'border-gray-300'}
        >
          <Trash2 className="w-4 h-4 mr-2" />
          Clear
        </Button>
      </div>

      <div 
        ref={scrollRef}
        className={`flex-1 rounded-lg p-4 overflow-y-auto ${
          theme === 'dark' ? 'bg-[#0D0D0D] border border-gray-800' : 'bg-gray-50 border border-gray-200'
        }`}
        style={{ fontFamily: 'JetBrains Mono, monospace', fontSize: '13px' }}
      >
        {rxMessages.map((msg, idx) => (
          <div key={idx} className="mb-1 flex gap-3">
            {showTimestamp && (
              <span className="text-gray-500">{msg.time}</span>
            )}
            <span className={displayMode === 'hex' ? 'text-[#0078D4]' : theme === 'dark' ? 'text-green-400' : 'text-green-600'}>
              {displayMode === 'ascii' ? msg.data : msg.hex}
            </span>
          </div>
        ))}
      </div>

      <div className="space-y-2">
        <Label className="text-xs text-gray-400">TX INPUT</Label>
        <div className="flex gap-2">
          <Textarea 
            value={txInput}
            onChange={(e) => setTxInput(e.target.value)}
            placeholder="Type your message here..."
            className={`min-h-[80px] ${
              theme === 'dark' ? 'bg-[#0D0D0D] border-gray-800' : 'bg-gray-50 border-gray-200'
            }`}
            style={{ fontFamily: 'JetBrains Mono, monospace' }}
          />
          <Button 
            onClick={handleSend}
            disabled={!isConnected}
            className="bg-[#0078D4] hover:bg-[#005a9e] text-white"
          >
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}

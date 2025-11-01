import { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Label } from './ui/label';
import { Slider } from './ui/slider';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Switch } from './ui/switch';

interface OscilloscopeTabProps {
  theme: 'dark' | 'light';
  isConnected: boolean;
}

export default function OscilloscopeTab({ theme, isConnected }: OscilloscopeTabProps) {
  const [data, setData] = useState<any[]>([]);
  const [timeBase, setTimeBase] = useState([50]);
  const [triggerMode, setTriggerMode] = useState('Auto');
  const [showGrid, setShowGrid] = useState(true);

  useEffect(() => {
    const generateData = () => {
      const newData = [];
      const time = Date.now();
      
      for (let i = 0; i < 100; i++) {
        newData.push({
          time: i,
          ch1: Math.sin(i * 0.1) * 2 + Math.random() * 0.3,
          ch2: Math.cos(i * 0.15) * 1.5 + Math.random() * 0.2,
          ch3: Math.sin(i * 0.08) * 1.8 + 0.5,
          ch4: Math.cos(i * 0.12) * 1.2 - 0.5,
        });
      }
      
      return newData;
    };

    setData(generateData());

    if (isConnected) {
      const interval = setInterval(() => {
        setData(generateData());
      }, 100);
      return () => clearInterval(interval);
    }
  }, [isConnected]);

  return (
    <div className="h-full flex flex-col p-4 gap-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-6">
          <div className="flex items-center gap-3">
            <Label className="text-sm">Time Base</Label>
            <div className="w-48">
              <Slider 
                value={timeBase}
                onValueChange={setTimeBase}
                min={10}
                max={100}
                step={10}
                className="cursor-pointer"
              />
            </div>
            <span className="text-sm text-gray-400 w-20">{timeBase[0]}ms/div</span>
          </div>

          <div className="flex items-center gap-2">
            <Label className="text-sm">Trigger</Label>
            <Select value={triggerMode} onValueChange={setTriggerMode}>
              <SelectTrigger className={`w-32 ${theme === 'dark' ? 'bg-[#252525] border-gray-700' : 'bg-white border-gray-300'}`}>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Auto">Auto</SelectItem>
                <SelectItem value="Normal">Normal</SelectItem>
                <SelectItem value="Single">Single</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-2">
            <Switch 
              id="grid" 
              checked={showGrid}
              onCheckedChange={setShowGrid}
            />
            <Label htmlFor="grid" className="text-sm cursor-pointer">Grid</Label>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#0078D4]"></div>
            <span className="text-xs">CH1</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#FF8C00]"></div>
            <span className="text-xs">CH2</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#00C853]"></div>
            <span className="text-xs">CH3</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-3 h-3 rounded-full bg-[#9C27B0]"></div>
            <span className="text-xs">CH4</span>
          </div>
        </div>
      </div>

      <div className={`flex-1 rounded-lg p-4 ${
        theme === 'dark' ? 'bg-[#0D0D0D] border border-gray-800' : 'bg-gray-50 border border-gray-200'
      }`}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            {showGrid && (
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={theme === 'dark' ? '#2a2a2a' : '#e0e0e0'} 
              />
            )}
            <XAxis 
              dataKey="time" 
              stroke={theme === 'dark' ? '#666' : '#999'}
              tick={{ fill: theme === 'dark' ? '#666' : '#999' }}
            />
            <YAxis 
              stroke={theme === 'dark' ? '#666' : '#999'}
              tick={{ fill: theme === 'dark' ? '#666' : '#999' }}
              domain={[-3, 3]}
            />
            <Tooltip 
              contentStyle={{
                backgroundColor: theme === 'dark' ? '#252525' : '#fff',
                border: `1px solid ${theme === 'dark' ? '#444' : '#ccc'}`,
                borderRadius: '6px',
                color: theme === 'dark' ? '#fff' : '#000'
              }}
            />
            <Line type="monotone" dataKey="ch1" stroke="#0078D4" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="ch2" stroke="#FF8C00" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="ch3" stroke="#00C853" strokeWidth={2} dot={false} isAnimationActive={false} />
            <Line type="monotone" dataKey="ch4" stroke="#9C27B0" strokeWidth={2} dot={false} isAnimationActive={false} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="grid grid-cols-4 gap-4">
        {[
          { ch: 'CH1', color: '#0078D4', voltage: '2.34V', freq: '10.2Hz' },
          { ch: 'CH2', color: '#FF8C00', voltage: '1.82V', freq: '8.5Hz' },
          { ch: 'CH3', color: '#00C853', voltage: '2.01V', freq: '9.1Hz' },
          { ch: 'CH4', color: '#9C27B0', voltage: '1.45V', freq: '7.8Hz' },
        ].map((channel) => (
          <div 
            key={channel.ch}
            className={`p-3 rounded-lg border ${
              theme === 'dark' ? 'bg-[#252525] border-gray-800' : 'bg-gray-50 border-gray-200'
            }`}
          >
            <div className="flex items-center gap-2 mb-2">
              <div className="w-2 h-2 rounded-full" style={{ backgroundColor: channel.color }}></div>
              <span className="text-xs">{channel.ch}</span>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Vpp:</span>
                <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{channel.voltage}</span>
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-gray-400">Freq:</span>
                <span style={{ fontFamily: 'JetBrains Mono, monospace' }}>{channel.freq}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

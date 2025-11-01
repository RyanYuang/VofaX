import { useEffect, useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';
import { Widget } from '../../../App';

interface OscilloscopeWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

const COLORS = ['#0A84FF', '#FF9F0A', '#30D158', '#BF5AF2', '#FF453A', '#64D2FF', '#FFD60A', '#FF375F'];

export default function OscilloscopeWidget({ widget, theme, isConnected }: OscilloscopeWidgetProps) {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const generateData = () => {
      const newData = [];
      const channels = widget.dataBinding?.channels || ['I0'];
      
      for (let i = 0; i < 100; i++) {
        const point: any = { time: i };
        channels.forEach((ch, idx) => {
          point[ch] = Math.sin(i * 0.1 + idx) * 2 + Math.random() * 0.3;
        });
        newData.push(point);
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
  }, [isConnected, widget.dataBinding?.channels]);

  const channels = widget.dataBinding?.channels || ['I0'];

  return (
    <div className="h-full p-4">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          {widget.config.showGrid && (
            <CartesianGrid 
              strokeDasharray="3 3" 
              stroke={theme === 'dark' ? '#2a2a2a' : '#e0e0e0'} 
            />
          )}
          <XAxis 
            dataKey="time" 
            stroke={theme === 'dark' ? '#666' : '#999'}
            tick={{ fill: theme === 'dark' ? '#666' : '#999', fontSize: 11 }}
            label={{ value: 'Time (ms)', position: 'insideBottom', offset: -5, fill: theme === 'dark' ? '#666' : '#999' }}
          />
          <YAxis 
            stroke={theme === 'dark' ? '#666' : '#999'}
            tick={{ fill: theme === 'dark' ? '#666' : '#999', fontSize: 11 }}
            domain={widget.config.yAxis === 'auto' ? ['auto', 'auto'] : [-3, 3]}
          />
          {channels.map((ch, idx) => (
            <Line 
              key={ch}
              type="monotone" 
              dataKey={ch} 
              stroke={COLORS[idx % COLORS.length]} 
              strokeWidth={2} 
              dot={false} 
              isAnimationActive={false}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

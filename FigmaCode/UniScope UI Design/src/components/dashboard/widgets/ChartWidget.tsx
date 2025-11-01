import { useEffect, useState } from 'react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { Widget } from '../../../App';

interface ChartWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

const COLORS = ['#0A84FF', '#FF9F0A', '#30D158'];

export default function ChartWidget({ widget, theme, isConnected }: ChartWidgetProps) {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    const generateData = () => {
      const newData = [];
      const channels = widget.dataBinding?.channels || ['I0'];
      
      for (let i = 0; i < 20; i++) {
        const point: any = { name: `T${i}` };
        channels.forEach((ch) => {
          point[ch] = Math.random() * 100;
        });
        newData.push(point);
      }
      
      return newData;
    };

    setData(generateData());

    if (isConnected) {
      const interval = setInterval(() => {
        setData(generateData());
      }, 2000);
      return () => clearInterval(interval);
    }
  }, [isConnected, widget.dataBinding?.channels]);

  const channels = widget.dataBinding?.channels || ['I0'];
  const ChartComponent = widget.config.chartType === 'bar' ? BarChart : LineChart;
  const DataComponent = widget.config.chartType === 'bar' ? Bar : Line;

  return (
    <div className="h-full p-4">
      <ResponsiveContainer width="100%" height="100%">
        <ChartComponent data={data}>
          <CartesianGrid 
            strokeDasharray="3 3" 
            stroke={theme === 'dark' ? '#2a2a2a' : '#e0e0e0'} 
          />
          <XAxis 
            dataKey="name" 
            stroke={theme === 'dark' ? '#666' : '#999'}
            tick={{ fill: theme === 'dark' ? '#666' : '#999', fontSize: 11 }}
          />
          <YAxis 
            stroke={theme === 'dark' ? '#666' : '#999'}
            tick={{ fill: theme === 'dark' ? '#666' : '#999', fontSize: 11 }}
          />
          <Legend />
          {channels.map((ch, idx) => (
            <DataComponent 
              key={ch}
              type="monotone" 
              dataKey={ch} 
              stroke={COLORS[idx % COLORS.length]}
              fill={COLORS[idx % COLORS.length]}
              strokeWidth={2}
            />
          ))}
        </ChartComponent>
      </ResponsiveContainer>
    </div>
  );
}

import { useState, useEffect } from 'react';
import { Widget } from '../../../App';

interface GaugeWidgetProps {
  widget: Widget;
  theme: 'dark' | 'light';
  isConnected: boolean;
}

export default function GaugeWidget({ widget, theme, isConnected }: GaugeWidgetProps) {
  const [value, setValue] = useState(0);

  useEffect(() => {
    if (isConnected) {
      const interval = setInterval(() => {
        const min = widget.config.min || 0;
        const max = widget.config.max || 100;
        setValue(min + Math.random() * (max - min));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [isConnected, widget.config.min, widget.config.max]);

  const min = widget.config.min || 0;
  const max = widget.config.max || 100;
  const percentage = ((value - min) / (max - min)) * 100;
  const angle = (percentage / 100) * 270 - 135;

  return (
    <div className="h-full flex items-center justify-center p-4">
      <div className="relative" style={{ width: '200px', height: '200px' }}>
        <svg viewBox="0 0 200 200" className="transform -rotate-90">
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke={theme === 'dark' ? '#2A2A2A' : '#E5E7EB'}
            strokeWidth="12"
          />
          <circle
            cx="100"
            cy="100"
            r="80"
            fill="none"
            stroke="url(#gradient)"
            strokeWidth="12"
            strokeDasharray={`${(percentage / 100) * 502} 502`}
            strokeLinecap="round"
            className="transition-all duration-500"
          />
          <defs>
            <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor="#0A84FF" />
              <stop offset="50%" stopColor="#30D158" />
              <stop offset="100%" stopColor="#FF9F0A" />
            </linearGradient>
          </defs>
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <div className="text-3xl" style={{ fontFamily: 'JetBrains Mono, monospace' }}>
            {value.toFixed(1)}
          </div>
          <div className="text-sm text-gray-400">{widget.config.unit}</div>
        </div>
      </div>
    </div>
  );
}

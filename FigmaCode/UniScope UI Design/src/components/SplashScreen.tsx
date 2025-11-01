import { Radar } from 'lucide-react';

export default function SplashScreen() {
  return (
    <div className="h-screen w-screen bg-gradient-to-br from-[#1E1E1E] via-[#252525] to-[#1A1A1A] flex items-center justify-center">
      <div className="text-center">
        <div className="relative mb-8">
          <div className="absolute inset-0 bg-[#0078D4] blur-3xl opacity-30 animate-pulse"></div>
          <div className="relative bg-gradient-to-br from-[#0078D4] to-[#005a9e] p-6 rounded-2xl shadow-2xl">
            <Radar className="w-16 h-16 text-white animate-spin" style={{ animationDuration: '3s' }} />
          </div>
        </div>
        
        <h1 className="text-white mb-2" style={{ fontFamily: 'Inter, sans-serif' }}>
          UniScope
        </h1>
        
        <p className="text-gray-400">
          Universal Serial Debug Hub
        </p>
        
        <div className="mt-8 flex items-center justify-center gap-2">
          <div className="w-2 h-2 bg-[#0078D4] rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-[#0078D4] rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-[#0078D4] rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}

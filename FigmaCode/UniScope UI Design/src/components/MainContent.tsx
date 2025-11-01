import { useState } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import TerminalTab from './TerminalTab';
import OscilloscopeTab from './OscilloscopeTab';
import DataLoggerTab from './DataLoggerTab';
import ProtocolAnalyzerTab from './ProtocolAnalyzerTab';

interface MainContentProps {
  theme: 'dark' | 'light';
  isConnected: boolean;
  setRxBytes: (bytes: number) => void;
  setTxBytes: (bytes: number) => void;
}

export default function MainContent({ theme, isConnected, setRxBytes, setTxBytes }: MainContentProps) {
  const [activeTab, setActiveTab] = useState('terminal');

  return (
    <div className={`flex-1 flex flex-col ${theme === 'dark' ? 'bg-[#1E1E1E]' : 'bg-white'}`}>
      <Tabs value={activeTab} onValueChange={setActiveTab} className="flex-1 flex flex-col">
        <div className={`border-b px-4 ${theme === 'dark' ? 'border-gray-800' : 'border-gray-200'}`}>
          <TabsList className={`${theme === 'dark' ? 'bg-transparent' : 'bg-transparent'} h-12`}>
            <TabsTrigger 
              value="terminal"
              className={`data-[state=active]:${theme === 'dark' ? 'bg-[#252525]' : 'bg-gray-100'} data-[state=active]:border-b-2 data-[state=active]:border-[#0078D4]`}
            >
              Terminal
            </TabsTrigger>
            <TabsTrigger 
              value="oscilloscope"
              className={`data-[state=active]:${theme === 'dark' ? 'bg-[#252525]' : 'bg-gray-100'} data-[state=active]:border-b-2 data-[state=active]:border-[#0078D4]`}
            >
              Oscilloscope
            </TabsTrigger>
            <TabsTrigger 
              value="logger"
              className={`data-[state=active]:${theme === 'dark' ? 'bg-[#252525]' : 'bg-gray-100'} data-[state=active]:border-b-2 data-[state=active]:border-[#0078D4]`}
            >
              Data Logger
            </TabsTrigger>
            <TabsTrigger 
              value="analyzer"
              className={`data-[state=active]:${theme === 'dark' ? 'bg-[#252525]' : 'bg-gray-100'} data-[state=active]:border-b-2 data-[state=active]:border-[#0078D4]`}
            >
              Protocol Analyzer
            </TabsTrigger>
          </TabsList>
        </div>

        <div className="flex-1 overflow-hidden">
          <TabsContent value="terminal" className="h-full m-0">
            <TerminalTab theme={theme} isConnected={isConnected} setRxBytes={setRxBytes} setTxBytes={setTxBytes} />
          </TabsContent>
          
          <TabsContent value="oscilloscope" className="h-full m-0">
            <OscilloscopeTab theme={theme} isConnected={isConnected} />
          </TabsContent>
          
          <TabsContent value="logger" className="h-full m-0">
            <DataLoggerTab theme={theme} isConnected={isConnected} />
          </TabsContent>
          
          <TabsContent value="analyzer" className="h-full m-0">
            <ProtocolAnalyzerTab theme={theme} isConnected={isConnected} />
          </TabsContent>
        </div>
      </Tabs>
    </div>
  );
}

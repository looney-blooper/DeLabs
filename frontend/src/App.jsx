import React, { useState, useRef, useEffect } from 'react';
import { Terminal, Cpu, Code2, Send, User, Bot, FileCode, Folder, File, ChevronDown } from 'lucide-react';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

const initialFileSystem = {
  'welcome.py': `# Swarm connected.\n# Awaiting workspace updates...\n`
};

function App() {
  const [input, setInput] = useState('');
  const [activeTab, setActiveTab] = useState('chat');
  const [activeFile, setActiveFile] = useState('welcome.py');
  
  const [messages, setMessages] = useState([
    { id: 1, role: 'system', agent: 'System', text: 'Swarm network initialized. Awaiting task assignment...' }
  ]);
  const messagesEndRef = useRef(null);

  const [files, setFiles] = useState(initialFileSystem);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleDispatch = (e) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;

    const userText = input;
    
    // 1. Show user message & clear input
    setMessages(prev => [...prev, { id: Date.now(), role: 'user', text: userText }]);
    setInput('');
    setIsProcessing(true);

    // 2. Open WebSocket connection to FastAPI
    const ws = new WebSocket('ws://localhost:8000/ws/swarm');

    ws.onopen = () => {
      ws.send(JSON.stringify({ prompt: userText }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'status') {
        setMessages(prev => [...prev, { id: Date.now(), role: 'system', agent: 'System', text: data.message }]);
      } 
      else if (data.type === 'update') {
        // Map the node name to the agent name
        setMessages(prev => [...prev, { id: Date.now(), role: 'agent', agent: data.node, text: data.message }]);
      } 
      else if (data.type === 'complete') {
        setMessages(prev => [...prev, { id: Date.now(), role: 'system', agent: 'System', text: data.message }]);
        
        // If the swarm generated files, update the explorer!
        if (data.files && Object.keys(data.files).length > 0) {
          setFiles(prev => ({ ...prev, ...data.files }));
          
          // Auto-switch to the first new file
          const firstFile = Object.keys(data.files)[0];
          setActiveFile(firstFile);
          setActiveTab('workspace');
        }
        
        // If there were errors, log them
        if (data.errors && data.errors.length > 0) {
           setMessages(prev => [...prev, { id: Date.now(), role: 'system', agent: 'System', text: `Errors encountered: ${data.errors.join(', ')}` }]);
        }
        
        setIsProcessing(false);
        ws.close(); // Close connection after task is complete
      } 
      else if (data.type === 'error') {
        setMessages(prev => [...prev, { id: Date.now(), role: 'system', agent: 'System', text: `Backend Error: ${data.message}` }]);
        setIsProcessing(false);
        ws.close();
      }
    };

    ws.onerror = () => {
      setMessages(prev => [...prev, { id: Date.now(), role: 'system', agent: 'System', text: 'WebSocket connection failed. Is FastAPI running on port 8000?' }]);
      setIsProcessing(false);
    };
  };

  return (
    <div className="flex h-screen bg-gray-900 text-gray-100 font-sans">
      
      {/* Sidebar - Swarm Status & File Explorer */}
      <aside className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
        <div className="p-4 border-b border-gray-700">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <Cpu className="w-6 h-6 text-blue-400" />
            DeLabs
          </h1>
        </div>
        
        <div className="p-4 border-b border-gray-700">
          <h2 className="text-xs uppercase text-gray-500 font-semibold mb-3">Swarm Status</h2>
          <div className="flex items-center gap-2 text-sm">
            <span className={`w-2 h-2 rounded-full ${isProcessing ? 'bg-yellow-500 animate-pulse shadow-[0_0_5px_#eab308]' : 'bg-green-500 shadow-[0_0_5px_#22c55e]'}`}></span>
            {isProcessing ? 'Processing Task...' : 'Idle'}
          </div>
        </div>

        {/* File Explorer */}
        <div className="p-4 flex-1 overflow-y-auto custom-scrollbar">
          <h2 className="text-xs uppercase text-gray-500 font-semibold mb-3 flex items-center gap-1">
            <ChevronDown className="w-4 h-4" /> Explorer
          </h2>
          <div className="space-y-1">
            <div className="flex items-center gap-2 text-sm text-gray-300 py-1">
              <Folder className="w-4 h-4 text-blue-400" />
              <span>core</span>
            </div>
            <div className="pl-4 space-y-1 mt-1">
              {Object.keys(files).map((filename) => (
                <div 
                  key={filename}
                  onClick={() => {
                    setActiveFile(filename);
                    setActiveTab('workspace');
                  }}
                  className={`flex items-center gap-2 text-sm py-1 px-2 rounded cursor-pointer transition-colors ${activeFile === filename ? 'bg-blue-900/40 text-blue-300' : 'text-gray-400 hover:bg-gray-700 hover:text-gray-200'}`}
                >
                  <File className="w-3.5 h-3.5" />
                  <span className="truncate">{filename}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Content - Interaction View */}
      <main className="flex-1 flex flex-col min-w-0">
        
        {/* Header with Tabs */}
        <header className="h-14 border-b border-gray-700 flex items-center px-4 bg-gray-800/50 justify-between shrink-0">
          <div className="flex gap-2">
            <button 
              onClick={() => setActiveTab('chat')}
              className={`px-4 py-2 text-sm font-medium rounded-md flex items-center gap-2 transition-colors ${activeTab === 'chat' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-200'}`}
            >
              <Terminal className="w-4 h-4" />
              Event Log
            </button>
            <button 
              onClick={() => setActiveTab('workspace')}
              className={`px-4 py-2 text-sm font-medium rounded-md flex items-center gap-2 transition-colors ${activeTab === 'workspace' ? 'bg-gray-700 text-white' : 'text-gray-400 hover:text-gray-200'}`}
            >
              <FileCode className="w-4 h-4" />
              Workspace
            </button>
          </div>
          <span className="text-gray-500 font-mono text-sm truncate ml-4">/delabs/core/{activeFile}</span>
        </header>

        {/* Dynamic Content Area based on Tab */}
        <div className="flex-1 overflow-y-auto bg-gray-900 custom-scrollbar">
          
          {/* Chat View */}
          {activeTab === 'chat' && (
            <div className="p-6">
              {messages.map((msg) => (
                <div key={msg.id} className={`rounded-lg p-4 mb-4 border shadow-sm ${msg.role === 'user' ? 'bg-blue-900/20 border-blue-800/30 ml-auto max-w-2xl' : 'bg-gray-800 border-gray-700 mr-auto max-w-3xl'}`}>
                  <div className="flex items-center gap-2 mb-2">
                    {msg.role === 'system' && <Terminal className="w-4 h-4 text-blue-400" />}
                    {msg.role === 'agent' && <Bot className="w-4 h-4 text-green-400" />}
                    {msg.role === 'user' && <User className="w-4 h-4 text-gray-400" />}
                    <span className={`text-sm font-mono ${msg.role === 'system' ? 'text-blue-400' : msg.role === 'agent' ? 'text-green-400' : 'text-gray-400'}`}>
                      {msg.role === 'user' ? 'You' : msg.agent}
                    </span>
                  </div>
                  <p className="text-gray-300 leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}

          {/* Workspace View */}
          {activeTab === 'workspace' && (
            <div className="p-6 h-full min-h-[500px]">
              <div className="bg-[#1e1e1e] rounded-lg border border-gray-700 h-full flex flex-col shadow-xl">
                <div className="bg-gray-800 px-4 py-2 border-b border-gray-700 flex items-center justify-between shrink-0">
                  <span className="text-sm font-mono text-gray-300">{activeFile}</span>
                </div>
                <div className="flex-1 overflow-auto custom-scrollbar">
                  <SyntaxHighlighter 
                    language="python" 
                    style={vscDarkPlus}
                    customStyle={{ margin: 0, padding: '1rem', background: 'transparent', minHeight: '100%' }}
                    showLineNumbers={true}
                  >
                    {files[activeFile] || '# File empty or missing content'}
                  </SyntaxHighlighter>
                </div>
              </div>
            </div>
          )}

        </div>

        {/* Command Input Area */}
        <div className="p-4 border-t border-gray-700 bg-gray-800 shrink-0">
          <form onSubmit={handleDispatch} className="max-w-4xl mx-auto flex gap-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder={isProcessing ? "Swarm is thinking..." : "Instruct the swarm..."}
              disabled={isProcessing}
              className="flex-1 bg-gray-900 border border-gray-600 rounded-md px-4 py-3 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all text-gray-100 placeholder-gray-500 disabled:opacity-50"
            />
            <button 
              type="submit" 
              disabled={!input.trim() || isProcessing} 
              className="bg-blue-600 hover:bg-blue-500 disabled:opacity-50 disabled:cursor-not-allowed px-6 py-2 rounded-md flex items-center gap-2 transition-colors font-medium shadow-lg"
            >
              <Send className="w-4 h-4" />
              Dispatch
            </button>
          </form>
        </div>
      </main>
    </div>
  );
}

export default App;
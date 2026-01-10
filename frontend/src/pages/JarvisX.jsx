import { useState, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  Mic,
  MicOff,
  Volume2,
  VolumeX,
  Send,
  User,
  Bot,
  Wallet,
  GraduationCap,
  Heart,
  Code,
  Globe,
  Shield,
  RefreshCw,
  ChevronRight,
  TrendingUp,
  AlertTriangle,
  Check,
  X,
  ArrowLeft,
  IndianRupee,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { ScrollArea } from "../components/ui/scroll-area";
import { Progress } from "../components/ui/progress";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Web Speech API setup
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const speechSynthesis = window.speechSynthesis;

export default function JarvisXPage() {
  const navigate = useNavigate();
  
  // Voice state
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [transcript, setTranscript] = useState("");
  
  // Chat state
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(() => `session_${Date.now()}`);
  
  // JARVIS-X state
  const [jarvisStatus, setJarvisStatus] = useState(null);
  const [speakerVerified, setSpeakerVerified] = useState(false);
  const [currentSpeaker, setCurrentSpeaker] = useState(null);
  const [activeModule, setActiveModule] = useState("chat");
  
  // Domain data
  const [fintechData, setFintechData] = useState(null);
  const [medtechData, setMedtechData] = useState(null);
  
  // Refs
  const recognitionRef = useRef(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Initialize speech recognition
  useEffect(() => {
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = true;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event) => {
        const current = event.resultIndex;
        const result = event.results[current];
        const transcriptText = result[0].transcript;
        setTranscript(transcriptText);
        
        if (result.isFinal) {
          setInputMessage(transcriptText);
          setIsListening(false);
        }
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        if (event.error !== 'no-speech') {
          toast.error(`Voice error: ${event.error}`);
        }
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort();
      }
    };
  }, []);

  // Text-to-speech function
  const speak = useCallback((text) => {
    if (!voiceEnabled || !speechSynthesis) return;
    
    // Cancel any ongoing speech
    speechSynthesis.cancel();
    
    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1.0;
    utterance.pitch = 1.0;
    utterance.volume = 1.0;
    
    // Try to use a natural voice
    const voices = speechSynthesis.getVoices();
    const preferredVoice = voices.find(v => 
      v.name.includes('Google') || v.name.includes('Natural') || v.name.includes('Premium')
    ) || voices[0];
    
    if (preferredVoice) {
      utterance.voice = preferredVoice;
    }
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);
    
    speechSynthesis.speak(utterance);
  }, [voiceEnabled]);

  // Fetch JARVIS-X status on mount
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await axios.get(`${API}/jarvis-x/status`);
        setJarvisStatus(res.data);
        
        // Speak greeting
        if (voiceEnabled) {
          speak("Welcome. JARVIS-X system is online.");
        }
        
        // Add welcome message
        setMessages([{
          role: "assistant",
          content: "Welcome. JARVIS-X system is online. I am your voice-enabled, multi-domain AI assistant. How may I assist you today?",
          timestamp: new Date().toISOString(),
          intent: { intent: "greeting" }
        }]);
      } catch (error) {
        console.error("Failed to fetch JARVIS-X status:", error);
      }
    };
    
    fetchStatus();
  }, [speak, voiceEnabled]);

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Verify speaker
  const verifySpeaker = async (speakerId = "admin") => {
    try {
      const res = await axios.post(`${API}/jarvis-x/speaker/verify`, { speaker_id: speakerId });
      setSpeakerVerified(res.data.verified);
      setCurrentSpeaker(res.data.speaker);
      
      if (res.data.verified) {
        toast.success(res.data.message);
        speak(res.data.message);
      } else {
        toast.error(res.data.message);
        speak(res.data.message);
      }
      
      return res.data;
    } catch (error) {
      toast.error("Speaker verification failed");
      return { verified: false };
    }
  };

  // Toggle voice listening
  const toggleListening = () => {
    if (!SpeechRecognition) {
      toast.error("Speech recognition not supported in this browser");
      return;
    }

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      setTranscript("");
      recognitionRef.current.start();
      setIsListening(true);
    }
  };

  // Check for navigation commands
  const checkNavigationCommand = (message) => {
    const lowerMsg = message.toLowerCase();
    const navPatterns = [
      "go back", "back to dashboard", "return to dashboard", 
      "open dashboard", "show dashboard", "navigate to dashboard",
      "go to dashboard", "exit", "go home"
    ];
    return navPatterns.some(pattern => lowerMsg.includes(pattern));
  };

  // Handle navigation with voice feedback
  const handleNavigateToDashboard = () => {
    const response = "Returning to dashboard. Have a great day!";
    if (voiceEnabled) {
      speak(response);
    }
    toast.info("Returning to Dashboard...");
    setTimeout(() => navigate("/"), 1500);
  };

  // Send message to JARVIS-X
  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;
    
    // Check for navigation command first
    if (checkNavigationCommand(message)) {
      const userMessage = {
        role: "user",
        content: message,
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, userMessage]);
      setInputMessage("");
      setTranscript("");
      
      const assistantMessage = {
        role: "assistant",
        content: "Returning to dashboard. Have a great day!",
        timestamp: new Date().toISOString(),
        intent: { intent: "navigation" }
      };
      setMessages(prev => [...prev, assistantMessage]);
      handleNavigateToDashboard();
      return;
    }
    
    // Add user message
    const userMessage = {
      role: "user",
      content: message,
      timestamp: new Date().toISOString()
    };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage("");
    setTranscript("");
    setIsLoading(true);
    
    try {
      const res = await axios.post(`${API}/jarvis-x/chat`, {
        message: message,
        session_id: sessionId,
        speaker_id: currentSpeaker ? "admin" : "guest"
      });
      
      // Add assistant response
      const assistantMessage = {
        role: "assistant",
        content: res.data.response,
        timestamp: res.data.timestamp,
        intent: res.data.intent
      };
      setMessages(prev => [...prev, assistantMessage]);
      
      // Update speaker verification status
      setSpeakerVerified(res.data.speaker_verified);
      if (res.data.speaker) {
        setCurrentSpeaker(res.data.speaker.name);
      }
      
      // Speak the response
      if (voiceEnabled) {
        speak(res.data.response);
      }
      
    } catch (error) {
      console.error("Chat error:", error);
      const errorMessage = {
        role: "assistant",
        content: "I apologize, I encountered an error processing your request. Please try again.",
        timestamp: new Date().toISOString(),
        error: true
      };
      setMessages(prev => [...prev, errorMessage]);
      toast.error("Failed to get response");
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Fetch domain data
  const fetchFintechData = async () => {
    try {
      const [summary, budget, insights] = await Promise.all([
        axios.get(`${API}/jarvis-x/fintech/summary`),
        axios.get(`${API}/jarvis-x/fintech/budget`),
        axios.get(`${API}/jarvis-x/fintech/insights`)
      ]);
      setFintechData({
        summary: summary.data,
        budget: budget.data,
        insights: insights.data.insights
      });
    } catch (error) {
      console.error("Failed to fetch FinTech data:", error);
    }
  };

  const fetchMedtechData = async () => {
    try {
      const [vitals, reminders] = await Promise.all([
        axios.get(`${API}/jarvis-x/medtech/vitals`),
        axios.get(`${API}/jarvis-x/medtech/reminders`)
      ]);
      setMedtechData({
        vitals: vitals.data,
        reminders: reminders.data.reminders
      });
    } catch (error) {
      console.error("Failed to fetch MedTech data:", error);
    }
  };

  // Fetch data when switching modules
  useEffect(() => {
    if (activeModule === "fintech") {
      fetchFintechData();
    } else if (activeModule === "medtech") {
      fetchMedtechData();
    }
  }, [activeModule]);

  // Quick action buttons
  const quickActions = [
    { label: "System Status", query: "What is the system status?", icon: Shield },
    { label: "My Finances", query: "Show me my expense summary in rupees", icon: Wallet },
    { label: "Health Check", query: "What are my current vitals?", icon: Heart },
    { label: "Build Software", query: "I want to build a dashboard", icon: Code },
    { label: "Learn Python", query: "Show me the Python learning path", icon: GraduationCap },
    { label: "Go to Dashboard", query: "Go back to dashboard", icon: ArrowLeft },
  ];

  // Render intent badge
  const getIntentBadge = (intent) => {
    const colors = {
      system_intelligence: "bg-cyan-500/20 text-cyan-400 border-cyan-500/30",
      fintech: "bg-green-500/20 text-green-400 border-green-500/30",
      edutech: "bg-purple-500/20 text-purple-400 border-purple-500/30",
      medtech: "bg-red-500/20 text-red-400 border-red-500/30",
      software_generation: "bg-blue-500/20 text-blue-400 border-blue-500/30",
      general_knowledge: "bg-amber-500/20 text-amber-400 border-amber-500/30",
      navigation: "bg-gray-500/20 text-gray-400 border-gray-500/30",
    };
    
    return colors[intent] || "bg-muted text-muted-foreground";
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-6" data-testid="jarvis-x-page">
      {/* Header */}
      <header className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            {/* Back to Dashboard Button */}
            <Button
              variant="outline"
              size="icon"
              onClick={handleNavigateToDashboard}
              className="h-10 w-10 rounded-full border-primary/30 hover:bg-primary/10"
              data-testid="back-to-dashboard-btn"
            >
              <ArrowLeft className="w-5 h-5" />
            </Button>
            
            <div className="relative">
              <div className={`w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center ${isSpeaking ? 'animate-pulse' : ''}`}>
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div className={`absolute -bottom-1 -right-1 w-4 h-4 rounded-full ${jarvisStatus?.status === 'online' ? 'bg-emerald-500' : 'bg-red-500'} border-2 border-background`} />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold tracking-tight text-foreground" data-testid="jarvis-x-title">
                JARVIS-X
              </h1>
              <p className="text-xs md:text-sm text-muted-foreground tracking-wide">
                Voice-Enabled Multi-Domain AI Assistant • GPT-5.2 + Hugging Face
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Speaker Status */}
            <Badge 
              variant="outline" 
              className={`${speakerVerified ? 'bg-emerald-500/20 text-emerald-400 border-emerald-500/30' : 'bg-amber-500/20 text-amber-400 border-amber-500/30'} px-3 py-1 text-xs`}
              data-testid="speaker-badge"
            >
              <User className="w-3 h-3 mr-2" />
              {speakerVerified ? currentSpeaker || 'Verified' : 'Guest'}
            </Badge>

            {/* Voice Toggle */}
            <Button
              variant="outline"
              size="sm"
              onClick={() => setVoiceEnabled(!voiceEnabled)}
              className="text-xs"
              data-testid="voice-toggle-btn"
            >
              {voiceEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
            </Button>

            {/* Verify Speaker */}
            <Button
              variant={speakerVerified ? "outline" : "default"}
              size="sm"
              onClick={() => verifySpeaker("admin")}
              className="text-xs"
              data-testid="verify-speaker-btn"
            >
              <Shield className="w-4 h-4 mr-2" />
              {speakerVerified ? 'Verified' : 'Verify Voice'}
            </Button>
          </div>
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
        {/* Sidebar - Quick Actions & Modules */}
        <div className="lg:col-span-3 space-y-4">
          {/* Module Selector */}
          <Card className="bg-card/50 border-border/50" data-testid="module-selector">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground">
                ACTIVE MODULES
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {[
                { id: "chat", label: "Chat", icon: Bot },
                { id: "fintech", label: "FinTech", icon: Wallet },
                { id: "medtech", label: "MedTech", icon: Heart },
                { id: "edutech", label: "EduTech", icon: GraduationCap },
                { id: "software", label: "Software", icon: Code },
              ].map((module) => (
                <Button
                  key={module.id}
                  variant={activeModule === module.id ? "default" : "ghost"}
                  size="sm"
                  className="w-full justify-start text-xs"
                  onClick={() => setActiveModule(module.id)}
                  data-testid={`module-${module.id}`}
                >
                  <module.icon className="w-4 h-4 mr-2" />
                  {module.label}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card className="bg-card/50 border-border/50" data-testid="quick-actions">
            <CardHeader className="pb-2">
              <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground">
                QUICK ACTIONS
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {quickActions.map((action, idx) => (
                <Button
                  key={idx}
                  variant="ghost"
                  size="sm"
                  className="w-full justify-start text-xs"
                  onClick={() => sendMessage(action.query)}
                  data-testid={`quick-action-${idx}`}
                >
                  <action.icon className="w-4 h-4 mr-2" />
                  {action.label}
                </Button>
              ))}
            </CardContent>
          </Card>

          {/* System Status */}
          {jarvisStatus && (
            <Card className="bg-card/50 border-border/50" data-testid="system-status">
              <CardHeader className="pb-2">
                <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground">
                  SYSTEM STATUS
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-2 text-xs">
                {Object.entries(jarvisStatus.modules || {}).map(([module, status]) => (
                  <div key={module} className="flex justify-between items-center">
                    <span className="text-muted-foreground capitalize">{module.replace('_', ' ')}</span>
                    <Badge variant="outline" className="text-xs bg-emerald-500/10 text-emerald-400">
                      {typeof status === 'string' && status.includes('active') ? 'ON' : status}
                    </Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-9 space-y-4">
          {/* Domain-specific panels */}
          {activeModule === "fintech" && fintechData && (
            <Card className="bg-card/50 border-border/50" data-testid="fintech-panel">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Wallet className="w-4 h-4 text-green-400" />
                  Financial Overview (Simulated - INR ₹)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <IndianRupee className="w-3 h-3" /> Income
                    </div>
                    <div className="text-xl font-bold text-primary">₹{fintechData.summary.income?.toLocaleString('en-IN')}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <IndianRupee className="w-3 h-3" /> Spent
                    </div>
                    <div className="text-xl font-bold text-amber-400">₹{fintechData.summary.total_spent?.toLocaleString('en-IN')}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground flex items-center gap-1">
                      <IndianRupee className="w-3 h-3" /> Remaining
                    </div>
                    <div className="text-xl font-bold text-emerald-400">₹{fintechData.summary.remaining?.toLocaleString('en-IN')}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground">Savings Rate</div>
                    <div className="text-xl font-bold text-cyan-400">{fintechData.summary.savings_rate}%</div>
                  </div>
                </div>
                <div className="space-y-2">
                  {fintechData.insights.map((insight, idx) => (
                    <div key={idx} className="flex items-start gap-2 text-xs text-muted-foreground">
                      <ChevronRight className="w-3 h-3 mt-0.5 text-primary" />
                      {insight.replace(/\$/g, '₹')}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}

          {activeModule === "medtech" && medtechData && (
            <Card className="bg-card/50 border-border/50" data-testid="medtech-panel">
              <CardHeader className="pb-2">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Heart className="w-4 h-4 text-red-400" />
                  Health Monitoring (Simulated - Assistive Only)
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground">Heart Rate</div>
                    <div className="text-xl font-bold text-red-400">{medtechData.vitals.vitals.heart_rate} BPM</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground">Blood Pressure</div>
                    <div className="text-xl font-bold text-amber-400">{medtechData.vitals.vitals.blood_pressure}</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground">Temperature</div>
                    <div className="text-xl font-bold text-cyan-400">{medtechData.vitals.vitals.temperature}°F</div>
                  </div>
                  <div className="p-3 rounded-lg bg-muted/30 border border-border/50">
                    <div className="text-xs text-muted-foreground">O2 Saturation</div>
                    <div className="text-xl font-bold text-emerald-400">{medtechData.vitals.vitals.oxygen_saturation}%</div>
                  </div>
                </div>
                <Badge 
                  variant="outline" 
                  className={medtechData.vitals.status === "NORMAL" ? "bg-emerald-500/20 text-emerald-400" : "bg-amber-500/20 text-amber-400"}
                >
                  Status: {medtechData.vitals.status}
                </Badge>
                <p className="text-xs text-muted-foreground mt-2">{medtechData.vitals.disclaimer}</p>
              </CardContent>
            </Card>
          )}

          {/* Chat Interface */}
          <Card className="bg-card/50 border-border/50 h-[500px] flex flex-col" data-testid="chat-interface">
            <CardHeader className="pb-2 border-b border-border/30">
              <div className="flex items-center justify-between">
                <CardTitle className="text-sm font-medium flex items-center gap-2">
                  <Bot className={`w-4 h-4 ${isSpeaking ? 'text-cyan-400 animate-pulse' : 'text-primary'}`} />
                  JARVIS-X Conversation
                </CardTitle>
                {isListening && (
                  <Badge variant="outline" className="bg-red-500/20 text-red-400 animate-pulse">
                    <Mic className="w-3 h-3 mr-1" /> Listening...
                  </Badge>
                )}
              </div>
            </CardHeader>
            
            <CardContent className="flex-1 flex flex-col p-0 overflow-hidden">
              {/* Messages */}
              <ScrollArea className="flex-1 p-4">
                <div className="space-y-4">
                  {messages.map((msg, idx) => (
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                      data-testid={`message-${idx}`}
                    >
                      <div className={`max-w-[80%] ${msg.role === 'user' ? 'order-2' : ''}`}>
                        <div className={`rounded-lg p-3 ${
                          msg.role === 'user' 
                            ? 'bg-primary/20 border border-primary/30' 
                            : msg.error 
                              ? 'bg-red-500/10 border border-red-500/30'
                              : 'bg-muted/50 border border-border'
                        }`}>
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          {msg.intent && msg.role === 'assistant' && (
                            <Badge 
                              variant="outline" 
                              className={`text-xs mt-2 ${getIntentBadge(msg.intent.intent)}`}
                            >
                              {msg.intent.intent?.replace('_', ' ')}
                            </Badge>
                          )}
                        </div>
                        <p className="text-xs text-muted-foreground mt-1 px-1">
                          {new Date(msg.timestamp).toLocaleTimeString()}
                        </p>
                      </div>
                    </div>
                  ))}
                  {isLoading && (
                    <div className="flex justify-start">
                      <div className="bg-muted/50 border border-border rounded-lg p-3">
                        <RefreshCw className="w-4 h-4 animate-spin text-primary" />
                      </div>
                    </div>
                  )}
                  <div ref={messagesEndRef} />
                </div>
              </ScrollArea>

              {/* Transcript Preview */}
              {isListening && transcript && (
                <div className="px-4 py-2 bg-muted/30 border-t border-border/30 text-sm text-muted-foreground">
                  <Mic className="w-3 h-3 inline mr-2" />
                  {transcript}
                </div>
              )}

              {/* Input Area */}
              <div className="p-4 border-t border-border/30">
                <div className="flex gap-2">
                  <Button
                    variant={isListening ? "destructive" : "outline"}
                    size="icon"
                    onClick={toggleListening}
                    disabled={!SpeechRecognition}
                    data-testid="mic-btn"
                  >
                    {isListening ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
                  </Button>
                  <input
                    ref={inputRef}
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask JARVIS-X anything..."
                    className="flex-1 px-4 py-2 bg-muted/30 border border-border rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled={isLoading}
                    data-testid="chat-input"
                  />
                  <Button
                    onClick={() => sendMessage()}
                    disabled={isLoading || !inputMessage.trim()}
                    data-testid="send-btn"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                </div>
                <p className="text-xs text-muted-foreground mt-2">
                  Click the mic to speak, or type your message. Try: "What is the system status?" or "Show me my expenses"
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-6 pt-4 border-t border-border/30">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 text-xs text-muted-foreground">
          <p>
            JARVIS-X // Voice-Enabled AI Assistant // GPT-5.2 Powered
          </p>
          <p>
            Speaker: {speakerVerified ? currentSpeaker || 'Verified' : 'Guest'} | 
            Voice: {voiceEnabled ? 'ON' : 'OFF'} |
            Session: {sessionId.slice(0, 12)}...
          </p>
        </div>
      </footer>
    </div>
  );
}

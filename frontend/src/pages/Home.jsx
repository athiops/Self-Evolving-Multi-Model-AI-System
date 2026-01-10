import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Brain,
  Network,
  Activity,
  MessageSquare,
  Shield,
  Zap,
  Globe,
  Mic,
  Database,
  TrendingUp,
  Waves,
  GitBranch,
  Radio,
  Server,
  BarChart3,
  Heart,
  GraduationCap,
  Wallet,
  Code,
  Car,
  Building2,
  ShoppingCart,
  Factory,
  Lock,
  Users,
  ArrowRight,
  CheckCircle2,
  Sparkles,
  Eye,
} from "lucide-react";

export default function Home() {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const aiModels = [
    {
      number: "MODEL-1",
      name: "Core Self-Evolving AI",
      icon: Activity,
      description: "Online anomaly detection with continuous learning",
      features: ["Real-time streaming", "No retraining required", "Self-monitoring"],
      color: "cyan",
    },
    {
      number: "MODEL-2",
      name: "Federated Learning & Drift",
      icon: Network,
      description: "Privacy-preserving distributed learning with drift detection",
      features: ["5 Edge nodes", "ADWIN + Page-Hinkley", "Cross-org collaboration"],
      color: "purple",
    },
    {
      number: "MODEL-3",
      name: "Digital Twin Simulator",
      icon: Waves,
      description: "Future prediction and what-if scenario simulation",
      features: ["Health forecasting", "Risk scoring", "Scenario testing"],
      color: "blue",
    },
    {
      number: "MODEL-4",
      name: "Explainable AI (XAI)",
      icon: Eye,
      description: "Natural language explanations for all AI decisions",
      features: ["Decision transparency", "Trust building", "Regulatory compliance"],
      color: "green",
    },
    {
      number: "MODEL-5",
      name: "JARVIS Cognitive Interface",
      icon: Brain,
      description: "Natural language query processing and intent detection",
      features: ["NLP understanding", "Context awareness", "Multi-turn dialogue"],
      color: "cyan",
    },
    {
      number: "MODEL-6",
      name: "Personalization Engine",
      icon: Users,
      description: "User preferences and adaptive behavior",
      features: ["Custom experiments", "Report generation", "User profiles"],
      color: "yellow",
    },
  ];

  const realWorldUses = [
    {
      icon: Heart,
      title: "Healthcare",
      description: "Patient monitoring, early warning systems, remote care",
      stat: "6-hour early detection",
    },
    {
      icon: Wallet,
      title: "FinTech",
      description: "Fraud detection, transaction monitoring, personal finance",
      stat: "98.7% accuracy",
    },
    {
      icon: Factory,
      title: "Manufacturing",
      description: "Predictive maintenance, quality control, IoT monitoring",
      stat: "40% less downtime",
    },
    {
      icon: GraduationCap,
      title: "Education",
      description: "Adaptive learning, student risk prediction, skill tracking",
      stat: "Personalized paths",
    },
    {
      icon: Lock,
      title: "Cybersecurity",
      description: "Intrusion detection, threat intelligence, network monitoring",
      stat: "99.5% accuracy",
    },
    {
      icon: Car,
      title: "Autonomous Vehicles",
      description: "Safety systems, adaptive driving, condition monitoring",
      stat: "Real-time adaptation",
    },
    {
      icon: Building2,
      title: "Smart Cities",
      description: "Energy grid, traffic management, infrastructure monitoring",
      stat: "25% energy savings",
    },
    {
      icon: ShoppingCart,
      title: "E-Commerce",
      description: "Dynamic pricing, inventory optimization, demand prediction",
      stat: "15% revenue increase",
    },
  ];

  const jarvisFeatures = [
    {
      icon: Mic,
      title: "Voice Interaction",
      description: "Speak naturally - JARVIS understands and responds",
      tech: "Web Speech API + GPT-5.2",
    },
    {
      icon: Wallet,
      title: "FinTech Intelligence",
      description: "Expense tracking, budget monitoring, financial insights",
      tech: "Real-time analytics",
    },
    {
      icon: GraduationCap,
      title: "EduTech Assistant",
      description: "Learning paths, progress tracking, concept explanations",
      tech: "Adaptive curriculum",
    },
    {
      icon: Heart,
      title: "MedTech Monitoring",
      description: "Vitals tracking, health reminders, assistive alerts",
      tech: "No diagnosis mode",
    },
    {
      icon: Code,
      title: "Software Generation",
      description: "Requirements analysis, project scaffolding, MVP creation",
      tech: "AI-powered dev",
    },
    {
      icon: Globe,
      title: "Internet-Aware RAG",
      description: "Knowledge retrieval from trusted sources",
      tech: "Controlled access",
    },
  ];

  const keyAdvantages = [
    {
      title: "Self-Evolving",
      description: "Learns continuously without manual retraining",
      icon: Zap,
    },
    {
      title: "Privacy-First",
      description: "Federated learning protects sensitive data",
      icon: Shield,
    },
    {
      title: "Explainable",
      description: "Understand exactly why decisions are made",
      icon: MessageSquare,
    },
    {
      title: "Multi-Domain",
      description: "One system, endless applications",
      icon: GitBranch,
    },
  ];

  const getColorClasses = (color) => {
    const colors = {
      cyan: "border-cyan-500/30 bg-cyan-500/5 hover:border-cyan-500/50",
      purple: "border-purple-500/30 bg-purple-500/5 hover:border-purple-500/50",
      blue: "border-blue-500/30 bg-blue-500/5 hover:border-blue-500/50",
      green: "border-emerald-500/30 bg-emerald-500/5 hover:border-emerald-500/50",
      yellow: "border-yellow-500/30 bg-yellow-500/5 hover:border-yellow-500/50",
    };
    return colors[color] || colors.cyan;
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      {/* Animated background */}
      <div className="fixed inset-0 opacity-30">
        <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 via-purple-500/10 to-pink-500/10" />
        <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0zNiAxOGMzLjMxNCAwIDYgMi42ODYgNiA2cy0yLjY4NiA2LTYgNi02LTIuNjg2LTYtNiAyLjY4Ni02IDYtNnoiIHN0cm9rZT0iIzAwZmZmZiIgc3Ryb2tlLXdpZHRoPSIuNSIgb3BhY2l0eT0iLjEiLz48L2c+PC9zdmc+')] opacity-20" />
      </div>

      {/* Content */}
      <div className="relative z-10">
        {/* Hero Section */}
        <div className="container mx-auto px-4 py-12">
          <div
            className={`text-center mb-16 transition-all duration-1000 ${
              isVisible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-10"
            }`}
          >
            <div className="inline-flex items-center gap-2 mb-6 px-4 py-2 bg-cyan-500/10 border border-cyan-500/30 rounded-full">
              <Sparkles className="w-4 h-4 text-cyan-400" />
              <span className="text-sm font-mono text-cyan-400 tracking-wide">
                INSPIRED BY TONY STARK'S JARVIS
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 font-mono tracking-tighter">
              <span className="bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                JARVIS-X
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-400 mb-4 font-mono">
              Self-Evolving Multi-Model AI System
            </p>

            <p className="text-lg text-gray-500 max-w-3xl mx-auto mb-8 leading-relaxed">
              A production-ready AI platform combining continuous learning, federated
              intelligence, digital twin simulation, and voice-enabled interaction.
              Built for real-world applications across healthcare, finance, manufacturing,
              and more.
            </p>

            <div className="flex flex-wrap justify-center gap-4 mb-8">
              <Button
                onClick={() => navigate("/dashboard")}
                size="lg"
                className="bg-cyan-500 hover:bg-cyan-600 text-black font-mono font-bold tracking-widest shadow-[0_0_20px_rgba(0,255,255,0.3)] transition-all hover:shadow-[0_0_30px_rgba(0,255,255,0.5)]"
                data-testid="launch-dashboard-btn"
              >
                <Activity className="w-5 h-5 mr-2" />
                LAUNCH DASHBOARD
              </Button>

              <Button
                onClick={() => navigate("/jarvis-x")}
                size="lg"
                variant="outline"
                className="border-purple-500/50 text-purple-400 hover:bg-purple-500/10 font-mono font-bold tracking-widest"
                data-testid="talk-to-jarvis-btn"
              >
                <Mic className="w-5 h-5 mr-2" />
                TALK TO JARVIS-X
              </Button>
            </div>

            {/* Key stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
              {[
                { label: "AI Models", value: "6", icon: Brain },
                { label: "Accuracy", value: "98.5%", icon: TrendingUp },
                { label: "Domains", value: "8+", icon: Globe },
                { label: "Real-time", value: "<500ms", icon: Zap },
              ].map((stat, idx) => (
                <Card key={idx} className="bg-black/40 border-white/10 backdrop-blur-sm">
                  <CardContent className="p-4 text-center">
                    <stat.icon className="w-6 h-6 mx-auto mb-2 text-cyan-400" />
                    <div className="text-2xl font-bold text-white font-mono">{stat.value}</div>
                    <div className="text-xs text-gray-500 uppercase tracking-wider">
                      {stat.label}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* 6 Core AI Models */}
          <div className="mb-20">
            <div className="text-center mb-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-3 font-mono text-cyan-400">
                6 CORE AI MODELS
              </h2>
              <p className="text-gray-500">
                Each model serves a specific purpose in the intelligent ecosystem
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {aiModels.map((model, idx) => (
                <Card
                  key={idx}
                  className={`bg-black/40 backdrop-blur-xl border transition-all duration-300 hover:scale-105 cursor-pointer group ${getColorClasses(
                    model.color
                  )}`}
                  data-testid={`model-${idx + 1}-card`}
                >
                  <CardHeader>
                    <div className="flex items-start justify-between mb-3">
                      <model.icon className="w-10 h-10 text-cyan-400 group-hover:scale-110 transition-transform" />
                      <Badge
                        variant="outline"
                        className="font-mono text-xs border-white/20"
                      >
                        {model.number}
                      </Badge>
                    </div>
                    <CardTitle className="text-lg font-mono text-white">
                      {model.name}
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400 text-sm mb-4">{model.description}</p>
                    <div className="space-y-2">
                      {model.features.map((feature, fIdx) => (
                        <div key={fIdx} className="flex items-center gap-2 text-xs">
                          <CheckCircle2 className="w-3 h-3 text-emerald-500" />
                          <span className="text-gray-500">{feature}</span>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* JARVIS-X Features */}
          <div className="mb-20">
            <div className="text-center mb-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-3 font-mono text-purple-400">
                JARVIS-X VOICE ASSISTANT
              </h2>
              <p className="text-gray-500">
                Multi-domain conversational AI with voice interaction
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {jarvisFeatures.map((feature, idx) => (
                <Card
                  key={idx}
                  className="bg-black/40 backdrop-blur-xl border border-purple-500/20 hover:border-purple-500/40 transition-all group"
                  data-testid={`jarvis-feature-${idx}-card`}
                >
                  <CardHeader>
                    <feature.icon className="w-8 h-8 text-purple-400 mb-3 group-hover:scale-110 transition-transform" />
                    <CardTitle className="text-lg text-white">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-400 text-sm mb-2">{feature.description}</p>
                    <Badge
                      variant="outline"
                      className="text-xs border-purple-500/30 text-purple-400"
                    >
                      {feature.tech}
                    </Badge>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Real-World Applications */}
          <div className="mb-20">
            <div className="text-center mb-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-3 font-mono text-white">
                REAL-WORLD APPLICATIONS
              </h2>
              <p className="text-gray-500">
                Production-ready solutions across multiple industries
              </p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {realWorldUses.map((use, idx) => (
                <Card
                  key={idx}
                  className="bg-gradient-to-br from-black/60 to-black/40 backdrop-blur-xl border border-white/10 hover:border-cyan-500/30 transition-all hover:scale-105 group"
                  data-testid={`industry-${idx}-card`}
                >
                  <CardHeader className="text-center">
                    <use.icon className="w-12 h-12 mx-auto text-cyan-400 mb-3 group-hover:scale-110 transition-transform" />
                    <CardTitle className="text-lg text-white">{use.title}</CardTitle>
                  </CardHeader>
                  <CardContent className="text-center">
                    <p className="text-gray-400 text-sm mb-3">{use.description}</p>
                    <div className="inline-flex items-center gap-1 px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 rounded-full">
                      <TrendingUp className="w-3 h-3 text-emerald-400" />
                      <span className="text-xs font-mono text-emerald-400">{use.stat}</span>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Key Advantages */}
          <div className="mb-20">
            <div className="text-center mb-10">
              <h2 className="text-3xl md:text-4xl font-bold mb-3 font-mono text-white">
                WHY JARVIS-X?
              </h2>
              <p className="text-gray-500">Revolutionary capabilities that set it apart</p>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              {keyAdvantages.map((advantage, idx) => (
                <Card
                  key={idx}
                  className="bg-black/40 backdrop-blur-xl border border-cyan-500/20 hover:border-cyan-500/40 transition-all text-center group"
                >
                  <CardContent className="pt-6">
                    <advantage.icon className="w-10 h-10 mx-auto mb-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                    <h3 className="text-lg font-bold text-white mb-2">{advantage.title}</h3>
                    <p className="text-sm text-gray-400">{advantage.description}</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* CTA Section */}
          <Card className="bg-gradient-to-r from-cyan-500/10 via-purple-500/10 to-pink-500/10 border border-cyan-500/30 backdrop-blur-xl">
            <CardContent className="p-8 md:p-12 text-center">
              <h2 className="text-3xl md:text-4xl font-bold mb-4 font-mono text-white">
                Ready to Experience the Future?
              </h2>
              <p className="text-lg text-gray-400 mb-8 max-w-2xl mx-auto">
                Launch the dashboard to see 6 AI models in action, or talk to JARVIS-X
                using voice commands. No setup required - just click and explore.
              </p>

              <div className="flex flex-wrap justify-center gap-4">
                <Button
                  onClick={() => navigate("/dashboard")}
                  size="lg"
                  className="bg-cyan-500 hover:bg-cyan-600 text-black font-mono font-bold tracking-widest shadow-[0_0_20px_rgba(0,255,255,0.3)]"
                  data-testid="cta-dashboard-btn"
                >
                  <Activity className="w-5 h-5 mr-2" />
                  EXPLORE DASHBOARD
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>

                <Button
                  onClick={() => navigate("/jarvis-x")}
                  size="lg"
                  className="bg-purple-500 hover:bg-purple-600 text-white font-mono font-bold tracking-widest shadow-[0_0_20px_rgba(168,85,247,0.3)]"
                  data-testid="cta-jarvis-btn"
                >
                  <Mic className="w-5 h-5 mr-2" />
                  TALK TO JARVIS-X
                  <ArrowRight className="w-5 h-5 ml-2" />
                </Button>
              </div>

              <div className="mt-8 pt-8 border-t border-white/10">
                <p className="text-sm text-gray-500 font-mono">
                  Powered by OpenAI GPT-5.2 • River ML • MongoDB • React • FastAPI
                </p>
              </div>
            </CardContent>
          </Card>

          {/* Footer */}
          <div className="text-center mt-12 pb-8">
            <p className="text-gray-600 text-sm">
              Built with ❤️ as a demonstration of self-evolving AI systems
            </p>
            <p className="text-gray-700 text-xs mt-2 font-mono">
              For educational and research purposes • Not for medical diagnosis or
              financial advice
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

import { useState, useEffect, useCallback, useRef } from "react";
import { Link } from "react-router-dom";
import axios from "axios";
import { toast } from "sonner";
import {
  Activity,
  Cpu,
  Zap,
  AlertTriangle,
  Database,
  Download,
  Upload,
  Settings,
  Play,
  Pause,
  RefreshCw,
  Trash2,
  FileJson,
  FileSpreadsheet,
  TrendingUp,
  BarChart3,
  Shield,
  Brain,
  Network,
  Server,
  Radio,
  GitBranch,
  Waves,
  CircleDot,
  Mic,
  Home,
  ArrowLeft,
} from "lucide-react";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import { ScrollArea } from "../components/ui/scroll-area";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Area,
  AreaChart,
  ReferenceLine,
} from "recharts";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

export default function Dashboard() {
  // State - Model 1
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamMode, setStreamMode] = useState("simulated");
  const [health, setHealth] = useState(null);
  const [alerts, setAlerts] = useState([]);
  const [scoreHistory, setScoreHistory] = useState([]);
  const [modelStats, setModelStats] = useState(null);
  const [latestPrediction, setLatestPrediction] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  // State - Model 2 (Federated + Drift)
  const [federatedStatus, setFederatedStatus] = useState(null);
  const [driftStatus, setDriftStatus] = useState(null);
  const [driftEvents, setDriftEvents] = useState([]);
  const [driftInjectionActive, setDriftInjectionActive] = useState(false);
  const [activeTab, setActiveTab] = useState("overview");
  
  // State - Model 3 (Digital Twin)
  const [twinPredictions, setTwinPredictions] = useState([]);
  const [riskScore, setRiskScore] = useState(null);
  const [liveVsPredicted, setLiveVsPredicted] = useState(null);
  
  // State - Model 4 (XAI)
  const [explanation, setExplanation] = useState(null);
  
  // State - Model 5 (JARVIS)
  const [jarvisQuery, setJarvisQuery] = useState("");
  const [jarvisHistory, setJarvisHistory] = useState([]);
  const [jarvisLoading, setJarvisLoading] = useState(false);
  
  // State - Model 6 (Settings/Personalization)
  const [preferences, setPreferences] = useState(null);
  const [experiments, setExperiments] = useState([]);
  const [reportData, setReportData] = useState(null);
  
  const streamIntervalRef = useRef(null);
  const fileInputRef = useRef(null);

  // Fetch initial data
  const fetchInitialData = useCallback(async () => {
    try {
      const [healthRes, alertsRes, historyRes, statsRes, fedRes, driftRes, driftEventsRes] = await Promise.all([
        axios.get(`${API}/health`),
        axios.get(`${API}/alerts`),
        axios.get(`${API}/history?limit=100`),
        axios.get(`${API}/model/stats`),
        axios.get(`${API}/federated/status`),
        axios.get(`${API}/drift/status`),
        axios.get(`${API}/drift/events?limit=20`),
      ]);

      setHealth(healthRes.data);
      setAlerts(alertsRes.data.alerts || []);
      setScoreHistory(
        (historyRes.data.history || []).map((item, index) => ({
          ...item,
          index,
          time: new Date(item.timestamp).toLocaleTimeString(),
        }))
      );
      setModelStats(statsRes.data);
      setStreamMode(healthRes.data.stream_mode || "simulated");
      setDriftInjectionActive(healthRes.data.drift_injection_active || false);
      setFederatedStatus(fedRes.data);
      setDriftStatus(driftRes.data);
      setDriftEvents(driftEventsRes.data.events || []);
      setIsLoading(false);
    } catch (error) {
      console.error("Error fetching initial data:", error);
      toast.error("Failed to connect to backend");
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchInitialData();
  }, [fetchInitialData]);

  // Stream next data point
  const fetchNextDataPoint = useCallback(async () => {
    try {
      const response = await axios.get(`${API}/stream/next`);
      const data = response.data;

      setLatestPrediction(data);
      setHealth((prev) => ({
        ...data.system_status,
        data_points_processed: (prev?.data_points_processed || 0) + 1,
        stream_mode: streamMode,
        drift_injection_active: driftInjectionActive,
      }));

      // Update drift status
      if (data.drift_status) {
        setDriftStatus((prev) => ({
          ...prev,
          ...data.drift_status,
        }));
        
        if (data.drift_status.drift_detected) {
          toast.warning(`Drift detected: ${data.drift_status.drift_type}`, {
            duration: 3000,
          });
          // Refresh drift events
          const eventsRes = await axios.get(`${API}/drift/events?limit=20`);
          setDriftEvents(eventsRes.data.events || []);
        }
      }

      // Update score history
      setScoreHistory((prev) => {
        const newHistory = [
          ...prev,
          {
            score: data.anomaly_score,
            timestamp: data.timestamp,
            index: prev.length,
            time: new Date(data.timestamp).toLocaleTimeString(),
            health: data.system_status.health,
            confidence: data.system_status.confidence,
            avg_score: data.system_status.avg_score,
            drift: data.drift_status?.drift_detected ? 1 : 0,
          },
        ].slice(-100);
        return newHistory;
      });

      // Refresh federated status periodically
      if (data.federated_round % 5 === 0) {
        const fedRes = await axios.get(`${API}/federated/status`);
        setFederatedStatus(fedRes.data);
      }

      // Check for alerts
      if (data.system_status.health === "UNSTABLE") {
        toast.error("System UNSTABLE - High anomaly detected!", { duration: 3000 });
      }
    } catch (error) {
      console.error("Error fetching data point:", error);
    }
  }, [streamMode, driftInjectionActive]);

  // Start/Stop streaming
  const toggleStreaming = useCallback(() => {
    if (isStreaming) {
      clearInterval(streamIntervalRef.current);
      streamIntervalRef.current = null;
      setIsStreaming(false);
      toast.info("Streaming paused");
    } else {
      setIsStreaming(true);
      fetchNextDataPoint();
      streamIntervalRef.current = setInterval(fetchNextDataPoint, 1000);
      toast.success("Streaming started");
    }
  }, [isStreaming, fetchNextDataPoint]);

  useEffect(() => {
    return () => {
      if (streamIntervalRef.current) {
        clearInterval(streamIntervalRef.current);
      }
    };
  }, []);

  // Mode change
  const handleModeChange = async (mode) => {
    try {
      await axios.post(`${API}/stream/config`, { mode });
      setStreamMode(mode);
      toast.success(`Mode changed to: ${mode}`);
    } catch (error) {
      toast.error("Failed to change mode");
    }
  };

  // CSV upload
  const handleFileUpload = async (event) => {
    const file = event.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await axios.post(`${API}/upload/csv`, formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      toast.success(`CSV uploaded: ${response.data.rows_loaded} rows`);
      setStreamMode("csv");
    } catch (error) {
      toast.error(error.response?.data?.detail || "Failed to upload CSV");
    }
  };

  // Reset
  const handleReset = async () => {
    try {
      if (isStreaming) {
        clearInterval(streamIntervalRef.current);
        setIsStreaming(false);
      }
      await axios.post(`${API}/model/reset`);
      setScoreHistory([]);
      setLatestPrediction(null);
      setAlerts([]);
      setDriftEvents([]);
      setDriftInjectionActive(false);
      await fetchInitialData();
      toast.success("System reset successfully");
    } catch (error) {
      toast.error("Failed to reset");
    }
  };

  // Clear alerts
  const handleClearAlerts = async () => {
    try {
      await axios.delete(`${API}/alerts`);
      setAlerts([]);
      toast.success("Alerts cleared");
    } catch (error) {
      toast.error("Failed to clear alerts");
    }
  };

  // Export
  const handleExport = (format) => {
    window.open(`${API}/export/${format}`, "_blank");
    toast.success(`Exporting as ${format.toUpperCase()}`);
  };

  // Inject drift
  const handleDriftInjection = async () => {
    try {
      const newState = !driftInjectionActive;
      await axios.post(`${API}/drift/inject`, { active: newState });
      setDriftInjectionActive(newState);
      toast[newState ? "warning" : "success"](
        newState ? "Drift injection ACTIVATED" : "Drift injection deactivated"
      );
      
      // Refresh data
      const [driftRes, driftEventsRes, fedRes] = await Promise.all([
        axios.get(`${API}/drift/status`),
        axios.get(`${API}/drift/events?limit=20`),
        axios.get(`${API}/federated/status`),
      ]);
      setDriftStatus(driftRes.data);
      setDriftEvents(driftEventsRes.data.events || []);
      setFederatedStatus(fedRes.data);
    } catch (error) {
      toast.error("Failed to toggle drift injection");
    }
  };

  // Trigger aggregation
  const handleAggregation = async () => {
    try {
      await axios.post(`${API}/federated/aggregate`);
      const fedRes = await axios.get(`${API}/federated/status`);
      setFederatedStatus(fedRes.data);
      toast.success("Weight aggregation completed");
    } catch (error) {
      toast.error("Failed to aggregate weights");
    }
  };

  // MODEL-3: Digital Twin Functions
  const fetchTwinPredictions = async () => {
    try {
      const [predRes, riskRes, compRes] = await Promise.all([
        axios.get(`${API}/twin/predict-health?steps=10`),
        axios.get(`${API}/twin/risk-score`),
        axios.get(`${API}/twin/comparison`)
      ]);
      setTwinPredictions(predRes.data.predictions || []);
      setRiskScore(riskRes.data);
      setLiveVsPredicted(compRes.data);
    } catch (error) {
      console.error("Failed to fetch twin data:", error);
    }
  };

  const runSimulation = async (scenarioType, params) => {
    try {
      const res = await axios.post(`${API}/twin/simulate`, {
        scenario_type: scenarioType,
        params: params
      });
      toast.success(`Simulation completed: ${scenarioType}`);
      return res.data;
    } catch (error) {
      toast.error("Failed to run simulation");
    }
  };

  // MODEL-4: XAI Functions
  const fetchExplanation = async () => {
    try {
      const res = await axios.get(`${API}/explain/health`);
      setExplanation(res.data);
    } catch (error) {
      console.error("Failed to fetch explanation:", error);
    }
  };

  // MODEL-5: JARVIS Functions
  const handleJarvisQuery = async (e) => {
    if (e) e.preventDefault();
    if (!jarvisQuery.trim()) return;

    setJarvisLoading(true);
    try {
      const res = await axios.post(`${API}/jarvis/query`, { query: jarvisQuery });
      setJarvisHistory(prev => [...prev, res.data]);
      setJarvisQuery("");
      toast.success("JARVIS responded");
    } catch (error) {
      toast.error("JARVIS query failed");
    } finally {
      setJarvisLoading(false);
    }
  };

  // MODEL-6: Settings/Personalization Functions
  const fetchPreferences = async () => {
    try {
      const res = await axios.get(`${API}/user/preferences`);
      setPreferences(res.data);
    } catch (error) {
      console.error("Failed to fetch preferences:", error);
    }
  };

  const updatePreferences = async (updates) => {
    try {
      await axios.post(`${API}/user/preferences`, { preferences: updates });
      setPreferences(prev => ({ ...prev, ...updates }));
      toast.success("Preferences updated");
    } catch (error) {
      toast.error("Failed to update preferences");
    }
  };

  const fetchExperiments = async () => {
    try {
      const res = await axios.get(`${API}/experiments/list`);
      setExperiments(res.data.experiments || []);
    } catch (error) {
      console.error("Failed to fetch experiments:", error);
    }
  };

  const runExperiment = async (experimentType, duration) => {
    try {
      const res = await axios.post(`${API}/experiments/run`, {
        experiment_type: experimentType,
        duration_seconds: duration
      });
      setExperiments(prev => [...prev, res.data]);
      toast.success(`Experiment started: ${experimentType}`);
    } catch (error) {
      toast.error("Failed to run experiment");
    }
  };

  const generateReport = async () => {
    try {
      const res = await axios.get(`${API}/reports/generate`, { responseType: 'blob' });
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'jarvis_research_report.json');
      document.body.appendChild(link);
      link.click();
      link.remove();
      toast.success("Report downloaded!");
    } catch (error) {
      toast.error("Failed to generate report");
    }
  };

  // Fetch twin and explanation data periodically when on those tabs
  useEffect(() => {
    if (activeTab === "twin") {
      fetchTwinPredictions();
      const interval = setInterval(fetchTwinPredictions, 5000);
      return () => clearInterval(interval);
    } else if (activeTab === "jarvis") {
      fetchExplanation();
    } else if (activeTab === "settings") {
      fetchPreferences();
      fetchExperiments();
    }
  }, [activeTab]);

  // Health styles
  const getHealthStyles = (status) => {
    switch (status) {
      case "STABLE":
      case "HEALTHY":
        return {
          bg: "bg-emerald-500",
          glow: "glow-green",
          text: "text-emerald-400",
          badge: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
        };
      case "WARNING":
      case "DEGRADED":
        return {
          bg: "bg-amber-500",
          glow: "glow-yellow",
          text: "text-amber-400",
          badge: "bg-amber-500/20 text-amber-400 border-amber-500/30",
        };
      case "UNSTABLE":
      case "CRITICAL":
        return {
          bg: "bg-rose-500",
          glow: "glow-red",
          text: "text-rose-400",
          badge: "bg-rose-500/20 text-rose-400 border-rose-500/30",
        };
      default:
        return {
          bg: "bg-muted",
          glow: "",
          text: "text-muted-foreground",
          badge: "bg-muted text-muted-foreground",
        };
    }
  };

  const healthStyles = getHealthStyles(health?.health);
  const globalHealthStyles = getHealthStyles(federatedStatus?.global_health);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background" data-testid="loading-screen">
        <div className="text-center space-y-4">
          <Network className="w-16 h-16 text-primary animate-pulse mx-auto" />
          <p className="text-muted-foreground font-mono text-sm tracking-wider">
            INITIALIZING MODEL-2: FEDERATED + DRIFT...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-4 md:p-6 lg:p-8" data-testid="dashboard">
      {/* Header */}
      <header className="mb-6">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="relative">
              <Network className="w-10 h-10 text-primary" />
              <div className={`absolute -top-1 -right-1 w-3 h-3 rounded-full ${healthStyles.bg} ${health?.health !== "STABLE" ? "animate-pulse" : ""}`} />
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-heading font-bold tracking-tight text-foreground" data-testid="dashboard-title">
                MODEL-2
              </h1>
              <p className="text-xs md:text-sm text-muted-foreground tracking-widest uppercase">
                Federated Learning + Concept Drift Detection
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 flex-wrap">
            {/* Home Link */}
            <Link to="/">
              <Button
                variant="outline"
                size="sm"
                className="font-mono text-xs tracking-wider border-white/20 hover:border-cyan-500/50"
                data-testid="home-btn"
              >
                <Home className="w-4 h-4 mr-2" />
                HOME
              </Button>
            </Link>

            {/* JARVIS-X Link */}
            <Link to="/jarvis-x">
              <Button
                variant="default"
                size="sm"
                className="font-mono text-xs tracking-wider bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500"
                data-testid="jarvis-x-btn"
              >
                <Mic className="w-4 h-4 mr-2" />
                JARVIS-X
              </Button>
            </Link>

            {/* Drift Injection Toggle */}
            <Button
              variant={driftInjectionActive ? "destructive" : "outline"}
              size="sm"
              onClick={handleDriftInjection}
              className="font-mono text-xs tracking-wider"
              data-testid="drift-inject-btn"
            >
              <Waves className={`w-4 h-4 mr-2 ${driftInjectionActive ? "animate-pulse" : ""}`} />
              {driftInjectionActive ? "DRIFT ON" : "INJECT DRIFT"}
            </Button>

            <Badge
              variant="outline"
              className={`${healthStyles.badge} px-3 py-1 font-mono text-xs border`}
              data-testid="health-badge"
            >
              <span className={`w-2 h-2 rounded-full ${healthStyles.bg} mr-2 ${health?.health !== "STABLE" ? "animate-pulse" : ""}`} />
              {health?.health || "UNKNOWN"}
            </Badge>

            <Button
              variant={isStreaming ? "destructive" : "default"}
              size="sm"
              onClick={toggleStreaming}
              className="font-mono text-xs tracking-wider"
              data-testid="stream-toggle-btn"
            >
              {isStreaming ? (
                <>
                  <Pause className="w-4 h-4 mr-2" />
                  STOP
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 mr-2" />
                  START
                </>
              )}
            </Button>
          </div>
        </div>
      </header>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="mb-6">
        <TabsList className="bg-muted/50 border border-border">
          <TabsTrigger value="overview" className="font-mono text-xs" data-testid="tab-overview">
            <Activity className="w-4 h-4 mr-2" />
            OVERVIEW
          </TabsTrigger>
          <TabsTrigger value="federated" className="font-mono text-xs" data-testid="tab-federated">
            <Network className="w-4 h-4 mr-2" />
            FEDERATED
          </TabsTrigger>
          <TabsTrigger value="drift" className="font-mono text-xs" data-testid="tab-drift">
            <Waves className="w-4 h-4 mr-2" />
            DRIFT
          </TabsTrigger>
          <TabsTrigger value="twin" className="font-mono text-xs" data-testid="tab-twin">
            <CircleDot className="w-4 h-4 mr-2" />
            DIGITAL TWIN
          </TabsTrigger>
          <TabsTrigger value="jarvis" className="font-mono text-xs" data-testid="tab-jarvis">
            <Brain className="w-4 h-4 mr-2" />
            JARVIS
          </TabsTrigger>
          <TabsTrigger value="settings" className="font-mono text-xs" data-testid="tab-settings">
            <Settings className="w-4 h-4 mr-2" />
            SETTINGS
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4 md:gap-6">
            {/* Left Column */}
            <div className="lg:col-span-3 space-y-4">
              {/* Quick Stats */}
              <Card className="glass-panel corner-brackets" data-testid="stats-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    SYSTEM METRICS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-muted-foreground">ANOMALY SCORE</span>
                      <span className={`font-mono text-lg font-bold ${latestPrediction?.anomaly_score > 0.7 ? "text-rose-400" : "text-primary"}`} data-testid="anomaly-score">
                        {latestPrediction?.anomaly_score?.toFixed(4) || "0.0000"}
                      </span>
                    </div>
                    <Progress value={(latestPrediction?.anomaly_score || 0) * 100} className="h-1.5" />
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className="text-xs text-muted-foreground">CONFIDENCE</span>
                      <span className="font-mono text-lg font-bold text-emerald-400" data-testid="confidence-value">
                        {((health?.confidence || 0) * 100).toFixed(1)}%
                      </span>
                    </div>
                    <Progress value={(health?.confidence || 0) * 100} className="h-1.5" />
                  </div>

                  <div className="flex justify-between items-center pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">DATA POINTS</span>
                    <span className="font-mono text-sm text-primary" data-testid="data-points-count">
                      {health?.data_points_processed || 0}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">DRIFT EVENTS</span>
                    <span className={`font-mono text-sm ${(driftStatus?.drift_count || 0) > 0 ? "text-amber-400" : "text-muted-foreground"}`} data-testid="drift-count">
                      {driftStatus?.drift_count || 0}
                    </span>
                  </div>

                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">FED ROUNDS</span>
                    <span className="font-mono text-sm text-secondary" data-testid="fed-rounds">
                      {federatedStatus?.aggregation_rounds || 0}
                    </span>
                  </div>
                </CardContent>
              </Card>

              {/* Data Source */}
              <Card className="glass-panel" data-testid="data-source-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Database className="w-4 h-4 text-primary" />
                    DATA SOURCE
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <Select value={streamMode} onValueChange={handleModeChange}>
                    <SelectTrigger className="font-mono text-xs" data-testid="mode-select">
                      <SelectValue placeholder="Select mode" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="simulated">SIMULATED</SelectItem>
                      <SelectItem value="csv">CSV DATA</SelectItem>
                    </SelectContent>
                  </Select>

                  <div
                    className="upload-area rounded p-4 text-center cursor-pointer"
                    onClick={() => fileInputRef.current?.click()}
                    data-testid="csv-upload-area"
                  >
                    <Upload className="w-6 h-6 mx-auto mb-2 text-muted-foreground" />
                    <p className="text-xs text-muted-foreground">Upload CSV</p>
                    <input
                      ref={fileInputRef}
                      type="file"
                      accept=".csv"
                      onChange={handleFileUpload}
                      className="hidden"
                    />
                  </div>
                </CardContent>
              </Card>

              {/* Actions */}
              <Card className="glass-panel" data-testid="actions-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Settings className="w-4 h-4 text-primary" />
                    ACTIONS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button variant="outline" size="sm" className="w-full font-mono text-xs justify-start" onClick={handleReset} data-testid="reset-model-btn">
                    <RefreshCw className="w-4 h-4 mr-2" />
                    RESET ALL
                  </Button>
                  <Button variant="outline" size="sm" className="w-full font-mono text-xs justify-start" onClick={handleAggregation} data-testid="aggregate-btn">
                    <GitBranch className="w-4 h-4 mr-2" />
                    AGGREGATE
                  </Button>
                  <Button variant="outline" size="sm" className="w-full font-mono text-xs justify-start" onClick={() => handleExport("json")} data-testid="export-json-btn">
                    <FileJson className="w-4 h-4 mr-2" />
                    EXPORT JSON
                  </Button>
                  <Button variant="outline" size="sm" className="w-full font-mono text-xs justify-start" onClick={() => handleExport("csv")} data-testid="export-csv-btn">
                    <FileSpreadsheet className="w-4 h-4 mr-2" />
                    EXPORT CSV
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Center Column - Charts */}
            <div className="lg:col-span-6 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="main-chart-card">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                      <Activity className="w-4 h-4 text-primary" />
                      LIVE ANOMALY SCORE
                    </CardTitle>
                    <div className="flex items-center gap-2">
                      {driftInjectionActive && (
                        <Badge variant="destructive" className="text-xs animate-pulse">
                          DRIFT ACTIVE
                        </Badge>
                      )}
                      <Badge variant="outline" className="font-mono text-xs">
                        {scoreHistory.length} SAMPLES
                      </Badge>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="h-[280px]" data-testid="anomaly-chart">
                    <ResponsiveContainer width="100%" height="100%">
                      <AreaChart data={scoreHistory}>
                        <defs>
                          <linearGradient id="scoreGradient" x1="0" y1="0" x2="0" y2="1">
                            <stop offset="5%" stopColor="hsl(184, 100%, 50%)" stopOpacity={0.3} />
                            <stop offset="95%" stopColor="hsl(184, 100%, 50%)" stopOpacity={0} />
                          </linearGradient>
                        </defs>
                        <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                        <XAxis dataKey="time" stroke="rgba(255,255,255,0.3)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }} tickLine={false} />
                        <YAxis domain={[0, "auto"]} stroke="rgba(255,255,255,0.3)" tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }} tickLine={false} />
                        <Tooltip
                          contentStyle={{
                            backgroundColor: "rgba(0, 0, 0, 0.9)",
                            border: "1px solid rgba(0, 240, 255, 0.3)",
                            borderRadius: "4px",
                            fontFamily: "JetBrains Mono",
                            fontSize: "12px",
                          }}
                        />
                        <ReferenceLine y={0.7} stroke="rgba(244, 63, 94, 0.5)" strokeDasharray="5 5" label={{ value: "THRESHOLD", fill: "rgba(244, 63, 94, 0.7)", fontSize: 10 }} />
                        <Area type="monotone" dataKey="score" stroke="hsl(184, 100%, 50%)" strokeWidth={2} fill="url(#scoreGradient)" dot={false} activeDot={{ r: 4, fill: "hsl(184, 100%, 50%)" }} />
                      </AreaChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              {/* Secondary Charts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Card className="glass-panel" data-testid="confidence-chart-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                      <Shield className="w-4 h-4 text-emerald-400" />
                      CONFIDENCE TREND
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[140px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={scoreHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="time" hide />
                          <YAxis domain={[0, 1]} hide />
                          <Line type="monotone" dataKey="confidence" stroke="#10b981" strokeWidth={2} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>

                <Card className="glass-panel" data-testid="avg-score-chart-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                      <TrendingUp className="w-4 h-4 text-secondary" />
                      MOVING AVERAGE
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className="h-[140px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={scoreHistory}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis dataKey="time" hide />
                          <YAxis domain={[0, "auto"]} hide />
                          <Line type="monotone" dataKey="avg_score" stroke="#a855f7" strokeWidth={2} dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>

            {/* Right Column */}
            <div className="lg:col-span-3 space-y-4">
              {/* Global Health */}
              <Card className={`glass-panel ${globalHealthStyles.glow}`} data-testid="global-health-panel">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Network className="w-4 h-4 text-primary" />
                    GLOBAL HEALTH
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-center py-4">
                    <div className="text-center">
                      <div className={`w-16 h-16 rounded-full ${globalHealthStyles.bg} flex items-center justify-center mx-auto mb-3 ${federatedStatus?.global_health !== "HEALTHY" ? "animate-pulse" : ""}`}>
                        <Network className="w-8 h-8 text-white" />
                      </div>
                      <p className={`font-heading font-bold text-xl ${globalHealthStyles.text}`} data-testid="global-health-text">
                        {federatedStatus?.global_health || "UNKNOWN"}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {federatedStatus?.online_nodes || 0}/{federatedStatus?.total_nodes || 0} nodes online
                      </p>
                    </div>
                  </div>
                </CardContent>
              </Card>

              {/* Latest Data */}
              {latestPrediction && (
                <Card className="glass-panel" data-testid="latest-prediction-card">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                      <Zap className="w-4 h-4 text-primary" />
                      LATEST DATA
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <div className={`p-3 rounded border ${latestPrediction.is_anomaly ? "border-rose-500/30 bg-rose-500/10" : "border-border bg-muted/20"}`}>
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-muted-foreground">FEATURES</span>
                        <div className="flex gap-1">
                          {latestPrediction.is_anomaly && (
                            <Badge variant="destructive" className="text-xs">ANOMALY</Badge>
                          )}
                          {latestPrediction.drift_status?.drift_detected && (
                            <Badge className="text-xs bg-amber-500/20 text-amber-400 border-amber-500/30">DRIFT</Badge>
                          )}
                        </div>
                      </div>
                      <div className="grid grid-cols-5 gap-1">
                        {latestPrediction.data_point?.map((val, i) => (
                          <div key={i} className="bg-background/50 rounded px-1 py-0.5 text-center">
                            <span className="font-mono text-xs text-foreground">{val.toFixed(2)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              )}

              {/* Alerts */}
              <Card className="glass-panel" data-testid="alerts-card">
                <CardHeader className="pb-2">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                      <AlertTriangle className="w-4 h-4 text-amber-400" />
                      ALERTS
                    </CardTitle>
                    <Button variant="ghost" size="icon" className="h-6 w-6" onClick={handleClearAlerts} data-testid="clear-alerts-btn">
                      <Trash2 className="w-3 h-3" />
                    </Button>
                  </div>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[150px]">
                    {alerts.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-6 text-muted-foreground">
                        <Shield className="w-6 h-6 mb-2 opacity-50" />
                        <p className="text-xs">No alerts</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {alerts.slice(-5).map((alert, index) => (
                          <div
                            key={alert.id || index}
                            className={`p-2 rounded border ${alert.severity === "critical" ? "border-rose-500/30 bg-rose-500/10" : "border-amber-500/30 bg-amber-500/10"}`}
                          >
                            <p className={`text-xs font-medium ${alert.severity === "critical" ? "text-rose-400" : "text-amber-400"}`}>
                              {alert.message}
                            </p>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Federated Tab */}
        <TabsContent value="federated" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Federated Stats */}
            <div className="lg:col-span-3 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="fed-stats-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <GitBranch className="w-4 h-4 text-primary" />
                    FEDERATION STATS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">TOTAL NODES</span>
                    <span className="font-mono text-lg font-bold text-primary">{federatedStatus?.total_nodes || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">ONLINE</span>
                    <span className="font-mono text-lg font-bold text-emerald-400">{federatedStatus?.online_nodes || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">ROUNDS</span>
                    <span className="font-mono text-lg font-bold text-secondary">{federatedStatus?.aggregation_rounds || 0}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">TOTAL DATA</span>
                    <span className="font-mono text-sm text-muted-foreground">{federatedStatus?.total_data_points || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">GLOBAL AVG</span>
                    <span className="font-mono text-sm text-muted-foreground">{federatedStatus?.global_avg_score?.toFixed(4) || "0.0000"}</span>
                  </div>
                  <Button variant="outline" size="sm" className="w-full font-mono text-xs mt-2" onClick={handleAggregation} data-testid="fed-aggregate-btn">
                    <GitBranch className="w-4 h-4 mr-2" />
                    AGGREGATE NOW
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Node Cards */}
            <div className="lg:col-span-9">
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4" data-testid="node-cards-grid">
                {federatedStatus?.nodes && Object.entries(federatedStatus.nodes).map(([nodeId, node]) => {
                  const nodeHealth = getHealthStyles(node.health);
                  return (
                    <Card key={nodeId} className={`glass-panel ${nodeHealth.glow}`} data-testid={`node-card-${nodeId}`}>
                      <CardHeader className="pb-2">
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                            <Server className="w-4 h-4 text-primary" />
                            {node.name}
                          </CardTitle>
                          <Badge variant="outline" className={`${nodeHealth.badge} text-xs border`}>
                            {node.health}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-2">
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Location</span>
                          <span className="font-mono text-xs text-foreground">{node.location}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Data Points</span>
                          <span className="font-mono text-xs text-primary">{node.data_points_processed}</span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Avg Score</span>
                          <span className={`font-mono text-xs ${node.avg_score > 0.6 ? "text-amber-400" : "text-emerald-400"}`}>
                            {node.avg_score?.toFixed(4)}
                          </span>
                        </div>
                        <div className="flex justify-between items-center">
                          <span className="text-xs text-muted-foreground">Drift Events</span>
                          <span className={`font-mono text-xs ${node.drift_status?.drift_count > 0 ? "text-amber-400" : "text-muted-foreground"}`}>
                            {node.drift_status?.drift_count || 0}
                          </span>
                        </div>
                        <Progress value={Math.min(node.avg_score * 100, 100)} className="h-1 mt-2" />
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* Drift Tab */}
        <TabsContent value="drift" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Drift Stats */}
            <div className="lg:col-span-3 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="drift-stats-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Waves className="w-4 h-4 text-primary" />
                    DRIFT DETECTION
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">TOTAL SAMPLES</span>
                    <span className="font-mono text-lg font-bold text-primary">{driftStatus?.total_samples || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">DRIFT COUNT</span>
                    <span className={`font-mono text-lg font-bold ${(driftStatus?.drift_count || 0) > 0 ? "text-amber-400" : "text-emerald-400"}`}>
                      {driftStatus?.drift_count || 0}
                    </span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">ADWIN</span>
                    <span className="font-mono text-sm text-muted-foreground">{driftStatus?.adwin_drifts || 0}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-muted-foreground">PAGE-HINKLEY</span>
                    <span className="font-mono text-sm text-muted-foreground">{driftStatus?.ph_drifts || 0}</span>
                  </div>
                  <div className="flex justify-between items-center pt-2 border-t border-border/50">
                    <span className="text-xs text-muted-foreground">IN DRIFT</span>
                    <Badge variant={driftStatus?.in_drift ? "destructive" : "outline"} className="text-xs">
                      {driftStatus?.in_drift ? "YES" : "NO"}
                    </Badge>
                  </div>
                </CardContent>
              </Card>

              <Card className="glass-panel" data-testid="drift-controls-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Settings className="w-4 h-4 text-primary" />
                    CONTROLS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button
                    variant={driftInjectionActive ? "destructive" : "outline"}
                    size="sm"
                    className="w-full font-mono text-xs"
                    onClick={handleDriftInjection}
                    data-testid="drift-inject-btn-2"
                  >
                    <Waves className={`w-4 h-4 mr-2 ${driftInjectionActive ? "animate-pulse" : ""}`} />
                    {driftInjectionActive ? "STOP DRIFT" : "INJECT DRIFT"}
                  </Button>
                  <p className="text-xs text-muted-foreground text-center pt-2">
                    Simulate concept drift by shifting data distribution
                  </p>
                </CardContent>
              </Card>
            </div>

            {/* Drift Events */}
            <div className="lg:col-span-9">
              <Card className="glass-panel" data-testid="drift-events-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Radio className="w-4 h-4 text-amber-400" />
                    DRIFT EVENTS LOG
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ScrollArea className="h-[400px]">
                    {driftEvents.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                        <Waves className="w-12 h-12 mb-4 opacity-30" />
                        <p className="text-sm">No drift events detected</p>
                        <p className="text-xs mt-2">Click "Inject Drift" to simulate distribution changes</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {driftEvents.map((event, index) => (
                          <div
                            key={event.id || index}
                            className="p-3 rounded border border-amber-500/30 bg-amber-500/10"
                            data-testid={`drift-event-${index}`}
                          >
                            <div className="flex items-center justify-between mb-1">
                              <Badge className="text-xs bg-amber-500/20 text-amber-400 border-amber-500/30">
                                {event.type}
                              </Badge>
                              <span className="text-xs text-muted-foreground">
                                Sample #{event.sample_number}
                              </span>
                            </div>
                            <div className="flex items-center justify-between">
                              <span className="text-xs text-muted-foreground">Score: {event.value}</span>
                              <span className="text-xs text-muted-foreground">
                                {new Date(event.timestamp).toLocaleString()}
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Digital Twin Tab - MODEL-3 */}
        <TabsContent value="twin" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Risk Score Panel */}
            <div className="lg:col-span-4 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="risk-score-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Shield className="w-4 h-4 text-primary" />
                    RISK ASSESSMENT
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {riskScore?.global_risk && (
                    <div className="space-y-4">
                      <div className="text-center py-4">
                        <div className={`text-5xl font-bold mb-2 ${
                          riskScore.global_risk.risk_category === 'CRITICAL' ? 'text-rose-400' :
                          riskScore.global_risk.risk_category === 'HIGH' ? 'text-amber-400' :
                          riskScore.global_risk.risk_category === 'MEDIUM' ? 'text-yellow-400' :
                          'text-emerald-400'
                        }`}>
                          {riskScore.global_risk.risk_score.toFixed(0)}
                        </div>
                        <Badge variant={riskScore.global_risk.risk_category === 'LOW' ? 'outline' : 'destructive'} className="text-xs">
                          {riskScore.global_risk.risk_category} RISK
                        </Badge>
                      </div>
                      <div className="space-y-2 border-t border-border/50 pt-3">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Score Risk</span>
                          <span className="font-mono text-primary">{riskScore.global_risk.factors.score_risk.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Drift Risk</span>
                          <span className="font-mono text-amber-400">{riskScore.global_risk.factors.drift_risk.toFixed(1)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Data Risk</span>
                          <span className="font-mono text-muted-foreground">{riskScore.global_risk.factors.data_risk.toFixed(1)}</span>
                        </div>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Live vs Predicted */}
              <Card className="glass-panel" data-testid="live-vs-predicted-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <TrendingUp className="w-4 h-4 text-primary" />
                    LIVE VS PREDICTED
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {liveVsPredicted && (
                    <div className="space-y-3">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="p-3 rounded border border-border bg-muted/20">
                          <div className="text-xs text-muted-foreground mb-1">LIVE</div>
                          <div className="font-mono text-lg text-primary">{liveVsPredicted.live_state.health}</div>
                          <div className="text-xs text-muted-foreground mt-1">Score: {liveVsPredicted.live_state.score.toFixed(3)}</div>
                        </div>
                        <div className="p-3 rounded border border-primary/30 bg-primary/10">
                          <div className="text-xs text-muted-foreground mb-1">PREDICTED</div>
                          <div className="font-mono text-lg text-primary">{liveVsPredicted.predicted_state.health}</div>
                          <div className="text-xs text-muted-foreground mt-1">Score: {liveVsPredicted.predicted_state.score.toFixed(3)}</div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between pt-2 border-t border-border/50">
                        <span className="text-xs text-muted-foreground">Accuracy</span>
                        <span className="font-mono text-sm text-emerald-400">{(liveVsPredicted.accuracy * 100).toFixed(1)}%</span>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Simulation Controls */}
              <Card className="glass-panel" data-testid="simulation-controls-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Settings className="w-4 h-4 text-primary" />
                    WHAT-IF SIMULATIONS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full font-mono text-xs"
                    onClick={() => runSimulation("sustained_drift", {duration_minutes: 5, intensity: 0.7})}
                    data-testid="sim-drift-btn"
                  >
                    Simulate Sustained Drift
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full font-mono text-xs"
                    onClick={() => runSimulation("node_failure", {node_count: 2, total_nodes: 5})}
                    data-testid="sim-failure-btn"
                  >
                    Simulate Node Failure
                  </Button>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full font-mono text-xs"
                    onClick={() => runSimulation("aggregation_delay", {delay_rounds: 15})}
                    data-testid="sim-delay-btn"
                  >
                    Simulate Agg Delay
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Future Predictions Chart */}
            <div className="lg:col-span-8">
              <Card className="glass-panel" data-testid="predictions-chart-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <CircleDot className="w-4 h-4 text-primary" />
                    FUTURE HEALTH PREDICTIONS
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {twinPredictions.length > 0 ? (
                    <div className="h-[400px]">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={twinPredictions}>
                          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
                          <XAxis 
                            dataKey="step" 
                            stroke="rgba(255,255,255,0.3)" 
                            tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }} 
                            label={{ value: "Steps Ahead", fill: "rgba(255,255,255,0.5)", position: "insideBottom", offset: -5 }}
                          />
                          <YAxis 
                            domain={[0, 1]} 
                            stroke="rgba(255,255,255,0.3)" 
                            tick={{ fill: "rgba(255,255,255,0.5)", fontSize: 10 }}
                            label={{ value: "Anomaly Score", fill: "rgba(255,255,255,0.5)", angle: -90, position: "insideLeft" }}
                          />
                          <Tooltip
                            contentStyle={{
                              backgroundColor: "rgba(0, 0, 0, 0.9)",
                              border: "1px solid rgba(0, 240, 255, 0.3)",
                              borderRadius: "4px",
                              fontFamily: "JetBrains Mono",
                              fontSize: "12px",
                            }}
                          />
                          <ReferenceLine y={0.6} stroke="rgba(251, 191, 36, 0.5)" strokeDasharray="5 5" label={{ value: "WARNING", fill: "rgba(251, 191, 36, 0.7)", fontSize: 10 }} />
                          <ReferenceLine y={0.8} stroke="rgba(244, 63, 94, 0.5)" strokeDasharray="5 5" label={{ value: "CRITICAL", fill: "rgba(244, 63, 94, 0.7)", fontSize: 10 }} />
                          <Line type="monotone" dataKey="predicted_score" stroke="hsl(184, 100%, 50%)" strokeWidth={2} dot={{ fill: "hsl(184, 100%, 50%)", r: 4 }} />
                          <Line type="monotone" dataKey="confidence" stroke="#10b981" strokeWidth={1} strokeDasharray="3 3" dot={false} />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                      <div className="text-center">
                        <CircleDot className="w-12 h-12 mx-auto mb-3 opacity-50" />
                        <p className="text-sm">Waiting for data to generate predictions...</p>
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Prediction Details */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-4">
                {twinPredictions.slice(0, 5).map((pred, idx) => (
                  <Card key={idx} className="glass-panel" data-testid={`pred-step-${pred.step}`}>
                    <CardContent className="p-3">
                      <div className="text-xs text-muted-foreground mb-1">Step +{pred.step}</div>
                      <Badge variant={pred.risk_level === 'HIGH' ? 'destructive' : 'outline'} className="text-xs mb-2">
                        {pred.predicted_health}
                      </Badge>
                      <div className="text-xs text-muted-foreground">
                        Score: <span className="font-mono text-primary">{pred.predicted_score.toFixed(3)}</span>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        </TabsContent>

        {/* JARVIS Tab - MODEL-5 */}
        <TabsContent value="jarvis" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Explanation Panel - MODEL-4 Integration */}
            <div className="lg:col-span-4 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="explanation-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Brain className="w-4 h-4 text-primary" />
                    SYSTEM EXPLANATION (XAI)
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  {explanation ? (
                    <div className="space-y-3">
                      <div className="p-3 rounded border border-primary/30 bg-primary/10">
                        <div className="text-xs text-primary font-bold mb-2">CURRENT HEALTH</div>
                        <p className="text-sm text-foreground leading-relaxed">{explanation.explanation}</p>
                      </div>
                      <div className="space-y-2 pt-2 border-t border-border/50">
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Status</span>
                          <Badge variant="outline" className="text-xs">{explanation.health}</Badge>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Avg Score</span>
                          <span className="font-mono text-primary">{explanation.metrics?.avg_score?.toFixed(4)}</span>
                        </div>
                        <div className="flex justify-between text-xs">
                          <span className="text-muted-foreground">Samples</span>
                          <span className="font-mono text-muted-foreground">{explanation.metrics?.samples}</span>
                        </div>
                      </div>
                    </div>
                  ) : (
                    <div className="text-center py-6 text-muted-foreground">
                      <Brain className="w-8 h-8 mx-auto mb-2 opacity-50" />
                      <p className="text-xs">Loading explanation...</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              <Card className="glass-panel" data-testid="quick-insights-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Zap className="w-4 h-4 text-primary" />
                    QUICK INSIGHTS
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-2">
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start font-mono text-xs"
                    onClick={() => setJarvisQuery("What is the system health?")}
                  >
                    System Status
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start font-mono text-xs"
                    onClick={() => setJarvisQuery("Predict the future")}
                  >
                    Future Prediction
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start font-mono text-xs"
                    onClick={() => setJarvisQuery("What is the risk level?")}
                  >
                    Risk Assessment
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start font-mono text-xs"
                    onClick={() => setJarvisQuery("Why was drift detected?")}
                  >
                    Explain Drift
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="sm" 
                    className="w-full justify-start font-mono text-xs"
                    onClick={() => setJarvisQuery("How are the nodes?")}
                  >
                    Node Status
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* JARVIS Chat Interface */}
            <div className="lg:col-span-8">
              <Card className="glass-panel h-[600px] flex flex-col" data-testid="jarvis-chat-card">
                <CardHeader className="pb-2 border-b border-border/30">
                  <CardTitle className="text-lg font-heading tracking-tight flex items-center gap-2">
                    <Brain className="w-6 h-6 text-primary animate-pulse" />
                    JARVIS COGNITIVE ASSISTANT
                  </CardTitle>
                  <p className="text-xs text-muted-foreground font-mono">AI-Powered System Intelligence</p>
                </CardHeader>
                <CardContent className="flex-1 flex flex-col p-0">
                  {/* Chat History */}
                  <ScrollArea className="flex-1 p-4">
                    {jarvisHistory.length === 0 ? (
                      <div className="flex flex-col items-center justify-center h-full text-muted-foreground">
                        <Brain className="w-16 h-16 mb-4 opacity-30 animate-pulse" />
                        <p className="text-sm font-mono">Hello, I am JARVIS.</p>
                        <p className="text-xs mt-2">Ask me about the system state, predictions, risks, or explanations.</p>
                      </div>
                    ) : (
                      <div className="space-y-4">
                        {jarvisHistory.map((item, idx) => (
                          <div key={idx} className="space-y-2" data-testid={`jarvis-msg-${idx}`}>
                            {/* User Query */}
                            <div className="flex justify-end">
                              <div className="bg-primary/20 border border-primary/30 rounded-lg p-3 max-w-[80%]">
                                <p className="text-sm text-foreground">{item.query}</p>
                                <p className="text-xs text-muted-foreground mt-1 font-mono">
                                  {new Date(item.timestamp).toLocaleTimeString()}
                                </p>
                              </div>
                            </div>
                            {/* JARVIS Response */}
                            <div className="flex justify-start">
                              <div className="bg-muted/50 border border-border rounded-lg p-3 max-w-[80%]">
                                <div className="flex items-start gap-2">
                                  <Brain className="w-4 h-4 text-primary mt-0.5 flex-shrink-0" />
                                  <div>
                                    <p className="text-sm text-foreground leading-relaxed">{item.response}</p>
                                    {item.intent && (
                                      <Badge variant="outline" className="text-xs mt-2">
                                        Intent: {item.intent}
                                      </Badge>
                                    )}
                                  </div>
                                </div>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>

                  {/* Input Area */}
                  <div className="p-4 border-t border-border/30">
                    <form onSubmit={handleJarvisQuery} className="flex gap-2">
                      <input
                        type="text"
                        value={jarvisQuery}
                        onChange={(e) => setJarvisQuery(e.target.value)}
                        placeholder="Ask JARVIS anything..."
                        className="flex-1 px-4 py-2 bg-muted/50 border border-border rounded-md text-sm font-mono focus:outline-none focus:ring-2 focus:ring-primary"
                        disabled={jarvisLoading}
                        data-testid="jarvis-input"
                      />
                      <Button 
                        type="submit" 
                        disabled={jarvisLoading || !jarvisQuery.trim()}
                        className="font-mono"
                        data-testid="jarvis-submit-btn"
                      >
                        {jarvisLoading ? (
                          <RefreshCw className="w-4 h-4 animate-spin" />
                        ) : (
                          <Zap className="w-4 h-4" />
                        )}
                      </Button>
                    </form>
                    <p className="text-xs text-muted-foreground mt-2 font-mono">
                      Try: "What is the risk level?" or "Predict future health"
                    </p>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Settings Tab - MODEL-6 */}
        <TabsContent value="settings" className="mt-4">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-4">
            {/* Preferences Panel */}
            <div className="lg:col-span-4 space-y-4">
              <Card className="glass-panel corner-brackets" data-testid="preferences-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Settings className="w-4 h-4 text-primary" />
                    PREFERENCES
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  {preferences ? (
                    <>
                      <div className="space-y-2">
                        <label className="text-xs text-muted-foreground">Alert Threshold</label>
                        <Select 
                          value={String(preferences.alert_threshold)} 
                          onValueChange={(v) => updatePreferences({ alert_threshold: parseFloat(v) })}
                        >
                          <SelectTrigger className="font-mono text-xs" data-testid="alert-threshold-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="0.5">0.5 - Sensitive</SelectItem>
                            <SelectItem value="0.6">0.6 - Moderate</SelectItem>
                            <SelectItem value="0.7">0.7 - Default</SelectItem>
                            <SelectItem value="0.8">0.8 - Lenient</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-xs text-muted-foreground">Explanation Depth</label>
                        <Select 
                          value={preferences.explanation_depth} 
                          onValueChange={(v) => updatePreferences({ explanation_depth: v })}
                        >
                          <SelectTrigger className="font-mono text-xs" data-testid="explanation-depth-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="brief">Brief</SelectItem>
                            <SelectItem value="detailed">Detailed</SelectItem>
                            <SelectItem value="technical">Technical</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <label className="text-xs text-muted-foreground">Notification Level</label>
                        <Select 
                          value={preferences.notification_level} 
                          onValueChange={(v) => updatePreferences({ notification_level: v })}
                        >
                          <SelectTrigger className="font-mono text-xs" data-testid="notification-level-select">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="all">All Alerts</SelectItem>
                            <SelectItem value="critical">Critical Only</SelectItem>
                            <SelectItem value="none">None</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="flex items-center justify-between pt-2 border-t border-border/50">
                        <span className="text-xs text-muted-foreground">Auto Aggregation</span>
                        <Badge 
                          variant={preferences.auto_aggregation ? "default" : "outline"} 
                          className="cursor-pointer text-xs"
                          onClick={() => updatePreferences({ auto_aggregation: !preferences.auto_aggregation })}
                        >
                          {preferences.auto_aggregation ? "ON" : "OFF"}
                        </Badge>
                      </div>

                      <div className="flex items-center justify-between">
                        <span className="text-xs text-muted-foreground">Refresh Rate</span>
                        <span className="font-mono text-xs text-primary">{preferences.dashboard_refresh_rate}ms</span>
                      </div>
                    </>
                  ) : (
                    <div className="text-center py-4 text-muted-foreground">
                      <Settings className="w-8 h-8 mx-auto mb-2 opacity-50 animate-pulse" />
                      <p className="text-xs">Loading preferences...</p>
                    </div>
                  )}
                </CardContent>
              </Card>

              {/* Report Generation */}
              <Card className="glass-panel" data-testid="report-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Download className="w-4 h-4 text-primary" />
                    RESEARCH REPORT
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-xs text-muted-foreground">
                    Generate comprehensive report with system stats, performance metrics, and key findings.
                  </p>
                  <Button 
                    variant="outline" 
                    size="sm" 
                    className="w-full font-mono text-xs"
                    onClick={generateReport}
                    data-testid="generate-report-btn"
                  >
                    <Download className="w-4 h-4 mr-2" />
                    DOWNLOAD REPORT
                  </Button>
                </CardContent>
              </Card>
            </div>

            {/* Experiments Panel */}
            <div className="lg:col-span-8 space-y-4">
              <Card className="glass-panel" data-testid="experiments-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <Cpu className="w-4 h-4 text-primary" />
                    CONTROLLED EXPERIMENTS
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="font-mono text-xs"
                      onClick={() => runExperiment("sustained_drift_recovery", 120)}
                      data-testid="exp-drift-recovery-btn"
                    >
                      Drift Recovery Test
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="font-mono text-xs"
                      onClick={() => runExperiment("node_resilience", 90)}
                      data-testid="exp-node-resilience-btn"
                    >
                      Node Resilience Test
                    </Button>
                    <Button 
                      variant="outline" 
                      size="sm" 
                      className="font-mono text-xs"
                      onClick={() => runExperiment("aggregation_efficiency", 60)}
                      data-testid="exp-aggregation-btn"
                    >
                      Aggregation Efficiency
                    </Button>
                  </div>

                  <ScrollArea className="h-[300px]">
                    {experiments.length === 0 ? (
                      <div className="flex flex-col items-center justify-center py-16 text-muted-foreground">
                        <Cpu className="w-12 h-12 mb-4 opacity-30" />
                        <p className="text-sm">No experiments conducted yet</p>
                        <p className="text-xs mt-2">Click a button above to run an experiment</p>
                      </div>
                    ) : (
                      <div className="space-y-2">
                        {experiments.map((exp, index) => (
                          <div
                            key={exp.id || index}
                            className="p-3 rounded border border-primary/30 bg-primary/10"
                            data-testid={`experiment-${index}`}
                          >
                            <div className="flex items-center justify-between mb-2">
                              <Badge className="text-xs bg-primary/20 text-primary border-primary/30">
                                {exp.type}
                              </Badge>
                              <Badge variant={exp.status === "running" ? "default" : "outline"} className="text-xs">
                                {exp.status}
                              </Badge>
                            </div>
                            <div className="flex items-center justify-between text-xs text-muted-foreground">
                              <span>Duration: {exp.duration_seconds}s</span>
                              <span>{new Date(exp.started_at).toLocaleString()}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </ScrollArea>
                </CardContent>
              </Card>

              {/* System Summary */}
              <Card className="glass-panel" data-testid="system-summary-card">
                <CardHeader className="pb-2">
                  <CardTitle className="text-xs font-mono tracking-widest text-muted-foreground flex items-center gap-2">
                    <BarChart3 className="w-4 h-4 text-primary" />
                    SYSTEM SUMMARY
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="p-3 rounded border border-border bg-muted/20 text-center">
                      <div className="text-2xl font-bold text-primary">{health?.data_points_processed || 0}</div>
                      <div className="text-xs text-muted-foreground mt-1">Data Points</div>
                    </div>
                    <div className="p-3 rounded border border-border bg-muted/20 text-center">
                      <div className="text-2xl font-bold text-amber-400">{driftStatus?.drift_count || 0}</div>
                      <div className="text-xs text-muted-foreground mt-1">Drift Events</div>
                    </div>
                    <div className="p-3 rounded border border-border bg-muted/20 text-center">
                      <div className="text-2xl font-bold text-secondary">{federatedStatus?.aggregation_rounds || 0}</div>
                      <div className="text-xs text-muted-foreground mt-1">Fed Rounds</div>
                    </div>
                    <div className="p-3 rounded border border-border bg-muted/20 text-center">
                      <div className="text-2xl font-bold text-emerald-400">{federatedStatus?.total_nodes || 0}</div>
                      <div className="text-xs text-muted-foreground mt-1">Active Nodes</div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>
      </Tabs>

      {/* Footer */}
      <footer className="mt-6 pt-4 border-t border-border/30">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-2 text-xs text-muted-foreground">
          <p className="font-mono">
            MODEL-2 // FEDERATED LEARNING + CONCEPT DRIFT // {federatedStatus?.total_nodes || 0} NODES
          </p>
          <p className="font-mono">
            ROUND: {federatedStatus?.aggregation_rounds || 0} | DRIFTS: {driftStatus?.drift_count || 0}
          </p>
        </div>
      </footer>
    </div>
  );
}

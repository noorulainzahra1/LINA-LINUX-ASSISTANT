/**
 * Dashboard - Main landing page
 * Shows recent activity, quick tool shortcuts, and statistics
 */
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { 
  Terminal, 
  MessageSquare, 
  BarChart3, 
  Wrench, 
  Clock, 
  Zap,
  ArrowRight,
  TrendingUp,
  Activity,
  LogOut
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useSession } from '../contexts/SessionContext';
import ThemeToggle from '../components/ThemeToggle';
import { sessionAPI, toolsAPI } from '../services/api';
import type { ToolInfo } from '../types';

export default function Dashboard() {
  const navigate = useNavigate();
  const { session, clearSession } = useSession();
  const { user, logout } = useAuth();

  const handleLogout = () => {
    clearSession();
    logout();
    navigate('/');
  };

  const { data: analytics, isLoading: analyticsLoading } = useQuery({
    queryKey: ['analytics', session?.session_id],
    queryFn: () => sessionAPI.getAnalytics(session?.session_id || ''),
    enabled: !!session?.session_id,
    retry: 1,
    retryDelay: 1000,
    staleTime: 30000, // Cache for 30 seconds
  });

  const { data: toolsData, isLoading: toolsLoading } = useQuery({
    queryKey: ['tools'],
    queryFn: () => toolsAPI.list(),
  });

  // Redirect to model selection if no session (with useEffect to handle properly)
  useEffect(() => {
    if (!session) {
      const timer = setTimeout(() => {
        navigate('/model-selection');
      }, 1000); // Give time for session to load from localStorage
      return () => clearTimeout(timer);
    }
  }, [session, navigate]);
  
  if (!session) {
    return (
      <div className="min-h-screen bg-light-bg dark:bg-dark-bg flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-dark-text-secondary">Loading session...</p>
        </div>
      </div>
    );
  }

  // Get most frequently used tools (first 6)
  const popularTools = toolsData?.tools
    .filter(tool => tool.installed)
    .slice(0, 6) || [];

  return (
    <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark custom-scrollbar">
      {/* Modern Header */}
      <header className="bg-white dark:bg-dark-bg-secondary border-b-2 border-gray-200 dark:border-dark-border px-8 py-6 shadow-md">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-3 rounded-xl bg-gradient-button">
              <Terminal className="w-7 h-7 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-black text-gray-900 dark:text-dark-text">Dashboard</h1>
              <p className="text-sm font-semibold text-gray-600 dark:text-dark-text-secondary">
                {session.mode ? `${session.mode.charAt(0).toUpperCase() + session.mode.slice(1)} Mode` : 'Welcome'}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            {user && (
              <div className="text-sm text-gray-600 dark:text-dark-text-secondary mr-2">
                <span className="font-semibold">{user.username}</span>
              </div>
            )}
            <ThemeToggle />
            <button
              onClick={() => navigate('/tools')}
              className="cyber-button-secondary flex items-center"
            >
              <Wrench className="w-4 h-4 mr-2" />
              Tools
            </button>
            <button
              onClick={() => navigate('/chat')}
              className="cyber-button flex items-center"
            >
              <MessageSquare className="w-4 h-4 mr-2" />
              Start Chat
            </button>
            <button
              onClick={() => navigate('/analytics')}
              className="px-5 py-2.5 bg-white dark:bg-dark-bg-secondary border-2 border-gray-300 dark:border-dark-border text-gray-700 dark:text-dark-text rounded-xl hover:border-gray-400 dark:hover:border-dark-border-accent transition-colors font-semibold"
            >
              <BarChart3 className="w-5 h-5" />
            </button>
            <button
              onClick={handleLogout}
              className="px-5 py-2.5 bg-white dark:bg-dark-bg-secondary border-2 border-red-300 dark:border-red-500/50 text-red-600 dark:text-red-400 rounded-xl hover:border-red-400 dark:hover:border-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors font-semibold flex items-center"
              title="Logout"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Statistics Panel */}
        {analyticsLoading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue"></div>
          </div>
        ) : analytics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <StatCard
              icon={<Terminal className="w-6 h-6" />}
              label="Commands Executed"
              value={analytics.commands_executed}
              color="aqua"
            />
            <StatCard
              icon={<Wrench className="w-6 h-6" />}
              label="Tools Used"
              value={analytics.unique_tools_used}
              color="cyan"
            />
            <StatCard
              icon={<Clock className="w-6 h-6" />}
              label="Session Duration"
              value={`${Math.round(analytics.duration_minutes)}m`}
              color="gold"
            />
            <StatCard
              icon={<TrendingUp className="w-6 h-6" />}
              label="Plans Generated"
              value={analytics.plans_generated}
              color="green"
            />
          </div>
        )}

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Quick Tool Shortcuts */}
          <div className="lg:col-span-2">
            <div className="cyber-card">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text flex items-center">
                  <Zap className="w-5 h-5 mr-2 text-cyber-blue" />
                  Quick Tool Shortcuts
                </h2>
                <button
                  onClick={() => navigate('/tools')}
                  className="text-sm text-cyber-blue hover:text-cyber-blue-deep flex items-center"
                >
                  View All <ArrowRight className="w-4 h-4 ml-1" />
                </button>
              </div>
              
              {toolsLoading ? (
                <div className="flex items-center justify-center p-8">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-cyber-blue"></div>
                </div>
              ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {popularTools.map((tool) => (
                    <ToolShortcut key={tool.name} tool={tool} />
                  ))}
                  {popularTools.length === 0 && (
                    <p className="text-gray-600 dark:text-dark-text-secondary col-span-full text-center py-4">
                      No tools available
                    </p>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Recent Activity & Stats */}
          <div className="space-y-6">
            {/* Recent Activity */}
            <div className="cyber-card">
              <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text flex items-center mb-4">
                <Activity className="w-5 h-5 mr-2 text-cyber-blue" />
                Recent Activity
              </h2>
              {analytics && analytics.commands_executed > 0 ? (
                <div className="space-y-2">
                  <div className="text-sm text-gray-700 dark:text-dark-text-secondary">
                    <p className="font-semibold">Last Session</p>
                    <p className="text-gray-600 dark:text-dark-text-muted">
                      {analytics.commands_executed} commands executed
                    </p>
                  </div>
                  {analytics.tools_used_list.length > 0 && (
                    <div className="text-sm text-gray-700 dark:text-dark-text-secondary">
                      <p className="font-semibold">Recent Tools</p>
                      <div className="flex flex-wrap gap-1 mt-1">
                        {analytics.tools_used_list.slice(0, 5).map((tool) => (
                          <span
                            key={tool}
                            className="bg-light-bg dark:bg-dark-bg-secondary border border-cyber-blue/30 dark:border-cyber-blue/50 text-cyber-blue dark:text-cyber-blue px-2 py-1 rounded text-xs"
                          >
                            {tool}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <p className="text-gray-600 dark:text-dark-text-secondary text-sm">
                  No recent activity. Start using LINA to see your stats here!
                </p>
              )}
            </div>

            {/* Quick Actions */}
            <div className="cyber-card">
              <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text mb-4">Quick Actions</h2>
              <div className="space-y-2">
                <button
                  onClick={() => navigate('/chat')}
                  className="w-full cyber-button text-left"
                >
                  <MessageSquare className="w-4 h-4 inline mr-2" />
                  Start Chat Session
                </button>
                <button
                  onClick={() => navigate('/tools')}
                  className="w-full cyber-button text-left"
                >
                  <Wrench className="w-4 h-4 inline mr-2" />
                  Browse Tools
                </button>
                <button
                  onClick={() => navigate('/analytics')}
                  className="w-full cyber-button text-left"
                >
                  <BarChart3 className="w-4 h-4 inline mr-2" />
                  View Analytics
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Tools Used Summary */}
        {analytics && analytics.tools_used_list.length > 0 && (
          <div className="cyber-card">
            <h2 className="text-xl font-bold text-gray-900 dark:text-dark-text mb-4">
              All Tools Used ({analytics.tools_used_list.length})
            </h2>
            <div className="flex flex-wrap gap-2">
              {analytics.tools_used_list.map((tool) => (
                <span
                  key={tool}
                  className="bg-light-bg dark:bg-dark-bg-secondary border border-cyber-blue/30 dark:border-cyber-blue/50 text-cyber-blue px-3 py-1 rounded-full text-sm hover:bg-cyber-blue/10 dark:hover:bg-cyber-blue/20 transition-colors cursor-pointer"
                >
                  {tool}
                </span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({
  icon,
  label,
  value,
  color,
}: {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  color: 'aqua' | 'cyan' | 'gold' | 'green';
}) {
  const colorClasses = {
    aqua: 'bg-cyber-blue/20 dark:bg-cyber-blue/30 border-cyber-blue/50 dark:border-cyber-blue/70 text-cyber-blue',
    cyan: 'bg-cyber-cyan/20 dark:bg-cyber-cyan/30 border-cyber-cyan/50 dark:border-cyber-cyan/70 text-cyber-cyan',
    gold: 'bg-action-gold/20 dark:bg-action-gold/30 border-action-gold/50 dark:border-action-gold/70 text-action-gold',
    green: 'bg-green-500/20 dark:bg-green-500/30 border-green-500/50 dark:border-green-500/70 text-green-700 dark:text-green-400',
  };

  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3">
        <div className={`${colorClasses[color]} border p-3 rounded-lg`}>
          {icon}
        </div>
        <div>
          <p className="text-sm text-gray-600 dark:text-dark-text-secondary">{label}</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-dark-text">{value}</p>
        </div>
      </div>
    </div>
  );
}

function ToolShortcut({ tool }: { tool: ToolInfo }) {
  const navigate = useNavigate();

  return (
    <button
      onClick={() => navigate('/tools')}
      className="bg-light-bg-secondary dark:bg-dark-bg-secondary border border-light-border dark:border-dark-border rounded-lg p-3 hover:border-cyber-blue/50 dark:hover:border-cyber-blue/70 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover transition-all text-left group"
    >
      <div className="flex items-center justify-between mb-1">
        <span className="font-semibold text-gray-900 dark:text-dark-text text-sm group-hover:text-cyber-blue transition-colors">
          {tool.name}
        </span>
        {tool.installed && (
          <span className="w-2 h-2 bg-green-500 dark:bg-cyber-green rounded-full" />
        )}
      </div>
      <p className="text-xs text-gray-600 dark:text-dark-text-secondary line-clamp-2">{tool.description}</p>
      <span className="text-xs text-cyber-blue/70 dark:text-cyber-blue/80 mt-1 block">
        {tool.category}
      </span>
    </button>
  );
}


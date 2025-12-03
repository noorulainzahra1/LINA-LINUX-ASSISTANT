/**
 * Session Analytics Dashboard
 */
import { useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { ArrowLeft, BarChart3, Terminal, Clock, Zap } from 'lucide-react';
import { useSession } from '../contexts/SessionContext';
import { sessionAPI } from '../services/api';
import ThemeToggle from '../components/ThemeToggle';

export default function Analytics() {
  const navigate = useNavigate();
  const { session } = useSession();

  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics', session?.session_id],
    queryFn: () => sessionAPI.getAnalytics(session?.session_id || ''),
    enabled: !!session?.session_id,
  });

  if (!session) {
    navigate('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-light dark:bg-gradient-dark custom-scrollbar">
      {/* Header */}
      <header className="bg-gradient-card dark:bg-gradient-card-dark border-b-2 border-light-border-accent dark:border-dark-border-accent px-6 py-4 shadow-card">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={() => navigate('/chat')}
              className="p-2 hover:bg-light-bg-hover dark:hover:bg-dark-bg-hover rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5 text-cyber-blue" />
            </button>
            <div className="flex items-center space-x-3">
              <BarChart3 className="w-6 h-6 text-cyber-blue" />
              <h1 className="text-xl font-bold text-gray-900 dark:text-dark-text">Session Analytics</h1>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <div className="max-w-6xl mx-auto p-6 space-y-6">
        {isLoading ? (
          <div className="flex items-center justify-center p-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-cyber-blue"></div>
          </div>
        ) : analytics ? (
          <>
            {/* Overview Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <StatCard
                icon={<Terminal className="w-6 h-6" />}
                label="Commands Executed"
                value={analytics.commands_executed}
                color="bg-blue-500"
              />
              <StatCard
                icon={<Zap className="w-6 h-6" />}
                label="Tools Used"
                value={analytics.unique_tools_used}
                color="bg-green-500"
              />
              <StatCard
                icon={<Clock className="w-6 h-6" />}
                label="Session Duration"
                value={`${Math.round(analytics.duration_minutes)} min`}
                color="bg-cyan-500"
              />
              <StatCard
                icon={<BarChart3 className="w-6 h-6" />}
                label="Plans Generated"
                value={analytics.plans_generated}
                color="bg-orange-500"
              />
            </div>

            {/* Tools Used List */}
            <div className="cyber-card">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text mb-4">
                Tools Used ({analytics.tools_used_list.length})
              </h2>
              <div className="flex flex-wrap gap-2">
                {analytics.tools_used_list.length > 0 ? (
                  analytics.tools_used_list.map((tool) => (
                    <span
                      key={tool}
                      className="bg-light-bg dark:bg-dark-bg-secondary border border-cyber-blue/30 dark:border-cyber-blue/50 text-cyber-blue px-3 py-1 rounded-full text-sm"
                    >
                      {tool}
                    </span>
                  ))
                ) : (
                  <p className="text-gray-600 dark:text-dark-text-secondary">No tools used yet</p>
                )}
              </div>
            </div>

            {/* Additional Stats */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="cyber-card">
                <h3 className="font-semibold text-gray-900 dark:text-dark-text mb-4">Conversations</h3>
                <p className="text-3xl font-bold text-cyber-blue">
                  {analytics.conversations}
                </p>
              </div>

              <div className="cyber-card">
                <h3 className="font-semibold text-gray-900 dark:text-dark-text mb-4">Explanations Requested</h3>
                <p className="text-3xl font-bold text-cyber-blue">
                  {analytics.explanations_requested}
                </p>
              </div>
            </div>

            {/* Learning Insights */}
            {analytics.learning_insights && (
              <div className="cyber-card">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-dark-text mb-4">
                  Learning Insights
                </h2>
                <pre className="bg-light-bg dark:bg-dark-bg-secondary border border-light-border dark:border-dark-border p-4 rounded-lg overflow-auto text-sm text-gray-700 dark:text-dark-text-secondary custom-scrollbar">
                  {JSON.stringify(analytics.learning_insights, null, 2)}
                </pre>
              </div>
            )}
          </>
        ) : (
          <div className="cyber-card p-12 text-center">
            <p className="text-gray-600 dark:text-dark-text-secondary">No analytics data available</p>
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
  color: string;
}) {
  const colorMap: Record<string, { bg: string; border: string; text: string }> = {
    'bg-blue-500': { bg: 'bg-blue-500/20 dark:bg-blue-500/30', border: 'border-blue-500/50 dark:border-blue-500/70', text: 'text-blue-500 dark:text-blue-400' },
    'bg-green-500': { bg: 'bg-green-500/20 dark:bg-green-500/30', border: 'border-green-500/50 dark:border-green-500/70', text: 'text-green-500 dark:text-green-400' },
    'bg-cyan-500': { bg: 'bg-cyan-500/20 dark:bg-cyan-500/30', border: 'border-cyan-500/50 dark:border-cyan-500/70', text: 'text-cyan-500 dark:text-cyan-400' },
    'bg-orange-500': { bg: 'bg-orange-500/20 dark:bg-orange-500/30', border: 'border-orange-500/50 dark:border-orange-500/70', text: 'text-orange-500 dark:text-orange-400' },
  };
  
  const colors = colorMap[color] || colorMap['bg-blue-500'];
  
  return (
    <div className="cyber-card">
      <div className="flex items-center space-x-3">
        <div className={`${colors.bg} border ${colors.border} ${colors.text} p-3 rounded-lg`}>
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


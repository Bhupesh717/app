import { useState, useEffect } from 'react';
import axios from 'axios';
import { Bell, Clock, Send, Settings, CheckCircle, XCircle, Calendar } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { toast } from 'sonner';
import { Toaster } from '@/components/ui/sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [logs, setLogs] = useState([]);
  const [scheduleSettings, setScheduleSettings] = useState(null);
  const [scheduleStatus, setScheduleStatus] = useState(null);
  const [loading, setLoading] = useState(false);
  const [editMode, setEditMode] = useState(false);
  const [tempScheduleTime, setTempScheduleTime] = useState('');

  useEffect(() => {
    fetchData();
    // Refresh data every 30 seconds
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [logsRes, settingsRes, statusRes] = await Promise.all([
        axios.get(`${API}/notifications/logs`),
        axios.get(`${API}/schedule/settings`),
        axios.get(`${API}/schedule/status`)
      ]);
      
      setLogs(logsRes.data);
      setScheduleSettings(settingsRes.data);
      setScheduleStatus(statusRes.data);
      setTempScheduleTime(settingsRes.data.schedule_time);
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Failed to load data');
    }
  };

  const handleManualTrigger = async () => {
    setLoading(true);
    try {
      await axios.post(`${API}/notifications/trigger`);
      toast.success('Notification sent successfully!');
      // Wait a bit then refresh logs
      setTimeout(fetchData, 1000);
    } catch (error) {
      console.error('Error triggering notification:', error);
      toast.error('Failed to send notification');
    } finally {
      setLoading(false);
    }
  };

  const handleScheduleToggle = async (enabled) => {
    try {
      await axios.put(`${API}/schedule/settings`, { enabled });
      toast.success(enabled ? 'Schedule enabled' : 'Schedule disabled');
      fetchData();
    } catch (error) {
      console.error('Error updating schedule:', error);
      toast.error('Failed to update schedule');
    }
  };

  const handleScheduleTimeUpdate = async () => {
    try {
      await axios.put(`${API}/schedule/settings`, { 
        schedule_time: tempScheduleTime 
      });
      toast.success('Schedule time updated');
      setEditMode(false);
      fetchData();
    } catch (error) {
      console.error('Error updating schedule time:', error);
      toast.error('Failed to update schedule time');
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 lg:p-8">
      <Toaster position="top-right" richColors />
      
      {/* Header */}
      <div className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="p-3 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 shadow-lg">
            <Bell className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-4xl sm:text-5xl font-bold text-gray-800">Push Notification Dashboard</h1>
            <p className="text-base text-gray-600 mt-1">WordPress to OneSignal automation for ccodelearner.com</p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto space-y-6">
        {/* Control Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Manual Trigger Card */}
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-t-lg">
              <CardTitle className="flex items-center gap-2">
                <Send className="w-5 h-5 text-blue-600" />
                Manual Trigger
              </CardTitle>
              <CardDescription>Send a notification immediately</CardDescription>
            </CardHeader>
            <CardContent className="pt-6">
              <Button 
                data-testid="manual-trigger-btn"
                onClick={handleManualTrigger} 
                disabled={loading}
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-medium py-6 rounded-xl shadow-md hover:shadow-lg transition-all duration-300"
              >
                {loading ? 'Sending...' : 'Send Notification Now'}
              </Button>
            </CardContent>
          </Card>

          {/* Schedule Settings Card */}
          <Card className="border-0 shadow-lg hover:shadow-xl transition-shadow duration-300">
            <CardHeader className="bg-gradient-to-r from-indigo-50 to-purple-50 rounded-t-lg">
              <CardTitle className="flex items-center gap-2">
                <Settings className="w-5 h-5 text-indigo-600" />
                Schedule Settings
              </CardTitle>
              <CardDescription>Configure automated notifications</CardDescription>
            </CardHeader>
            <CardContent className="pt-6 space-y-4">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-xl">
                <div className="flex items-center gap-2">
                  <Clock className="w-5 h-5 text-gray-600" />
                  <Label className="text-base font-medium">Enable Schedule</Label>
                </div>
                <Switch
                  data-testid="schedule-toggle"
                  checked={scheduleSettings?.enabled || false}
                  onCheckedChange={handleScheduleToggle}
                />
              </div>

              {scheduleSettings && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="schedule-time" className="text-base font-medium">Daily Time (UTC)</Label>
                    {!editMode && (
                      <Button 
                        variant="ghost" 
                        size="sm"
                        onClick={() => setEditMode(true)}
                        className="text-sm text-blue-600 hover:text-blue-700"
                      >
                        Edit
                      </Button>
                    )}
                  </div>
                  
                  {editMode ? (
                    <div className="flex gap-2">
                      <Input
                        data-testid="schedule-time-input"
                        id="schedule-time"
                        type="time"
                        value={tempScheduleTime}
                        onChange={(e) => setTempScheduleTime(e.target.value)}
                        className="flex-1 h-12 rounded-xl border-2 focus:border-blue-500"
                      />
                      <Button 
                        data-testid="save-schedule-btn"
                        onClick={handleScheduleTimeUpdate}
                        className="bg-blue-600 hover:bg-blue-700 rounded-xl px-6"
                      >
                        Save
                      </Button>
                      <Button 
                        variant="outline"
                        onClick={() => {
                          setEditMode(false);
                          setTempScheduleTime(scheduleSettings.schedule_time);
                        }}
                        className="rounded-xl"
                      >
                        Cancel
                      </Button>
                    </div>
                  ) : (
                    <div className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl">
                      <p className="text-2xl font-bold text-blue-600">{scheduleSettings.schedule_time}</p>
                    </div>
                  )}
                </div>
              )}

              {scheduleStatus?.next_run && scheduleSettings?.enabled && (
                <div className="flex items-center gap-2 p-4 bg-green-50 rounded-xl border border-green-200">
                  <Calendar className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="text-sm font-medium text-green-800">Next scheduled run:</p>
                    <p className="text-sm text-green-600">{formatDate(scheduleStatus.next_run)}</p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Notification History */}
        <Card className="border-0 shadow-lg">
          <CardHeader className="bg-gradient-to-r from-gray-50 to-slate-50 rounded-t-lg">
            <CardTitle className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-gray-700" />
              Notification History
            </CardTitle>
            <CardDescription>Recent notifications sent to subscribers</CardDescription>
          </CardHeader>
          <CardContent className="pt-6">
            {logs.length === 0 ? (
              <div className="text-center py-12">
                <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500 text-lg">No notifications sent yet</p>
                <p className="text-gray-400 text-sm mt-2">Click the manual trigger button to send your first notification</p>
              </div>
            ) : (
              <div className="space-y-4" data-testid="notification-logs">
                {logs.map((log) => (
                  <div
                    key={log.id}
                    data-testid={`notification-log-${log.id}`}
                    className="p-5 rounded-xl border-2 hover:border-blue-200 transition-all duration-300 bg-white hover:shadow-md"
                  >
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          {log.status === 'success' ? (
                            <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0" />
                          ) : (
                            <XCircle className="w-5 h-5 text-red-500 flex-shrink-0" />
                          )}
                          <h3 className="font-semibold text-gray-800 truncate" title={log.post_title}>
                            {log.post_title}
                          </h3>
                        </div>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2" dangerouslySetInnerHTML={{ __html: log.post_excerpt }} />
                        <div className="flex flex-wrap items-center gap-3 text-xs text-gray-500">
                          <span className="flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {formatDate(log.sent_at)}
                          </span>
                          {log.recipient_count !== null && (
                            <span className="px-2 py-1 bg-blue-50 text-blue-600 rounded-full font-medium">
                              {log.recipient_count} recipients
                            </span>
                          )}
                          <span className={`px-2 py-1 rounded-full font-medium ${
                            log.status === 'success' 
                              ? 'bg-green-50 text-green-600' 
                              : 'bg-red-50 text-red-600'
                          }`}>
                            {log.status}
                          </span>
                        </div>
                        {log.error_message && (
                          <p className="text-xs text-red-500 mt-2 p-2 bg-red-50 rounded">
                            Error: {log.error_message}
                          </p>
                        )}
                      </div>
                      <a
                        href={log.post_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:text-blue-700 text-sm font-medium whitespace-nowrap flex-shrink-0 hover:underline"
                      >
                        View Post →
                      </a>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;
import React from 'react';
import { Outlet, Link, useNavigate } from 'react-router-dom';
import { Satellite, Upload, User, LayoutDashboard, History, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error("Logout API failed", error);
    } finally {
      logout();
      navigate('/login');
    }
  };

  return (
    <div className="flex h-screen bg-slate-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <Satellite className="h-6 w-6 text-blue-600 mr-2" />
          <span className="font-bold text-lg tracking-tight">AstraGeo</span>
        </div>
        <nav className="flex-1 py-4">
          <ul className="space-y-1 px-3">
            <li>
              <Link to="/dashboard" className="flex items-center px-3 py-2 text-slate-700 rounded-md hover:bg-slate-100">
                <LayoutDashboard className="h-5 w-5 mr-3 text-slate-400" />
                Dashboard
              </Link>
            </li>
            <li>
              <Link to="/upload" className="flex items-center px-3 py-2 text-slate-700 rounded-md hover:bg-slate-100">
                <Upload className="h-5 w-5 mr-3 text-slate-400" />
                New Analysis
              </Link>
            </li>
            <li>
              <Link to="/analyses" className="flex items-center px-3 py-2 text-slate-700 rounded-md hover:bg-slate-100">
                <History className="h-5 w-5 mr-3 text-slate-400" />
                Analysis History
              </Link>
            </li>
          </ul>
        </nav>
        <div className="p-4 border-t border-slate-200">
          <Link to="/profile" className="flex items-center text-slate-700 hover:text-slate-900 mb-4">
            <User className="h-5 w-5 mr-2" />
            <span className="truncate">{user?.full_name || user?.email || 'Profile'}</span>
          </Link>
          <button 
            onClick={handleLogout}
            className="flex items-center text-red-600 hover:text-red-700 w-full text-left"
          >
            <LogOut className="h-5 w-5 mr-2" />
            <span>Logout</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto">
        <header className="h-16 bg-white border-b border-slate-200 flex items-center justify-end px-6 space-x-4">
          <span className="text-sm font-medium text-slate-700">Welcome, {user?.full_name || user?.email}</span>
          <span className="text-sm text-slate-500 border-l pl-4 border-slate-200">System Status: <span className="text-green-500 font-medium">Online</span></span>
        </header>
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

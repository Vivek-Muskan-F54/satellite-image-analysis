import React from 'react';
import { Outlet, Link, useNavigate, useLocation } from 'react-router-dom';
import { Satellite, Upload, LayoutDashboard, History, LogOut } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../services/api';

export const AppLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

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

  const NavLink = ({ to, icon: Icon, children }: { to: string, icon: any, children: React.ReactNode }) => {
    const isActive = location.pathname.startsWith(to);
    return (
      <Link
        to={to}
        className={`flex items-center px-3 py-2.5 rounded-lg transition-all duration-200 group ${
          isActive
            ? 'bg-blue-600/10 text-blue-600 font-medium'
            : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
        }`}
      >
        <Icon className={`h-5 w-5 mr-3 transition-colors ${isActive ? 'text-blue-600' : 'text-slate-400 group-hover:text-slate-600'}`} />
        {children}
      </Link>
    );
  };

  return (
    <div className="flex h-screen bg-slate-50 font-sans selection:bg-blue-100 selection:text-blue-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-slate-200 flex flex-col shadow-sm z-10">
        <div className="h-16 flex items-center px-6 border-b border-slate-100">
          <Satellite className="h-6 w-6 text-blue-600 mr-2.5" />
          <span className="font-bold text-xl text-slate-900 tracking-tight">AstraGeo</span>
        </div>

        <nav className="flex-1 py-6 px-3">
          <div className="mb-2 px-3 text-xs font-semibold text-slate-400 uppercase tracking-wider">
            Menu
          </div>
          <ul className="space-y-1.5">
            <li><NavLink to="/dashboard" icon={LayoutDashboard}>Dashboard</NavLink></li>
            <li><NavLink to="/upload" icon={Upload}>New Analysis</NavLink></li>
            <li><NavLink to="/analyses" icon={History}>Analysis History</NavLink></li>
          </ul>
        </nav>

        <div className="p-4 border-t border-slate-100 bg-slate-50/50">
          <div className="flex items-center px-3 py-2 mb-2 rounded-lg bg-white border border-slate-200 shadow-sm">
            <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold mr-3 flex-shrink-0">
              {user?.full_name?.charAt(0).toUpperCase() || user?.email?.charAt(0).toUpperCase() || 'U'}
            </div>
            <div className="overflow-hidden">
              <p className="text-sm font-medium text-slate-900 truncate">
                {user?.full_name || 'User'}
              </p>
              <p className="text-xs text-slate-500 truncate">{user?.email}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center px-3 py-2 text-sm text-slate-600 hover:text-red-600 hover:bg-red-50 rounded-lg w-full transition-colors"
          >
            <LogOut className="h-4 w-4 mr-3" />
            <span>Sign out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden relative">
        <header className="h-16 bg-white/80 backdrop-blur-md border-b border-slate-200 flex items-center justify-between px-8 sticky top-0 z-20">
          <div className="text-sm font-medium text-slate-700">
            {/* Contextual header content could go here */}
          </div>
          <div className="flex items-center space-x-6">
            <div className="flex items-center text-sm">
              <span className="relative flex h-2.5 w-2.5 mr-2">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
              </span>
              <span className="text-slate-600 font-medium">System Online</span>
            </div>
          </div>
        </header>
        <div className="flex-1 overflow-y-auto p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
};

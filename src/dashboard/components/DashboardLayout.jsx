import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Users, FileText, Mail, Bell, Settings } from 'lucide-react';

const Sidebar = () => (
  <div className="w-64 bg-gray-800 min-h-screen p-4">
    <div className="text-white text-xl font-bold mb-8">
      Claude MCP Toolkit
    </div>
    <nav>
      <SidebarLink to="/" icon={<Home size={20} />} text="Dashboard" />
      <SidebarLink to="/clients" icon={<Users size={20} />} text="Clientes" />
      <SidebarLink to="/proposals" icon={<FileText size={20} />} text="Propostas" />
      <SidebarLink to="/emails" icon={<Mail size={20} />} text="Emails" />
      <SidebarLink to="/notifications" icon={<Bell size={20} />} text="Notificações" />
      <SidebarLink to="/settings" icon={<Settings size={20} />} text="Configurações" />
    </nav>
  </div>
);

const SidebarLink = ({ to, icon, text }) => (
  <Link
    to={to}
    className="flex items-center text-gray-300 hover:text-white hover:bg-gray-700 px-4 py-2 rounded mb-2"
  >
    {icon}
    <span className="ml-3">{text}</span>
  </Link>
);

const Header = () => (
  <header className="bg-white shadow">
    <div className="max-w-7xl mx-auto py-4 px-4 sm:px-6 lg:px-8">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <div className="flex items-center">
          <button className="relative p-2">
            <Bell className="h-6 w-6 text-gray-600" />
            <span className="absolute top-0 right-0 h-4 w-4 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
              3
            </span>
          </button>
          <div className="ml-4 flex items-center">
            <img
              className="h-8 w-8 rounded-full"
              src="/api/placeholder/32/32"
              alt="User"
            />
            <span className="ml-2 text-gray-700">Admin</span>
          </div>
        </div>
      </div>
    </div>
  </header>
);

const DashboardLayout = ({ children }) => {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1">
        <Header />
        <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
          {children}
        </main>
      </div>
    </div>
  );
};

export default DashboardLayout;
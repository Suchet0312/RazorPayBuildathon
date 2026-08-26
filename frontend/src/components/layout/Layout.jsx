import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';

const Layout = () => {
  return (
    <div className="flex h-screen overflow-hidden bg-bg-dark text-gray-200">
      <Sidebar />
      <div className="flex-1 overflow-y-auto relative">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-[#0a0a0b] via-[#0a0a0b] to-[#0a0a0b] opacity-80 pointer-events-none z-[-1]" />
        <main className="p-8 max-w-7xl mx-auto min-h-full">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;

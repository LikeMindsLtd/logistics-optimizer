import { Outlet } from 'react-router-dom';
import Sidebar from './SideBar';

const MainLayout = () => {
  const sidebarWidth = '220px'; // same width used in your Sidebar component

  return (
    <div style={{ display: 'flex' }}>
      {/* Fixed Sidebar */}
      <div
        style={{
          width: sidebarWidth,
          position: 'fixed',
          top: 0,
          left: 0,
          height: '100vh',
          backgroundColor: '#1f2937', // Tailwind gray-800
          color: 'white',
        }}
      >
        <Sidebar />
      </div>

      {/* Main Content */}
      <main
        style={{
          flex: 1,
          padding: '20px',
          marginLeft: sidebarWidth, // ensures it doesn't overlap
          backgroundColor: '#f3f4f6', // Tailwind gray-100
          minHeight: '100vh',
        }}
      >
        <Outlet />
      </main>
    </div>
  );
};

export default MainLayout;

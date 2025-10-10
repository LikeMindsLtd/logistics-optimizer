import { NavLink } from 'react-router-dom';

const Sidebar = () => {
  const navItems = [
    { name: 'Dashboard', path: '/dashboard' },
    { name: 'Plants', path: '/plants' },
    { name: 'Trains', path: '/trains' },
    { name: 'Ports', path: '/ports' },
    { name: 'Vessels', path: '/vessels' },
    { name: 'Optimization', path: '/optimization' },
    { name: 'Data Management', path: '/data-management' },
  ];

  return (
    <nav style={{ width: '220px', backgroundColor: '#2c3e50', color: '#ecf0f1', padding: '20px' }}>
      <h2>Logistics Optimizer</h2>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {navItems.map((item) => (
          <li key={item.path} style={{ margin: '10px 0' }}>
            <NavLink
              to={item.path}
              style={({ isActive }) => ({
                color: isActive ? '#3498db' : '#ecf0f1',
                textDecoration: 'none',
                fontWeight: isActive ? 'bold' : 'normal',
              })}
            >
              {item.name}
            </NavLink>
          </li>
        ))}
      </ul>
    </nav>
  );
};

export default Sidebar;

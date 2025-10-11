import { NavLink, Link } from "react-router-dom";



const Sidebar = () => {
  const navItems = [
    { name: "Dashboard", path: "/dashboard" },
    { name: "Plants", path: "/plants" },
    { name: "Trains", path: "/trains" },
    { name: "Ports", path: "/ports" },
    { name: "Vessels", path: "/vessels" },
    { name: "Optimization", path: "/optimization" },
    { name: "Data Management", path: "/data-management" },
  ];

  return (
    <nav
      style={{
        width: "220px",
        backgroundColor: "#2c3e50",
        color: "#ecf0f1",
        padding: "20px",
        height: "100vh",
        position: "relative",
      }}
    >
      <h2 className="text-3xl font-bold mb-4">Logistics Optimizer</h2>
      <ul style={{ listStyle: "none", padding: 0 }}>
        {navItems.map((item) => (
          <li key={item.path} style={{ margin: "10px 0" }}>
            <NavLink
              to={item.path}
              style={({ isActive }) => ({
                color: isActive ? "#3498db" : "#ecf0f1",
                textDecoration: "none",
                fontWeight: isActive ? "bold" : "normal",
              })}
            >
              {item.name}
            </NavLink>
          </li>
        ))}
      </ul>
      <div style={{position: 'absolute', bottom: '20px'}}>
        <Link to="/logout" className="" style={{color:'red', textDecoration: 'none'}}>Logout</Link>
      </div>
    </nav>
  );
};

export default Sidebar;

// frontend/src/components/Navbar.jsx
import { Link, useNavigate } from "react-router-dom";

export default function Navbar() {
  const navigate = useNavigate();
  const token = localStorage.getItem("pixclad_token");

  const handleLogout = () => {
    localStorage.removeItem("pixclad_token");
    navigate("/login");
  };

  return (
    <nav className="bg-gray-900 text-white px-6 py-3 flex justify-between items-center shadow-lg">
      <Link to="/" className="text-2xl font-bold">Pixclad</Link>
      <div className="flex gap-4">
        {!token && (
          <>
            <Link to="/login" className="hover:text-gray-300">Login</Link>
            <Link to="/register" className="hover:text-gray-300">Register</Link>
            <Link to="/upload" className="hover:text-gray-300">Upload</Link>
          </>
        )}
        {token && (
          <>
            <Link to="/dashboard" className="hover:text-gray-300">Dashboard</Link>
            <Link to="/upload" className="hover:text-gray-300">Upload</Link>
            <button onClick={handleLogout} className="hover:text-gray-300">Logout</button>
          </>
        )}
      </div>
    </nav>
  );
}
